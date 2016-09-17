from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^from/url/(?P<url>https?://[\w/:%#\$&\?\(\)~\.=\+\-]+)$', views.from_url, name='from_url'),
]
