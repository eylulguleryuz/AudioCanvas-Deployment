from django.test import TestCase, RequestFactory
from unittest.mock import Mock
from creation.views import keyword_search
from unittest.mock import patch 
import itertools

class KeywordSearchTestCase(TestCase):
    def setUp(self):
        # Set up the request factory
        self.factory = RequestFactory()

    def test_keyword_search_matching_labels(self):
        # Create a mock request with a search text that matches labels
        request = self.factory.get('/search/', {'search': 'label1'})
        
        # Mock LabeledSound.objects.values_list method to return some mock labels
        mock_labels = ['Label1, Label2', 'Label3']
        with patch('AItasks.models.LabeledSound.objects.values_list') as mock_values_list:
            mock_values_list.return_value = mock_labels

            # Call the view function
            response = keyword_search(request)

        # Check if the response contains the expected results
        self.assertContains(response, 'Label1')

    def test_keyword_search_no_matching_labels(self):
        # Create a mock request with a search text that doesn't match any labels
        request = self.factory.get('/search/', {'search': 'nonexistent'})

        # Mock LabeledSound.objects.values_list method to return some mock labels
        mock_labels = ['Label1, Label2', 'Label3']
        with patch('AItasks.models.LabeledSound.objects.values_list') as mock_values_list:
            mock_values_list.return_value = mock_labels

            # Call the view function
            response = keyword_search(request)

        # Check if the response does not contain any results
        self.assertNotContains(response, 'Label')

    def test_keyword_search_no_labels(self):
        # Create a mock request with a search text
        request = self.factory.get('/search/', {'search': 'label1'})

        # Mock LabeledSound.objects.values_list method to return an empty list
        with patch('AItasks.models.LabeledSound.objects.values_list') as mock_values_list:
            mock_values_list.return_value = []

            # Call the view function
            response = keyword_search(request)

        # Check if the response does not contain any results
        self.assertNotContains(response, 'Label')
from django.test import TestCase, RequestFactory
from account.models import Account
from creation.views import CreationWizardView
from creation.models import CreationInfo, Keyword
from creation.forms import ImageForm, KeywordForm, CustomizationForm, SoundForm
from django.core.files.uploadedfile import SimpleUploadedFile
import base64
from unittest.mock import patch
from AItasks.soundgeneration import generate
import time
import random
def test_sound_generation():
    # Define keywords and methods
    keywords_list = [
        "Umbrella", "Dog", "Toilet", "Frog", "Beetle",
        "Cat", "water_drops", "Tin can", "Car", "Sheep", 
        "Clapping", "Laughing"
    ]
    methods = ["Plain", "Creative"]

    # Open log file in write mode
    with open("generation_log3.csv", "w") as file:
        # Header for the log file
        file.write("Keywords,Method,Duration (seconds),Average Duration\n")

        # Manual combinations of 1, 2, 5, and 10 keywords
        combinations = {
            
            30: [["Umbrella", "Dog", "Toilet", "Frog", "glass_breaking", "Cat", "water_drops", "Tin can", "Car", "Sheep", 
            "hand_saw", "cow", "airplane", "hen", "washing_machine", "snoring", "footsteps", "engine", "mouse_click", "breathing",
            "toothbrush", "chirping_birds", "church_bells", "clapping", "laughing", "wind", "thunderstorm", "rooster","sea_waves","pig"]]

        }

        # Test each combination
        for num_keywords, keyword_combinations in combinations.items():
            for keywords in keyword_combinations:
                for method in methods:
                        total_duration = 0
                        for _ in range(10):  # Run each combination 10 times
                            start_time = time.time()
                            generate(keywords, 30, method)  # Fixed duration of 30 seconds
                            end_time = time.time()
                            total_duration += end_time - start_time


                        # Calculate average duration
                        average_duration = total_duration / 10
                        file.write(f"{keywords},{method},30,{average_duration}\n")
                    