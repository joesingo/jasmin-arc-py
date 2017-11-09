from .exceptions import InvalidConfigError


class ConnectionConfig(object):
    """
    Class to define required keys for config files and the default config settings, and to provide
    methods to create and validate config dicts
    """
    REQUIRED_KEYS = ["pem_file", "client_cert_file", "browser_cert_file", "certs_dir", "arc_proxy_cmd",
                     "myproxy_file", "arc_server", "outputs_filename", "errors_filename"]

    DEFAULT_CONFIG = {
        "pem_file": "~/.arc/userkey-nopass.pem",
        "client_cert_file": "~/.arc/usercert.pem",
        "browser_cert_file": "~/certBundle.p12",
        "certs_dir": "/etc/grid-security/certificates",
        "arc_proxy_cmd": "/usr/bin/arcproxy",
        "myproxy_file": "/tmp/x509up_u502",
        "arc_server": "jasmin-ce.ceda.ac.uk:60000/arex",
        "outputs_filename": "outputs.zip",
        "errors_filename": "errors_file.txt"
    }

    @classmethod
    def create_config(cls, config=None):
        """
        Update the default config with values from the given dictionary

        :param config: Dictionary to get overriden settings from, or None to use default settings
        :return: Dictionary containing config settings
        """
        c = dict(cls.DEFAULT_CONFIG)
        if config:
            c.update(config)
        return c

    @classmethod
    def validate(cls, config):
        """
        Verify that the config is valid

        :raises InvalidConfigError: if configuration is invalid
        """
        for key in cls.REQUIRED_KEYS:
            try:
                val = config[key]
            except KeyError as e:
                raise InvalidConfigError("Required key '{}' not present".format(key))

            if not isinstance(val, str):
                raise InvalidConfigError("Value for key '{}' is not a string".format(key))

