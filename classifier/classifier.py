#coding:utf-8
from sklearn.externals import joblib
from .address import Address
import os


class ClfAddress(object):
    def __init__(self):
        '''load trained classifier which judges the given words is address or not'''
        base = os.path.dirname(os.path.abspath(__file__))
        learned = os.path.join(base, 'svc.learned')
        self._clf = joblib.load(learned)

    def is_address(self, address_string):
        if not address_string:
            return False
        a = Address(address_string)
        a.preprocess()
        result = self._clf.predict(a.features)[0]
        if result == '1':
            return True
        else:
            return False
