from django.http import HttpResponse
from django.shortcuts import render,redirect
from formtools.wizard.views import SessionWizardView
from creation.forms import CustomizationForm, ImageForm, KeywordForm, SoundForm
from AItasks.models import LabeledSound
from django.core.files.storage import FileSystemStorage
from creation.models import CreationInfo, Keyword
from AItasks.imageprocessing import extract_keywords_from_image
from AItasks.soundgeneration import generate
from django.conf import settings
import base64
from django.views.decorators.csrf import csrf_exempt
from pydub import AudioSegment
import io
import os
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages

os.environ["PATH"] += os.pathsep + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bin')

class CreationWizardView(SessionWizardView):
    form_list = [
        ImageForm, 
        KeywordForm, 
        CustomizationForm,
         SoundForm
   ]
    template_name = "wizard.html"
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp'))
    extracted_keywords = {}

    def done(self, form_list, **kwargs):
        user = self.request.user
        creation_info = CreationInfo(account=user)
        image_file = form_list[0].cleaned_data['image_file']
        creation_info.image_file = image_file
    
        decoded_audio = base64.b64decode(self.request.session.get('sound'))
        sound = AudioSegment.from_file(io.BytesIO(decoded_audio))

        duration = self.get_cleaned_data_for_step('2')['duration']
        creation_method = self.get_cleaned_data_for_step('2')['creation_method']
    
        creation_info.save_sound_with_customizations(sound, duration, creation_method)
        
        creation_info.save()
        keywords = self.request.session.get('keywords', []) 
        for word in keywords:
            keyword = Keyword(keyword=word, creation=creation_info)
            keyword.save()

        # Prompt user for rating
        return render(self.request, 'rating/rating_prompt.html', {'creation_info': creation_info})

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        creation_infos = CreationInfo.objects.filter(account=self.request.user).order_by('-created_date')
        context['creation_infos'] = creation_infos

        if self.steps.current == '1':
            stored_image = self.get_cleaned_data_for_step('0')['image_file']
            if stored_image:
                keywords = extract_keywords_from_image(stored_image)
                if keywords:
                    context['keywords'] = keywords
                self.request.session['keywords'] = keywords
                

        if self.steps.current == '3':
            keywords = self.request.session.get('keywords')
            duration = self.get_cleaned_data_for_step('2')['duration']
            creation_method = self.get_cleaned_data_for_step('2')['creation_method']
            if keywords:
                sound, used_labels, unused_labels = generate(keywords, duration, creation_method)
                try:
                    audio_segment = AudioSegment.from_file(io.BytesIO(base64.b64decode(sound)))
                    if audio_segment:
                            # Save sound data to session
                        self.request.session['sound'] = sound
                            # Pass sound data to the context
                        context['sound_data'] = sound
                except Exception:
                    context['error_message'] = "No clips found, please start over and try adding keywords or uploading another picture."
                context['used_labels'] = used_labels
                context['unused_labels'] = unused_labels
            
        return context

def keyword_search(request):
    search_text = request.GET.get('search')
    results = []
    # Get queryset with distinct labels
    label_query = LabeledSound.objects.values_list('label', flat=True)
    if hasattr(label_query, 'distinct'):  # Check if distinct method is available
        label_query = label_query.distinct()
    else:
        label_query = set(label_query)  # Convert list to set to remove duplicates
    
    # Filter labels that match the search text
    for label in label_query:
        split_labels = [split_label.strip() for split_label in label.split(',')]
        for split_label in split_labels:
            if split_label.lower().startswith(search_text.lower()):
                results.append(split_label.capitalize())

    return render(request, 'search/search_results.html', {'results': results})
    
def add_keywords(request):
    keyword = request.GET.get('keyword')
    existing_keywords = request.session.get('keywords', {})
    existing_keywords[keyword] = existing_keywords.get(keyword, 0) + 1
    request.session['keywords'] = existing_keywords
    return render(request, 'keyword_list.html', {'keywords': existing_keywords})

def delete_keywords(request):
    keyword = request.GET.get('keyword')
    existing_keywords = request.session.get('keywords', {})
    if keyword in existing_keywords:
        if existing_keywords[keyword] > 1:
            existing_keywords[keyword] -= 1
        else:
            del existing_keywords[keyword]
        request.session['keywords'] = existing_keywords 
    return render(request, 'keyword_list.html', {'keywords': existing_keywords})
     
def save_rating(request):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        creation_info_id = request.POST.get('creation_info_id')  # Retrieve creation_info ID from POST data
        if creation_info_id:
            creation_info = get_object_or_404(CreationInfo, id=creation_info_id)
            creation_info.save_rating(rating)
            creation_info.save()

            response_message = f'Feedback saved successfully for creation_info_id: {creation_info_id}'

            return JsonResponse({'message': response_message})
        else:
            return JsonResponse({'error': 'creation_info_id not provided'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


