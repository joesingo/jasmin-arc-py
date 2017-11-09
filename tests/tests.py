import unittest
import copy

from jasmin_arc.config import ConnectionConfig
from jasmin_arc.exceptions import InvalidConfigError


class ConfigTests(unittest.TestCase):

    def test_valid_config(self):
        """
        Test that the default config with no customisations is marked as valid
        """
        config = ConnectionConfig.create_config()
        try:
            ConnectionConfig.validate(config)
        except InvalidConfigError as e:
            self.fail("Config incorrectly marked as invalid: '{}'".format(e.message))

    def test_missing_key(self):
        """
        Test that configs with missing required keys are marked as invalid
        """
        config = ConnectionConfig.create_config()
        key = ConnectionConfig.REQUIRED_KEYS[0]
        del config[key]
        self.assertRaises(InvalidConfigError, ConnectionConfig.validate, config)

    def test_invalid_type(self):
        """
        Test that configs containing non-string values are marked as invalid
        """
        config = ConnectionConfig.create_config()
        key = ConnectionConfig.REQUIRED_KEYS[0]
        config[key] = {}
        self.assertRaises(InvalidConfigError, ConnectionConfig.validate, config)

    def test_override_value(self):
        """
        Test that default values can be overridden
        """
        key = ConnectionConfig.REQUIRED_KEYS[0]
        config = ConnectionConfig.create_config({key: "mycustomvalue"})
        self.assertEqual(config[key], "mycustomvalue")

    def test_extra_keys(self):
        """
        Test that adding extraneous keys in the config does not mean it is invalid
        """
        config = ConnectionConfig.create_config({"extrakeyhere": "hello"})
        try:
            ConnectionConfig.validate(config)
        except InvalidConfigError as e:
            self.fail("Config incorrectly marked as invalid: '{}'".format(e.message))


if __name__ == "__main__":
    unittest.main()

