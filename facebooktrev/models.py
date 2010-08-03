from django.db import models

from whatever.models import CustomUser

class FacebookUser(models.Model):
    uid = models.CharField(max_length=80)
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(CustomUser,
                             blank=True,
                             null=True,
                             related_name="facebookuser")
    friends = models.ManyToManyField('self',
                                     blank=True,
                                     null=True)
    def __unicode__(self):
        return "%s (uid %s)" % (self.user, self.uid)
    
