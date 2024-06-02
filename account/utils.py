from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def send_confirmation_email(user):
    """
    Send a confirmation email to the user with a unique confirmation link.
    @param user - the user object for whom the confirmation email is being sent
    @return None
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    confirmation_link = f"http://example.com/confirm-email/{uid}/{token}"
    message = f"Click the following link to confirm your email: {confirmation_link}"
    send_mail("Confirm your email", message, "from@example.com", [user.email])
