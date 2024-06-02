from django.contrib import admin
from django.contrib.admin import ModelAdmin
from creation.models import CreationInfo, Keyword, KeywordSummary, RatingSummary
from django.db.models import Count
from collections import defaultdict


class CreationAdmin(admin.ModelAdmin):

    filter_horizontal = ()
    list_filter = () 
    fieldsets = ()
    search_fields = ('account', 'duration', 'creation_method', 'rating')
    list_display = ('account', 'duration', 'creation_method', 'rating')
    readonly_fields = ('duration', 'creation_method', 'rating', 'image_file')
    list_filter = ('account', 'duration', 'creation_method', 'rating')
    
admin.site.register(CreationInfo, CreationAdmin)
    

class KeywordAdmin(admin.ModelAdmin):

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    search_fields = ('keyword',)
    list_display = ('keyword', 'creation')
    
admin.site.register(Keyword, KeywordAdmin)
    

class KeywordSummaryAdmin(ModelAdmin):
    change_list_template = 'creation_change_list.html'
    def has_add_permission(self, request):
        return False 
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        keyword_counts = Keyword.objects.values('keyword').annotate(total_count=Count('keyword'))

        popular_keywords = keyword_counts.order_by('-total_count')

        popular_keywords_list = list(popular_keywords.values('keyword', 'total_count'))

        response.context_data['popular_keywords'] = popular_keywords_list
        

        return response

class RatingSummaryAdmin(ModelAdmin):
    change_list_template = 'rating/rating_change_list.html'
    
    def has_add_permission(self, request):
        return False 

    list_filter = (
        'account', 
        'creation_method',
    )
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset

        except (AttributeError, KeyError):
            return response
        
        metrics = {
            'rating_count': Count('rating'),
        }

        rating_summary_data = list(
            qs
            .values('rating')
            .annotate(**metrics)
            .order_by('-rating_count')
        )

        response.context_data['rating_summary'] = rating_summary_data
        return response
admin.site.register(KeywordSummary, KeywordSummaryAdmin)
admin.site.register(RatingSummary, RatingSummaryAdmin)