"""
Wrapper for loading templates from "templates" directories in INSTALLED_APPS
packages.
"""

import os
import sys
from itertools import chain

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist
from django.utils._os import safe_join
from django.utils.importlib import import_module

# At compile time, cache the directories to search.
fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
app_template_dirs = []
for app in settings.INSTALLED_APPS:
    try:
        mod = import_module(app)
    except ImportError, e:
        raise ImproperlyConfigured, 'ImportError %s: %s' % (app, e.args[0])
    template_dir = os.path.join(os.path.dirname(mod.__file__), 'templates')
    if os.path.isdir(template_dir):
        app_template_dirs.append(template_dir.decode(fs_encoding))

# It won't change, so convert it to a tuple to save memory.
app_template_dirs = tuple(app_template_dirs)


def get_template_dirs_sources(template_name, template_dirs=None):
    """
    Returns the absolute paths to "template_name", when appended to each
    directory in "template_dirs". Any paths that don't lie inside one of the
    template dirs are excluded from the result set, for security reasons.
    """
    if not template_dirs:
        template_dirs = settings.TEMPLATE_DIRS
    skin_dir = settings.SKIN_DIRECTORY
    new_template_dirs = []
    for t in template_dirs:
        new_template_dirs.append(os.path.join(t, skin_dir))
    for template_dir in new_template_dirs:
        try:
            yield safe_join(template_dir, template_name)
        except UnicodeDecodeError:
            # The template dir name was a bytestring that wasn't valid UTF-8.
            raise
        except ValueError:
            # The joined path was located outside of this particular
            # template_dir (it might be inside another one, so this isn't
            # fatal).
            pass


def get_template_app_sources(template_name, template_dirs=None):
    """
    """
    if not template_dirs:
        template_dirs = app_template_dirs
    skin_dir = settings.SKIN_DIRECTORY
    new_template_dirs = []
    for t in template_dirs:
        new_template_dirs.append(os.path.join(t, skin_dir))
    for template_dir in new_template_dirs:
        try:
            yield safe_join(template_dir, template_name)
        except UnicodeDecodeError:
            # The template dir name was a bytestring that wasn't valid UTF-8.
            raise
        except ValueError:
            # The joined path was located outside of template_dir.
            pass

def get_template_sources(template_name, template_dirs=None):
    return chain(get_template_dirs_sources(template_name,
                                           template_dirs=template_dirs),
                 get_template_app_sources(template_name,
                                           template_dirs=template_dirs)
                 )

def load_template_source(template_name, template_dirs=None):
    template_dirs = template_dirs or []
    for filepath in get_template_sources(template_name, template_dirs):
        try:
            return (open(filepath).read().decode(settings.FILE_CHARSET), filepath)
        except IOError:
            pass
    raise TemplateDoesNotExist, template_name
load_template_source.is_usable = True
