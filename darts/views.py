import json
import os
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from urllib.parse import urlencode
from .forms import SourceUrlForm
from .parser import HtmlParser, TextParser

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secrets.json'), 'r') as f:
    secrets = json.load(f)
    GOOGLE_MAPS_API_KEY = secrets['key']['g_map_api']

GOOGLE_MAPS_URL_BASE = 'https://maps.googleapis.com/maps/api/js?'
CALLBACK_FUNCTION = 'initMap'
MAP_SRC = GOOGLE_MAPS_URL_BASE + urlencode({'key': GOOGLE_MAPS_API_KEY, 'callback': CALLBACK_FUNCTION, 'signed_in': 'true'})

def index(request):
    form = SourceUrlForm()
    context = {
        'map_src': MAP_SRC,
        'form': form,
    }
    return render(request, 'darts/index.html', context)

def from_url(request):
    form = SourceUrlForm(request.GET)
    url = ""
    if form.is_valid():
        url = form.cleaned_data['url']
    else:
        return HttpResponseRedirect(reverse('darts:index', args=(request)))
    parser = HtmlParser(url=url)
    darts = parser.make_darts()
    context = {
        'map_src': MAP_SRC,
        'darts': darts,
    }
    return render(request, 'darts/from_url.html', context)
