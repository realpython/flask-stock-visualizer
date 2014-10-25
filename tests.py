import unittest
from app import app


class BasicTestCase(unittest.TestCase):

    def test_index(self):
        """ Ensure flask was set up correctly. """
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_index_slightly_better(self):
        """ Ensure '/' contains expected HTML. """
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertIn("<title>Flask Stock Visualizer</title>", response.data)


if __name__ == '__main__':
    unittest.main()
