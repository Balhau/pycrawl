import os
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        a=12
        #self.db_fd, main.app.config['DATABASE'] = tempfile.mkstemp()
        #self.app = main.app.test_client()
        #main.init_db()

    def tearDown(self):
        b=123
        #os.close(self.db_fd)
        #os.unlink(main.app.config['DATABASE'])

    def test_ola(self):
        assert 2==1

    def test_empty_db(self):
        assert 3==1
        #rv = self.app.get('/')
        #assert 'No entries here so far' in rv.data
