import os

import arc

from exceptions import InvalidConfigError


class ConnectionConfig(object):
    """
    Class to define required keys for config files and the default config settings, and to provide
    methods to create and validate config dicts
    """

    PEM_FILE = "~/.arc/userkey-nopass.pem"
    """Path to the private key file associated with your grid certificate"""

    CLIENT_CERT_FILE = "~/.arc/usercert.pem"
    """Path to grid certificate file"""

    BROWSER_CERT_FILE = "~/certBundle.p12"
    """**Description here**"""

    CERTS_DIR = "/etc/grid-security/certificates"
    """**Description here**"""

    ARCPROXY_PATH = "/usr/bin/arcproxy"
    """
    Path to the ``arcproxy`` binary, which is used to generate a proxy certificate from the
    private key and certificate
    """

    PROXY_FILE = "/tmp/arcproxy_file"
    """Path to save the generated proxy certificate to"""

    ARC_SERVER = "jasmin-ce.ceda.ac.uk:60000/arex"
    """URL to the ARC server"""

    OUTPUTS_FILENAME = "outputs.zip"
    """
    The name of the file that will be retrieved when saving job outputs. This should match the
    location output is written to in your job scripts.
    """

    ERRORS_FILENAME = "errors_file.txt"
    """Similar to ``OUTPUTS_FILENAME`` but for error output."""

    def __init__(self, config_dict={}, logger=None):
        """
        :param config_dict: A dictionary containing options to override. Each key should be one of
                            the default options listed above
        :param logger:      An instance of ``arc.Logger`` used to log warnings about invalid config
                            options
        """
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
            elif logger:
                logger.msg(arc.WARNING, "'{}' is not a valid config option".format(key))

