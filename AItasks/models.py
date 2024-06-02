from django.db import models
from django.core.files.storage import FileSystemStorage
from pydub import AudioSegment
from django.core.exceptions import ValidationError
import os
from io import BytesIO
from django.core.files.storage import default_storage
from django.dispatch import receiver
from django.db.models.signals import post_delete
os.environ["PATH"] += os.pathsep + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bin')
MAX_FILE_SIZE = 30 * 1024 * 1024  # 30 MB in bytes
def sound_storage(instance, filename):
    """
    Store the sound file in the specified directory.
    @param instance - the sound instance to be stored
    @param filename - the name of the file
    @return The file path where the sound file is stored.
    """
    file_path = f'audio/clips/{instance.filename}'
    return file_path

def theme_storage(instance, filename):
    """
    Store the theme sound file in the 'audio/theme' directory with the filename provided.
    @param instance - the instance of the theme audio file
    @param filename - the name of the file
    @return The file path where the theme audio file is stored.
    """
    file_path = f'audio/theme/{instance.filename}'
    return file_path

class LabeledSound(models.Model):
    """
    A model representing a labeled sound file with validation for allowed file extensions and audio file content.
    @param models.Model - The base class for Django models.
    @attribute ALLOWED_EXTENSIONS - List of allowed file extensions for sound files.
    @attribute label - CharField for the label of the sound file.
    @attribute filename - CharField for the name of the sound file.
    @attribute sound_file - FileField for uploading the sound file.
    @method clean - Custom validation to ensure the filename has an allowed extension.
    @method save - Override the save method to validate the audio file content before saving.
    @method __str__ - String representation of the model, returns the filename.
    """
    ALLOWED_EXTENSIONS = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.wma', '.m4a']

    label = models.CharField(max_length=100)
    filename = models.CharField(max_length=100, unique=True)
    sound_file = models.FileField(upload_to=sound_storage)

    def clean(self):
        super().clean()
        if not any(self.filename.lower().endswith(ext) for ext in self.ALLOWED_EXTENSIONS):
            raise ValidationError({'filename': f'Filename must end with one of the following extensions: {", ".join(self.ALLOWED_EXTENSIONS)}'})

    def save(self, *args, **kwargs):
        file = self.sound_file
        if file:
            if file.size > MAX_FILE_SIZE:
                raise ValidationError({'sound_file': f'File size must be under {MAX_FILE_SIZE / (1024 * 1024)} MB'})
            file.seek(0)
            file_content = file.read()
            file.seek(0)

            try:
                audio_segment = AudioSegment.from_file(BytesIO(file_content))
            except Exception as e:
                raise ValidationError({'sound_file': f'Invalid audio file: {e}'})

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.filename)

class ThemeSound(models.Model):
    """
    A model representing a theme sound with validation for allowed file extensions and audio file content.
    - `label`: A character field for the label of the theme sound.
    - `filename`: A character field for the filename of the theme sound (unique).
    - `sound_file`: A file field for uploading the theme sound file.
    """
    ALLOWED_EXTENSIONS = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.wma', '.m4a']

    label                 = models.CharField(max_length=100)
    filename              = models.CharField(max_length=100, unique=True)
    sound_file            = models.FileField(upload_to=theme_storage)

    def __str__(self):
        return str(self.filename)

    def clean(self):
        super().clean()
        if not any(self.filename.lower().endswith(ext) for ext in self.ALLOWED_EXTENSIONS):
            raise ValidationError({'filename': f'Filename must end with one of the following extensions: {", ".join(self.ALLOWED_EXTENSIONS)}'})

    def save(self, *args, **kwargs):
        file = self.sound_file
        if file:
            if file.size > MAX_FILE_SIZE:
                raise ValidationError({'sound_file': f'File size must be under {MAX_FILE_SIZE / (1024 * 1024)} MB'})
            file.seek(0)
            file_content = file.read()
            file.seek(0)

            try:
                audio_segment = AudioSegment.from_file(BytesIO(file_content))
            except Exception as e:
                raise ValidationError({'sound_file': f'Invalid audio file: {e}'})

        self.full_clean()
        super().save(*args, **kwargs)

@receiver(post_delete, sender=ThemeSound)
def themesound_delete(sender, instance, **kwargs):
    """
    Define a signal receiver function that deletes the associated sound file when a ThemeSound instance is deleted.
    @param sender - The sender of the signal (ThemeSound model).
    @param instance - The instance of the ThemeSound model being deleted.
    """
    instance.sound_file.delete(False) 

@receiver(post_delete, sender=LabeledSound)
def labeledsound_delete(sender, instance, **kwargs):
    """
    Define a signal receiver function that deletes the associated sound file when a LabeledSound instance is deleted.
    @param sender - The sender of the signal (LabeledSound model).
    @param instance - The instance of the LabeledSound model being deleted.
    """
    instance.sound_file.delete(False) 

