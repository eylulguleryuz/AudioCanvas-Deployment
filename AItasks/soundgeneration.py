import os
import random
import pandas as pd
from pydub import AudioSegment
import base64
import tempfile  
import numpy as np 
import math
import logging
from AItasks.models import LabeledSound, ThemeSound

logging.basicConfig(filename='sound_generation.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

os.environ["PATH"] += os.pathsep + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bin')

def filter_sound_clips(labels):
    """
    Filter sound clips based on the provided labels by searching for matching labels in the database.
    @param labels - List of labels to filter sound clips
    @return List of tuples containing sound file, label, and filename of matching sound clips
    """
    matching_clips = []
    try:
        for label in labels:
            matching_sounds = LabeledSound.objects.filter(label__icontains=label)
            for sound in matching_sounds:
                matching_clips.append((sound.sound_file, sound.label, sound.filename))
    except Exception as e:
        logging.error(f"Error occurred while filtering sound clips: {e}")
    return matching_clips

def retrieve_theme_clips():
    """
    Retrieve theme clips from the database and return a list of tuples containing sound file, label, and filename.
    @return A list of tuples containing sound file, label, and filename
    """
    theme_clips = []
    try:
        all_sounds = ThemeSound.objects.all()
        for sound in all_sounds:
            theme_clips.append((sound.sound_file, sound.label, sound.filename))
    except Exception as e:
        logging.error(f"Error occurred while retrieving theme clips: {e}")
    return theme_clips

def generate_sound(sound_clips, duration, labels, method):
    """
    Generate a sound clip by combining segments from a list of sound clips based on specified labels and duration.
    @param sound_clips - List of sound clips with their details.
    @param duration - Desired duration of the generated sound clip.
    @param labels - List of labels to be included in the generated sound clip.
    @param method - Method for generating the sound clip ("Creative" or "Plain").
    @return Tuple containing the generated sound clip, list of labels used in the clip, and list of labels not used.
    Raises:
    Exception: An error occurred while processing the sound clips.
    """
    selected_segments = []
    random.shuffle(sound_clips)
    used_labels = []
    unused_labels = []

    for label in labels:
        current_duration = 0
        label_sound = AudioSegment.silent()
        label_used = False
        for clip_details in sound_clips:
            sound_file, clip_label, filename = clip_details
            if label.lower() in clip_label.lower():
                try:                   
                    clip = AudioSegment.from_file(sound_file)
                    # Trim silence from the beginning and end of the clip
                    start_trim = detect_leading_silence(clip)
                    end_trim = detect_leading_silence(clip.reverse())
                    length = len(clip)    
                    clip = clip[start_trim:length-end_trim]
                    
                    if current_duration +  len(clip) > duration:
                        remaining_duration = duration*1000 - current_duration
                        if remaining_duration > 0:
                            clip = clip[:remaining_duration]
                        else:
                            break  # No remaining duration

                    label_sound += clip
                    current_duration += len(clip)
                    label_used = True
                except Exception as e:
                    logging.error(f"Error occurred while adding the sound: {sound_file}")
                    continue  
        selected_segments.append(label_sound)
        if label_used:
            used_labels.append(label)
        else:
            unused_labels.append(label)
    max_length = duration * 1000 
    overlapped_sound = AudioSegment.silent(duration=max_length)
    for segment in selected_segments:
        overlapped_sound = overlapped_sound.overlay(segment, position=0)
    overlapped_sound.fade_in(math.ceil(duration/10)) #needs an integer
    overlapped_sound.fade_out(math.ceil(duration/10))

    if(method=="Creative"):
        theme_clips = retrieve_theme_clips()
        try:
            selected_theme_clip = random.choice(theme_clips)
            theme_sound = AudioSegment.from_file(selected_theme_clip[0])

            start_trim = detect_leading_silence(theme_sound)
            end_trim = detect_leading_silence(theme_sound.reverse())
            length = len(theme_sound)    
            theme_sound = theme_sound[start_trim:length-end_trim]

            theme_sound = theme_sound[:max_length] 

            lowered_theme_sound = theme_sound - 8 #make it quieter
            creative_sound = overlapped_sound.overlay(lowered_theme_sound, position=0)
            creative_sound.fade_out(math.ceil(duration/10))
            return creative_sound, used_labels, unused_labels
        except Exception as e:
            logging.error(f"Error occurred while adding the theme sound: {selected_theme_clip[2]}")
        
    return overlapped_sound, used_labels, unused_labels



def detect_leading_silence(sound, silence_threshold=-40.0, chunk_size=5):
    """
    Detect the amount of leading silence in a sound file based on a given silence threshold and chunk size.
    @param sound - the input sound file
    @param silence_threshold - the threshold below which a chunk is considered silent (default is -40.0 dBFS)
    @param chunk_size - the size of each chunk in milliseconds (default is 5 ms)
    @return The duration of leading silence in milliseconds
    """
    trim_ms = 0 # ms

    assert chunk_size > 0 # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms


def generate(labels, duration, method):
    """
    Generate a sound clip based on the provided labels and duration using a specified method.
    @param labels - The labels for the sound clip generation.
    @param duration - The duration of the sound clip.
    @param method - The method used for generating the sound clip.
    @return encoded_sound_data - The base64 encoded sound data.
    @return used_labels - The labels used for generating the sound clip.
    @return unused_labels - The labels not used for generating the sound clip.
    """
    try:
        filtered_clips = filter_sound_clips(labels)
        if filtered_clips:
            generated_sound, used_labels, unused_labels = generate_sound(filtered_clips, duration, labels, method)
            if generated_sound:
                # Create a temporary file to save the sound
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                    temp_file_path = temp_file.name
                    generated_sound.export(temp_file_path, format="mp3")
                
                # Read the saved sound file and encode it to Base64
                with open(temp_file_path, "rb") as sound_file:
                    encoded_sound_data = base64.b64encode(sound_file.read()).decode('utf-8')
                
                # Clean up the temporary file
                os.remove(temp_file_path)
                return encoded_sound_data, used_labels, unused_labels
            else:
                return "No sound created", used_labels, unused_labels
        else:
            return "No clips found", [], labels
    except Exception as e:
        logging.error(f"Error occurred while generating sound: {e}")
        return "Error occurred while generating sound", [], []