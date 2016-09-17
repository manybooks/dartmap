import json
import os
from django.http import HttpResponse
from django.shortcuts import render
from urllib.parse import urlencode
from .parser import HtmlParser, TextParser

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secrets.json'), 'r') as f:
    secrets = json.load(f)
    GOOGLE_MAPS_JS_API_KEY = secrets['key']['js']

GOOGLE_MAPS_URL_BASE = 'https://maps.googleapis.com/maps/api/js?'
CALLBACK_FUNCTION = 'initMap'
MAP_SRC = GOOGLE_MAPS_URL_BASE + urlencode({'key': GOOGLE_MAPS_JS_API_KEY, 'callback': CALLBACK_FUNCTION, 'signed_in': 'true'})

def index(request):
    context = { 'map_src': MAP_SRC, }
    return render(request, 'darts/index.html', context)

def from_url(request, url):
    parser = HtmlParser(url=url)
    addresses = parser.make_darts()
    context = { 'map_src': MAP_SRC,
                'addresses': addresses}
    return render(request, 'darts/from_url.html', context)
