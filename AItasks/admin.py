from django.contrib import admin
from .models import LabeledSound, ThemeSound
from django.contrib import messages
class LabeledSoundAdmin(admin.ModelAdmin):
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    search_fields = ('label', 'filename')
    list_display = ('label', 'filename')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # obj is None when adding a new sound
            return []
        else:
            return []
            
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        unique_category_count = LabeledSound.objects.values('label').distinct().count()
        extra_context['unique_category_count'] = unique_category_count

        message = f"There are {unique_category_count} unique categories."
        self.message_user(request, message, level=messages.INFO)

        return super().changelist_view(request, extra_context=extra_context)
    
admin.site.register(LabeledSound, LabeledSoundAdmin)

class ThemeSoundAdmin(admin.ModelAdmin):
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    list_display = ('filename',  'label', 'sound_file')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # obj is None when adding a new sound
            return ['filename', 'sound_file']
        else:
            return []
admin.site.register(ThemeSound, ThemeSoundAdmin)


