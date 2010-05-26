from django.db.models import Model 
from slugify import smart_slugify

class AutoSlugModel(Model):
    class Meta:
        abstract = True
    """same as django model but allows you to be lazy about the slug"""
    def __init__(self, *args, **kwargs):
        if not kwargs.get('slug') and 'slug' in self._meta.get_all_field_names():
            if kwargs.get('title'):
                kwargs['slug'] = smart_slugify(kwargs['title'], lower_case=True)
            elif kwargs.get('name'):
                kwargs['slug'] = smart_slugify(kwargs['name'], lower_case=True)
            elif kwargs:
                import warnings
                warnings.warn("Unable to automagically set slug (%s)" % \
                              self._meta.get_all_field_names())
        super(AutoSlugModel, self).__init__(*args, **kwargs)





               
                                                
