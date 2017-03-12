import os
import pycrawler.main
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        a=12
        print a

    def tearDown(self):
        b=123
        print b

    def test_ola(self):
        assert 2==1

    def test_empty_db(self):
        assert 3==1
