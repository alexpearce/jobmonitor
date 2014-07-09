import unittest2
import webmonitor

class TestWebMonitor(unittest2.TestCase):
    def setUp(self):
        self.app = webmonitor.create_app()
        self.client = self.app.test_client()


if __name__ == '__main__':
    unittest2.main()
