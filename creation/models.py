from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.core.validators import MinValueValidator, MaxValueValidator
from account.models import Account
from django.contrib.postgres.fields import ArrayField
import base64
from pydub import AudioSegment
import os
import io
from django.core.files.base import ContentFile

os.environ["PATH"] += os.pathsep + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bin')

def upload_location_images(instance, filename):
    """
    Generate the file path for uploading location images based on the account ID and filename.
    @param instance - The instance of the location image
    @param filename - The name of the file being uploaded
    @return The file path for storing the image
    """
    file_path = '{account_id}/images/{filename}'.format(
        account_id=str(instance.account.id),  filename=filename
    )
    return file_path

def upload_location_sounds(instance, filename):
    """
    Generate the file path for uploading location sounds based on the account ID and filename.
    @param instance - The instance of the location sound
    @param filename - The name of the file being uploaded
    @return The file path for storing the sound clip
    """
    file_path = '{account_id}/sound_clips/{filename}'.format(
        account_id=str(instance.account.id),  filename=filename
    )
    return file_path

class CreationInfo(models.Model):
    """
    A model class representing Creation Information with various fields like created date, account, starred, image file, sound file, duration, creation method, and rating.
    - created_date: Date and time when the creation information was added.
    - account: User account associated with the creation.
    - starred: Boolean field indicating if the creation is starred.
    - image_file: Image file associated with the creation.
    - sound_file: Sound file associated with the creation.
    - CREATION_METHOD_CHOICES: Choices for the method of creation (Plain or Creative).
    - duration: Duration of the creation (validated between 2.5 and 30).
    - creation_method: Method used for creating the content.
    - rating: Rating of the creation (validated between 0 and 5)
    """
    created_date            = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    account                 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    starred                 = models.BooleanField(default=False)
    image_file              = models.ImageField(null=False, blank=False, upload_to=upload_location_images)
    sound_file              = models.FileField(upload_to=upload_location_sounds)
    CREATION_METHOD_CHOICES = [('Plain', 'Plain'), ('Creative', 'Creative')]

    duration                = models.FloatField(validators=[MinValueValidator(2.5), MaxValueValidator(30)])
    creation_method         = models.CharField(max_length=50, choices=CREATION_METHOD_CHOICES)
    rating                  = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True)

    def __str__(self):
            return str(self.id)

    def save_sound_with_customizations(self, sound, duration, creation_method):
        self.duration = duration
        self.creation_method = creation_method
        # Convert AudioSegment to mp3 
        with io.BytesIO() as buffer:
            sound.export(buffer, format='mp3')
            buffer.seek(0)
            # Save the converted audio data to the FileField
            self.sound_file.save("sound.mp3", ContentFile(buffer.read()))

    def save_rating(self, rating):
        self.rating = rating


class Keyword(models.Model):
    """
    A class representing a keyword associated with a creation.
    Attributes:
    - creation: ForeignKey to CreationInfo model, on_delete CASCADE
    - keyword: CharField with max length 100
    """
    creation                = models.ForeignKey(CreationInfo, on_delete=models.CASCADE)
    keyword                 = models.CharField(max_length=100)

    def __str__(self):
        return str(self.keyword)

class KeywordSummary(Keyword):
    """
    Create a proxy model for the Keyword model to display a summary of the most popular keywords.
    This class does not create a new table in the database but provides a different interface for querying the existing Keyword model.
    @param KeywordSummary - The proxy model for the Keyword model.
    @param Meta - Inner class for metadata configuration.
        @param proxy - Set to True to indicate that this is a proxy model.
        @param verbose_name - The human-readable name for the model in the admin interface.
        @param verbose_name_plural - The plural name for the model in the admin interface.
    """
    class Meta:
        proxy = True
        verbose_name = 'Most Popular Keywords'
        verbose_name_plural = 'Most Popular Keyword Stats'

class RatingSummary(CreationInfo):
    """
    Create a proxy model for the RatingSummary class that inherits from CreationInfo.
    This proxy model does not create a new database table.
    It provides metadata such as verbose_name and verbose_name_plural for the model.
    """
    class Meta:
        proxy = True
        verbose_name = 'Rating Summary'
        verbose_name_plural = 'Rating Summaries'

@receiver(post_delete, sender=CreationInfo)
def creation_delete(sender, instance, **kwargs):    
    """
    Define a signal receiver function that listens for the `post_delete` signal of the `CreationInfo` model. Upon deletion of an instance, this function deletes the associated sound and image files.
    @param sender - The sender of the signal
    @param instance - The instance being deleted
    @param kwargs - Additional keyword arguments
    """
    instance.sound_file.delete(False) 
    instance.image_file.delete(False) 

