from django.conf.urls import url
from . import views

app_name = 'darts'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^from/url/$', views.from_url, name='from_url'),
]
