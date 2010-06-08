from django.contrib.auth.backends import ModelBackend

from whatever.models import CustomUser

class NoAuthBackend(ModelBackend):
    """
    Authenticates against signup.models.CustomUser, without requiring
    authorisation
    """
    def authenticate(self, username=None, password=None):
        try:
            username = username.lower() # we're using emails
            user = CustomUser.objects.get(username=username)
            if password is None:
                user.login_count += 1
                user.save()
                return user
            else:
                if user.check_password(unicode(password)):
                    user.login_count += 1
                    user.save()
                    return user
                else:
                    return None                
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None

