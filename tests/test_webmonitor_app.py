import unittest
import webmonitor

class WebMonitorTest(unittest.TestCase):
    def setUp(self):
        self.app = webmonitor.create_app()
        self.client = self.app.test_client()


if __name__ == '__main__':
    unittest.main()
