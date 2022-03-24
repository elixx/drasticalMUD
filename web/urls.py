"""
Url definition file to redistribute incoming URL requests to django
views. Search the Django documentation for "URL dispatcher" for more
help.

"""
from django.urls import path, include

# default evennia patterns
from evennia.web.urls import urlpatterns

import web.custom

# eventual custom patterns
custom_patterns = [
    # url(r'/desired/url/', view, name='example'),
    path(r'areas/', web.custom.areaView.as_view(), name='areas')
]

# this is required by Django.
urlpatterns = custom_patterns + urlpatterns
