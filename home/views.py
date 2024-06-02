from django.shortcuts import render, redirect
from account.models import Account
from django.urls import reverse
from django.http import HttpResponseRedirect

def home_view(request):
	"""
	Define the behavior of the home view based on the user's authentication status.
	@param request - the HTTP request object
	@return Renders the home page (landing page) if the user is not authenticated, otherwise redirects to the logged_in page.
	"""
	context = {}
	user = request.user

	if not user.is_authenticated:
		return render(request, 'home.html', context)

	return redirect(reverse('logged_in'))


from django.urls import reverse

def custom_404_view(request, exception):
    return HttpResponseRedirect(reverse('home')) 


