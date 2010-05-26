import sys
import os
#Calculate the path based on the location of the WSGI script.
sys.path.append('/var/www/whatevertrevor')
sys.path.append('/var/www/whatevertrevor/trevor') 

#Add the path to 3rd party django application and to django itself.
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'trevor.settings'
       
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
