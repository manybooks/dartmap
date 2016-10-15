#coding:utf-8
from bs4 import BeautifulSoup
from collections import OrderedDict, namedtuple
from . import encoding
from .models import Dart
import codecs
import requests
import os
import sys
import re

KEYWORDS = {"address": "address",
            "region": "region",
            "locality": "locality",
            "street": "street"}

#ADDRESS_PATTERN = "(?P<address>(.+[都道府県])?.*[市区町村].*[0-9０-９]+(?!.*[、。}]))" #都道府県を含まなくてもヒットするが、許容範囲が広くなりすぎてしまう
#ADDRESS_PATTERN = "(?P<address>\S{2,3}[都道府県]+.*[市区町村].*[0-9０-９]+(?!.*[、。}]))" #末尾が数字で切れてしまい、「階」、「F」、「館」などの情報が落ちてしまう。
#ADDRESS_PATTERN = "(?P<address>\S{2,3}[都道府県]+.*[市区町村].*[0-9０-９]+(?!.*[、。}]).*)" #句読点を含むものの除外ができない。
ADDRESS_PATTERN = "[：]*(?P<address>(?!.*(、|。))\S{2,3}[都道府県]+.*[市区町村].*[0-9０-９]+)" #現状もっとも精度が高いが、市区町村からはじまるケースに対応できない。
ADDRESS_WORD_CNT_MAX = 40
TABLE_NAME_PATTERN = ".*名.*"
PREFIX_NAME_PATTERN = ".*[名]+.*[:：]+(?P<place_name>.*)$"


class BaseParser(object):
    def make_darts(self):
        '''Make several marker of google maps from seed.
        This method must be overriden by childclass'''
        raise NotImplementedError()

class HtmlParser(BaseParser):
    def __init__(self, url, depth=0):
        assert isinstance(depth, int), "depth must be integer"
        self._depth = depth
        self._src_url = url
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
            addresses_re_matched = self._from_regular_expression(url);
            #addresses_kwd_matched = self._from_keyword_address(url);
            #addresses_separated = self._from_keyword_divisions(url);
            self._darts.update(addresses_re_matched)
            #self._darts.add(addresses_kwd_matched)
            #self._darts.add(addresses_separated)
        return self._darts

    def _from_regular_expression(self, url):
        soup = self._parse_url(url, bsFlag=True)
        elements_contain_address = soup.find_all(string=re.compile(ADDRESS_PATTERN))
        if not elements_contain_address:
            return None
        result = set()
        for idx, element_contain_address in enumerate(elements_contain_address):
            address = self._format_address(element_contain_address.string)
            place_name = self._get_place_name(element_contain_address).strip()
            dart = Dart(pk=idx+1, address=address, place_name=place_name, link_url=url, src_url=self._src_url)
            result.add(dart)
        return result

    def _format_address(self, address_string):
        formatted_address = self._remove_extra(address_string)
        if len(formatted_address) > ADDRESS_WORD_CNT_MAX:
            return None
        return formatted_address

    def _remove_extra(self, string_inside_element):
        """remove extra words like 'postal code' contained in BeautifulSoup element,
           and then return only string that express address"""
        address_str = re.search(ADDRESS_PATTERN, string_inside_element).group("address")
        return address_str

    def _get_place_name(self, element_contain_address):
        three_gen_parent = element_contain_address.parent.parent.parent

        #１．<td>等のテーブルのケース(ex)お遍路
        for td_th_element in three_gen_parent.find_all(['td', 'th']):
            if re.search(TABLE_NAME_PATTERN, td_th_element.string):
                element_contain_place_name = td_th_element.find_next(name=td_th_element.name, string=True)
                place_name = element_contain_place_name.string
                return place_name

        #２．<li>タグ<p>タグ等の中身で、名称：XXXのようにプリフィクスがついているケース(ex)find travel
        for string in three_gen_parent.stripped_strings:
            m = re.search(PREFIX_NAME_PATTERN, string)
            if m:
                place_name = m.group('place_name')
                return place_name

        #３．<p>タグ等のclassやproperty属性などにnameがふくまれているケース(ex)食べログ
        for element in element_contain_address.find_all_previous():
            for attribute_value in element.attrs.values():
                if _contain_keyword(attribute_value, "name"):
                    return element.string

        #４．<a>タグの中身が住所となっているケース(ex)東急ハンズ
        for element in element_contain_address.find_all_previous('a'):
            if element.string:
                return element.string
        return None

    def _has_attr_contains(self, kwd):
        """returns function object of attrs_contain_keyword keeping variable 'kwd' inside"""
        def attrs_contain_keyword(*args):
            for attr in args[0].attrs.values():
                return _contain_keyword(attr, kwd)
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

#util method below
def _contain_keyword(iterable, keyword):
    """bs4 tag.attrs.values() returns two‐dimensional list. This is why using recursive call in this function"""
    result = False
    if isinstance(iterable, str):
        return keyword in iterable.lower()
    for elem in iterable:
        result = _contain_keyword(elem, keyword)
        if result:
            break
    return result

def show_all(iterable):
    """print method for debug"""
    for elem in iterable:
        print (elem)

def show_matched_only(iterable):
    """print method for debug"""
    for elem in iterable:
        if re.search(ADDRESS_PATTERN, elem):
            print (elem)
