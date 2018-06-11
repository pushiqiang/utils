from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
from .app import app as celery_app 
from .tasks import *

