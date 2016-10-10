import json
import os
from django.http import HttpResponse
from django.shortcuts import render
from urllib.parse import urlencode
from .parser import HtmlParser, TextParser

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secrets.json'), 'r') as f:
    secrets = json.load(f)
    GOOGLE_MAPS_API_KEY = secrets['key']['g_map_api']

GOOGLE_MAPS_URL_BASE = 'https://maps.googleapis.com/maps/api/js?'
CALLBACK_FUNCTION = 'initMap'
MAP_SRC = GOOGLE_MAPS_URL_BASE + urlencode({'key': GOOGLE_MAPS_API_KEY, 'callback': CALLBACK_FUNCTION, 'signed_in': 'true'})

def index(request):
    context = { 'map_src': MAP_SRC, }
    return render(request, 'darts/index.html', context)

def from_url(request, url):
    src_url_from_top_page = request.GET.get("src_url", False)
    if src_url_from_top_page:
        url = src_url_from_top_page
    else:
        url += _get_query_in_src_url(request)
    parser = HtmlParser(url=url)
    darts = parser.make_darts()
    context = { 'map_src': MAP_SRC,
                'darts': darts}
    return render(request, 'darts/from_url.html', context)

def _get_query_in_src_url(request):
    """if source url contains query, WSGI recognize that as 'QUERY_STRING' of META information and
    remove from 'url' keyword argument of from_url function. So this function salvage and return
    the query part of source url."""
    query = request.META["QUERY_STRING"]
    if query:
        return "?" + query
    return ""
