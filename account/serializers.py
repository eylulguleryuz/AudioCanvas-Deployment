from account.models import Account
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


class AccountSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Account
        fields = [ 'username', 'email', 'date_joined', 'last_login', 'is_admin', 'is_active', 'is_staff', 'is_superuser']