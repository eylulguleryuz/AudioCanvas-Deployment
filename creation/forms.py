from django import forms
from creation.models import CreationInfo
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

def validate_image_size(image):
    max_size_mb = 10
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image file size must be less than {max_size_mb}MB.")

class ImageForm(forms.Form):
    image_file = forms.ImageField(
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png']),
            validate_image_size
        ]
    )

class KeywordForm(forms.Form):
    keywords = None

class CustomizationForm(forms.Form):
    CHOICES = [('Plain', 'Plain'), ('Creative', 'Creative')]
    creation_method = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Creation Method"
    )
    duration = forms.FloatField(
        min_value=2.5,
        max_value=30,
        widget=forms.NumberInput(attrs={'placeholder': 'X seconds'}),
        label='Duration',
        required=True
    )

class SoundForm(forms.Form):
    sound = None
