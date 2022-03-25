"""
Url definition file to redistribute incoming URL requests to django
views. Search the Django documentation for "URL dispatcher" for more
help.

"""

from django.urls import path, include
from web.custom import areaView
# default evennia patterns

from evennia.web.website.urls import urlpatterns as evennia_default_urlpatterns

# add patterns
urlpatterns = [
    # website
    path("", include("evennia.web.website.urls")),
    # webclient
    path("webclient/", include("evennia.web.webclient.urls")),
    # web admin
    path("admin/", include("evennia.web.admin.urls")),
    # add any extra urls here:
    # path("mypath/", include("path.to.my.urls.file")),
    path(r'areas/', areaView.as_view(), name='areas')
]

# 'urlpatterns' must be named such for Django to find it.
urlpatterns = urlpatterns + evennia_default_urlpatterns
