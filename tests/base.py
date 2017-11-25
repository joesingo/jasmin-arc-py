import os
import sys
import unittest
import time

from jasmin_arc import ArcInterface


class ArcTestCase(unittest.TestCase):
    """
    Base class for tests - used to create an ArcInterface instance on class set up
    """
    @classmethod
    def setUpClass(cls):
        config_path = os.environ.get("JASMIN_ARC_CONFIG", None)
        if config_path:
            print("Using config at {}".format(config_path))
        else:
            print("Using default config")

        cls.ARC_INTERFACE = ArcInterface(config_path)

    def wait(self, n):
        """
        Wait for n seconds
        """
        sys.stdout.write("Waiting for {} seconds".format(n))
        for _ in range(n):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\n")
