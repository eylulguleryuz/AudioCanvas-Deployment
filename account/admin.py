from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import ModelAdmin
from django.db.models import Count, Max
from account.models import Account, AccountSummary
from datetime import datetime, timedelta
from django.contrib import messages

class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'date_joined', 'last_login', 'is_active', 'is_admin', 'is_staff')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    def changelist_view(self, request, extra_context=None):
        two_hours_ago = datetime.now() - timedelta(hours=0.16)
        inactive_user_count = Account.objects.filter(is_active=False, date_joined__lte=two_hours_ago).count()

        message = f"{inactive_user_count} inactive user{'s' if inactive_user_count != 1 else ''} found. You might want to take action."
        self.message_user(request, message, level=messages.INFO)

        return super().changelist_view(request)

class AccountSummaryAdmin(ModelAdmin):
    change_list_template = 'account/accountsummary_change_list.html'
    date_hierarchy = 'creationinfo__created_date'

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

        metrics = {
            'total': Count('creationinfo'),
            'latest_creation_date': Max('creationinfo__created_date'),
        }

        response.context_data['summary'] = list(
            qs
            .values('email',)
            .annotate(**metrics)
            .order_by('-total')
        )
        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )
        return response

admin.site.register(Account, AccountAdmin)    
admin.site.register(AccountSummary, AccountSummaryAdmin)
    
