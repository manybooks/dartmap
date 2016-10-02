#coding:utf-8
from bs4 import BeautifulSoup
from collections import OrderedDict, namedtuple
from . import encoding
import codecs
import json
import requests
import os
import sys
import re

KEYWORDS = {"address": "address",
            "region": "region",
            "locality": "locality",
            "street": "street"}

#ADDRESS_PATTERN = "(?P<address>(.+[都道府県])?.*[市区町村].*[0-9０-９]+(?!.*[、。}]))" #都道府県を含まなくてもヒットするが、許容範囲が広くなりすぎてしまう
#ADDRESS_PATTERN = "(?P<address>.{2,3}[都道府県]+.*[市区町村].*[0-9０-９]+(?!.*[、。}]))" #手前の「住所：」や郵便番号が入ってしまう
ADDRESS_PATTERN = "(?P<address>\S{2,3}[都道府県]+.*[市区町村].*[0-9０-９]+(?!.*[、。}]))"

ADDRESS_WORD_CNT_MAX = 40

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secrets.json'), 'r') as f:
    secrets = json.load(f)
    GOOGLE_MAPS_API_KEY = secrets['key']['g_map_api']

class BaseParser(object):
    def make_darts(self):
        '''Make several marker of google maps from seed.
        This method must be overriden by childclass'''
        raise NotImplementedError()

class HtmlParser(BaseParser):
    def __init__(self, url, depth=0):
        assert isinstance(depth, int), "depth must be integer"
        self._depth = depth
        self._urls = [url]
        self._darts = set()
        for search_function in encoding.search_functions():
            codecs.register(search_function)

    def _parse_url(self, url, bsFlag=False):
        res = requests.get(url)
        res.raise_for_status()
        if bsFlag:
            return BeautifulSoup(res.text.encode(res.encoding), "html.parser")
        else:
            return res.text

    def _get_inside_links(self, root):
        urls = set([root])
        visited = []
        while self._depth:
            for url in urls:
                if not url in visited:
                    visited.append(url)
                    urls.update(self._get_child_page(url))

        return urls

    def _get_child_page(self, url):
        text = self._parse_url(url)
        pattern = "href=['\"]+(?P<link>.*?)['\"]+"
        links = re.findall(pattern, text)
        for link in links:
            print (link)
        print (len(links))
        return links

    def make_darts(self):
        for url in self._urls:
            addresses_re_matched = self._from_regular_expression(url); print(len(addresses_re_matched)); show_all(addresses_re_matched)
            #addresses_kwd_matched = self._from_keyword_address(url); print(len(addresses_kwd_matched)); show_all(addresses_kwd_matched)
            #addresses_separated = self._from_keyword_divisions(url); print(len(addresses_separated)); show_all(addresses_separated)
        return addresses_re_matched

    def _from_regular_expression(self, url):
        soup = self._parse_url(url, bsFlag=True)
        elements_contain_address = soup.find_all(string=re.compile(ADDRESS_PATTERN))
        if elements_contain_address:
            darts = set([self._remove_extra(element_contain_address.string)
                            for element_contain_address
                            in elements_contain_address
                            if len(self._remove_extra(element_contain_address.string)) < ADDRESS_WORD_CNT_MAX])
        else:
            darts = set()
        return darts

    def _remove_extra(self, string_inside_element):
        """remove extra words like 'postal code' contained in BeautifulSoup element,
           and then return only string that express address"""
        address_str = re.search(ADDRESS_PATTERN, string_inside_element).group("address")
        return address_str

    def _has_attr_contains(self, kwd):
        """returns function object of attrs_contain_keyword keeping variable 'kwd' inside"""
        def contain_keyword(iterable, keyword):
            """returns True if iterable contains keyword, otherwise returns False"""
            result = False
            if isinstance(iterable, str):
                return keyword in iterable.lower()
            for elem in iterable:
                result = contain_keyword(elem, keyword)
                if result:
                    break
            return result

        def attrs_contain_keyword(*args):
            for attr in args[0].attrs.values():
                return contain_keyword(attr, kwd)
        return attrs_contain_keyword

    def _from_keyword_address(self, url):
        found = set()
        soup = self._parse_url(url, bsFlag=True)
        tags_of_address = soup.find_all(self._has_attr_contains(KEYWORDS["address"]))
        if tags_of_address:
            found.update(set([tag.string for tag in tags_of_address if tag.string]))
        return found

    def _from_keyword_divisions(self, url):
        found = set()
        soup = self._parse_url(url, bsFlag=True)
        tags_of_region = soup.find_all(self._has_attr_contains(KEYWORDS["region"]))
        tags_of_locality = soup.find_all(self._has_attr_contains(KEYWORDS["locality"]))
        tags_of_street = soup.find_all(self._has_attr_contains(KEYWORDS["street"]))
        o = Organizer(tags_of_region, tags_of_locality, tags_of_street)
        found = o.organize()
        return found

    def _get_descendant_content(self, tag):
        pass

class TextParser(BaseParser):
    pass

class Organizer(object):
    def __init__(self, region_tags, locality_tags, street_tags):
        self.region_tags = region_tags
        self.locality_tags = locality_tags
        self.street_tags = street_tags

    def organize(self):
        tag_trios = []
        result = set()
        every_tags_has_value = min(map(lambda key: len(self.__dict__[key]), self.__dict__.keys())) > 0
        if every_tags_has_value:
            tag_trios = self._get_tag_trio_has_same_parent()
        if tag_trios:
            result = { self._get_contents_from_tag_trio(tag_trio) for tag_trio in tag_trios }
        return result

    def _get_tag_trio_has_same_parent(self):
        tags_have_same_parent = []
        for region_tag in self.region_tags:
            locality_tag = list(filter(lambda locality_tag: locality_tag.parent == region_tag.parent, self.locality_tags))[0]
            street_tag = list(filter(lambda street_tag: street_tag.parent == region_tag.parent, self.street_tags))[0]
            if locality_tag and street_tag:
                tags_have_same_parent.append([region_tag, locality_tag, street_tag])
        return tags_have_same_parent

    def _get_contents_from_tag_trio(self, tag_trio):
        return "".join([tag.get_text() for tag in tag_trio])

def show_all(iterable):
    """print method for debug"""
    for elem in iterable:
        print (elem)

def show_matched_only(iterable):
    """print method for debug"""
    for elem in iterable:
        if re.search(ADDRESS_PATTERN, elem):
            print (elem)
