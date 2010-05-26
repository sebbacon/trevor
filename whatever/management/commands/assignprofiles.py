from django.core.management.base import NoArgsCommand

from whatever import models

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        users = models.CustomUser.objects.all()
        for user in users:
            profile = models.RegistrationProfile.objects\
                      .filter(email=user.email)
            if not profile:
                new_profile = models.RegistrationProfile.objects\
                              .create_profile(user, email=False)
                activated = models.RegistrationProfile.objects\
                            .activate_user(new_profile.activation_key)
                print user, activated
                                                    
                                                    
