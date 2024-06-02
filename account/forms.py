from django import forms
from django.contrib.auth.forms import UserCreationForm
from account.models import Account
from django.contrib.auth import authenticate

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text='Required. Add a valid email.')

    class Meta:
        model = Account
        fields = ("email", "username", "password1", "password2")


class ResendActivationForm(forms.Form):

    class Meta:
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not email:
            raise forms.ValidationError("Email field is required.")

        try:
            user = Account.objects.get(email=email)
            if not user.is_active:
                return
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError('Email "%s" is not valid.' % email)
            

class AccountAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'password')
    
    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            try:
                user = Account.objects.get(email=email)
            except Account.DoesNotExist:
                raise forms.ValidationError('Invalid login')
            if not user.is_active:
                raise forms.ValidationError("Please confirm your email.")
                
            if not authenticate(email=email, password=password):
                raise forms.ValidationError('Incorrect email and/or password.')



class AccountUpdateForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ('email', 'username')
    
    def clean_email(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            try:
                account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
            except Account.DoesNotExist:
                return email 
            raise forms.ValidationError('Email "%s" is already in use.' % email)

    def clean_username(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            try:
                account = Account.objects.exclude(pk=self.instance.pk).get(username=username)
            except Account.DoesNotExist:
                return username 
            raise forms.ValidationError('Username "%s" is already in use.' % username)
