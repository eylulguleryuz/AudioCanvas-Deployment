from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six  

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Define a custom token generator for account activation tokens based on the PasswordResetTokenGenerator class.
    @param PasswordResetTokenGenerator - The base token generator class.
    @returns AccountActivationTokenGenerator - An instance of the custom token generator for account activation.
    """
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp)  + six.text_type(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator()