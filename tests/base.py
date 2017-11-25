import os
import unittest

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
