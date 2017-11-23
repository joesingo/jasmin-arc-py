import os

import arc

from exceptions import InvalidConfigError


class ConnectionConfig(object):
    """
    Class to define available config options and their default values
    """

    #: Path to the private key file associated with your grid certificate
    PEM_FILE = "~/.arc/userkey-nopass.pem"

    #: Path to grid certificate file
    CLIENT_CERT_FILE = "~/.arc/usercert.pem"

    #: **Description here**
    BROWSER_CERT_FILE = "~/certBundle.p12"

    #: **Description here**
    CERTS_DIR = "/etc/grid-security/certificates"

    #: Path to the ``arcproxy`` binary, which is used to generate a proxy certificate from the
    #: private key and certificate
    ARCPROXY_PATH = "/usr/bin/arcproxy"

    #: Path to save the generated proxy certificate to
    PROXY_FILE = "/tmp/arcproxy_file"

    #: URL to the ARC server
    ARC_SERVER = "jasmin-ce.ceda.ac.uk:60000/arex"

    #: The minimum number of seconds the proxy file may have left until expiry before a new proxy
    #: is automatically generated
    PROXY_RENEWAL_THRESHOLD = 10

    def __init__(self, config_dict, logger=None):
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

    def __getattribute__(self, key):
        """
        Expand ~ to home directory in config values
        """
        val = super(ConnectionConfig, self).__getattribute__(key)
        home_dir = os.environ.get("HOME")
        if home_dir:
            try:
                val = val.replace("~", home_dir)
            except AttributeError:
                pass

        return val
