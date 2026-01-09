"""
WSGI config for manufatures project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

# Add local packages to path (Critical for PythonAnywhere)
path_to_packages = '/home/tele/.local/lib/python3.12/site-packages'
if path_to_packages not in sys.path:
    sys.path.append(path_to_packages)

# Add project root to path
path_to_project = '/home/tele/manufatures'
if path_to_project not in sys.path:
    sys.path.append(path_to_project)


from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')

application = get_wsgi_application()
