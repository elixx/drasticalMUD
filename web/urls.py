"""
Url definition file to redistribute incoming URL requests to django
views. Search the Django documentation for "URL dispatcher" for more
help.

"""

from django.urls import path, include

from evennia.web.website.urls import urlpatterns as evennia_default_urlpatterns
from web.custom import areaView, toplistView, playerView, areaInfoView

# default evennia patterns

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
    path(r'toplist/', toplistView.as_view(), name='toplist'),
    path(r'areas/', areaView.as_view(), name='areas'),
    path(r'area/<area_name>', areaInfoView.as_view(), name='areainfo'),
    path(r'player/<object_id>', playerView.as_view(), name='player')
]

# 'urlpatterns' must be named such for Django to find it.
urlpatterns = urlpatterns + evennia_default_urlpatterns
