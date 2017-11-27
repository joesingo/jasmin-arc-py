import os

import arc

from exceptions import InvalidConfigError


class ConnectionConfig(object):
    """
    Class to define available config options and their default values
    """

    #: Path to the private key file associated with your grid certificate
    CLIENT_KEY = "~/.arc/userkey-nopass.pem"

    #: Path to grid certificate file
    CLIENT_CERT = "~/.arc/usercert.pem"

    #: Path to directory containing trusted CA certificates
    CERTS_DIR = "/etc/grid-security/certificates"

    #: Path to the ``arcproxy`` binary, which is used to generate a proxy certificate from the
    #: private key and certificate
    ARCPROXY_PATH = "/usr/bin/arcproxy"

    #: Path to save the generated proxy certificate to
    PROXY_FILE = "/tmp/arcproxy_file"

    #: URL to the ARC server
    ARC_SERVER = "jasmin-ce.ceda.ac.uk:60000/arex"

    #: Number of seconds to set the validity period to when generating a proxy file (default: 12
    #: hours)
    PROXY_VALIDITY_PERIOD = 12 * 60 * 60

    #: The number of seconds the proxy file can have till expiry before a new proxy
    #: is automatically generated
    PROXY_RENEWAL_THRESHOLD = 10

    #: Path to job information file used by ARC client tools (arcstat, arcget etc) to load
    #: information about submitted jobs
    JOBS_INFO_FILE = "~/.arc/jobs.dat"

    #: The name of the file/directory to download when retrieving job outputs.
    OUTPUT_FILE = "output"

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
