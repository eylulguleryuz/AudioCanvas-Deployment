from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout,  get_user_model
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm, ResendActivationForm
from account.serializers import AccountSerializer
from account.models import Account
from rest_framework import viewsets, permissions,  generics, status
from creation.models import CreationInfo
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from account.decorators import user_not_authenticated
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from account.tokens import account_activation_token

@user_not_authenticated
def registration_view(request):
	context = {}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid(): 
			user = form.save(commit=False)  
			user.is_active = False  
			user.save()
			activateEmail(request, user, form.cleaned_data.get('email'))
			return redirect('login')
		else:
			context['registration_form'] = form
	else:
		form = RegistrationForm()
		context['registration_form'] = form
	return render(request, 'account/register.html', context)

def activateEmail(request, user, to_email):
    """
    Send an activation email to a user for account confirmation.
    @param request - the HTTP request object
    @param user - the user to activate the account for
    @param to_email - the email address to send the activation email to
    """
    mail_subject = 'Activate your user account.'
    message = render_to_string('account/account_confirmation.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user.username}, please go to your email {to_email} inbox and click on \
            received activation link to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')

def activate(request, uidb64, token):
	"""
	Activate a user account based on the provided token and user ID.
	@param request - the HTTP request object
	@param uidb64 - the user ID encoded in base64
	@param token - the activation token
	@return Redirects the user to the login page if activation is successful, otherwise redirects to the home page.
	"""
	try:
		uid = force_str(urlsafe_base64_decode(uidb64))
		user = Account.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
		user = None

	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()
		messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
		return redirect('login')
	else:
		messages.error(request, 'Activation link is invalid!')
		if user:
			activateEmail(request, user, user.email)
			messages.info(request, f'Activation email has been resent to {user.email}. Please check your email inbox.')

	return redirect('home')


def logout_view(request):
	logout(request)
	return redirect('home')


def login_view(request):
	context = {}

	user = request.user
	if user.is_authenticated:
		return redirect('home')
	
	if request.POST:
		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():
			email=request.POST['email']
			password = request.POST['password']
			user = authenticate(email=email, password=password)
			if user:
				login(request, user)
				return redirect('home')

					
	else:
		form = AccountAuthenticationForm()
	
	context['login_form'] = form
	return render(request, 'account/login.html', context)


def resend_confirmation(request):
	"""
	Resend the account activation email if the user requests it.
	@param request - the HTTP request object
	@return the rendered resend confirmation page
	"""
	context = {}

	user = request.user
	if user.is_authenticated:
		return redirect('home')
	
	if request.method == 'POST':
		form = ResendActivationForm(request.POST)
		if form.is_valid():
			email=request.POST['email']
			try:
				user = Account.objects.get(email=email)
				if user.is_active:
					messages.info(request, "Your account is already active.")
				else:
					activateEmail(request, user, email)
					return redirect('login')
			except Account.DoesNotExist:
				messages.info(request, "This account doesn't exist.")
	else:
		form = ResendActivationForm()
    
	context = {'activation_form': form}
	return render(request, 'account/resend_confirmation.html', context)


def account_view(request):

	if not request.user.is_authenticated:
		return redirect("login")

	context = {}

	if request.POST:
		form = AccountUpdateForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			context['success_message'] = "Information updated!"
			form = AccountUpdateForm(instance=request.user)
	else:
		form = AccountUpdateForm(
				initial= {
					"email": request.user.email,
					"username": request.user.username,
				}
			)
	context['account_form'] = form
	return render(request, 'account/account.html', context)

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    context = {}
    creation_infos = CreationInfo.objects.filter(account=request.user).order_by('-starred', '-created_date')
    context['creation_infos'] = creation_infos
    return render(request, 'profile/profile.html', context)

def delete_creation(request):
	"""
	Delete a creation based on the provided creation_id and return the updated list of creations for the current user.
	@param request - the HTTP request object
	@return The updated list of creation_infos for the current user.
	"""
	creation_id = request.POST.get('creation_id')
	creation = get_object_or_404(CreationInfo, pk=creation_id)
	creation.delete()
	creations = CreationInfo.objects.filter(account=request.user).order_by('-starred', '-created_date')
	return render(request, 'profile/profile_partial.html', {'creation_infos': creations})

def heart_creation(request):
	"""
	Create or update a heart (favorite) for a creation based on the request data.
	@param request - the HTTP request object
	@return Renders the updated creation information in the profile_partial.html template.
	"""
	creation_id = request.POST.get('creation_id')
	creation = get_object_or_404(CreationInfo, pk=creation_id)
	creation.starred = not creation.starred
	creation.save()
	creations = CreationInfo.objects.filter(account=request.user).order_by('-starred', '-created_date')
	return render(request, 'profile/profile_partial.html', {'creation_infos': creations})


def sort_profile_view(request):
	user = request.user
	sort_criteria = request.GET.get('sort')

	if sort_criteria == 'starred':
		creations = CreationInfo.objects.filter(account=user).order_by('-starred', '-created_date')
	elif sort_criteria == 'newToOld':
		creations = CreationInfo.objects.filter(account=user).order_by('-created_date')
	elif sort_criteria == 'OldToNew':
		creations = CreationInfo.objects.filter(account=user).order_by('created_date')
	else:
		# Default sorting
		creations = CreationInfo.objects.filter(account=user).order_by('-starred', '-created_date')
	return render(request, 'profile/profile_partial.html', {'creation_infos': creations})
