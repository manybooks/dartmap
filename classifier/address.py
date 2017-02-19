#coding:utf-8
import pandas as pd

kwds = ("県", "都", "道", "府")
puncs = ("、", "。", "！", "？")
spaces = (" ", "　")

#1.文字数
def count_of(s):
    return len(s)

#2.数字の数
def cnt_of_num_in(s):
    is_numeric = [1 if c.isnumeric() else 0 for c in s]
    return sum(is_numeric)

#3.空白文字の数
def cnt_of_space_in(s):
    is_space = [1 if c in spaces else 0 for c in s]
    return sum(is_space)

#4.都道府県を含むか否か
def kwd_in(s):
    for kwd in kwds:
        if kwd in s:
            return 1
    return 0

#5.句読点などを含むか否か
def punc_in(s):
    for punc in puncs:
        if punc in s:
            return 1
    return 0

#6.数字で終わるか否か
def is_numeric_the_last_char_of(s):
    last_char = s[-1:]
    return 1 if last_char.isnumeric() else 0


class Address(object):
    def __init__(self, matched_expression):
        self._string = str(matched_expression)

    def preprocess(self):
        self._word_cnt = count_of(self._string)
        self._num_cnt = cnt_of_num_in(self._string)
        self._space_cnt = cnt_of_space_in(self._string)
        self._has_kwd = kwd_in(self._string)
        self._has_punc = punc_in(self._string)
        self._ends_with_numeric = is_numeric_the_last_char_of(self._string)
        self.features = pd.DataFrame([[self._word_cnt, self._num_cnt, self._space_cnt, self._has_kwd, self._has_punc, self._ends_with_numeric]])
