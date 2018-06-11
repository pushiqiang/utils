
from __future__ import absolute_import

import os, sys
import django

from celery import Celery


app = Celery('bodybuilder_worker')
app.config_from_object('task_worker.settings')

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bodybuilder_moments.settings")
    django.setup() 

