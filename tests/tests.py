import unittest
import os
import json
from tempfile import NamedTemporaryFile

from jasmin_arc.arc_interface import ArcInterface
from jasmin_arc.exceptions import InvalidConfigError, ProxyGenerationError


class ArcInterfaceTests(unittest.TestCase):

    def setUp(self):
        self.temp_files = []

    def tearDown(self):
        for f in self.temp_files:
            os.unlink(f)

    def test_invalid_config(self):
        """
        Test that providing an invalid config file raises the expected exception
        """
        filename = None
        with NamedTemporaryFile(delete=False) as config_file:
            filename = config_file.name
            config_file.write("this is not valid JSON!")

        self.temp_files.append(filename)

        with self.assertRaises(InvalidConfigError):
            a = ArcInterface(filename)

    def test_proxy_generation_failure(self):
        """
        Test that using a non-existant key file raises the expected exception
        """
        filename = None
        with NamedTemporaryFile(delete=False) as config_file:
            filename = config_file.name
            json.dump({"PEM_FILE": "/tmp/nonexistentfile"}, config_file)

        self.temp_files.append(filename)

        a = ArcInterface(filename)
        with self.assertRaises(ProxyGenerationError):
            a.submit_job("/bin/echo")

if __name__ == "__main__":
    unittest.main()

