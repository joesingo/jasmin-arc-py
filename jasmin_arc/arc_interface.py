import os
import sys
from tempfile import NamedTemporaryFile
import json
import subprocess

from jinja2 import Environment, PackageLoader, select_autoescape
import arc

from constants import JobStatuses, LogLevels
from config import ConnectionConfig
from exceptions import (InvalidConfigError, ProxyGenerationError, InvalidJobDescription,
                        JobSubmissionError, NoTargetsAvailableError)


# Location of directory containing templates for JSDL XML
TEMPLATES_DIR = "templates"


class ArcInterface(object):
    """
    Class to handle interactions with the ARC-CE server
    """

    def __init__(self, config_path=None, log=sys.stdout, log_level=LogLevels.INFO):
        """
        Create an object to interface with the ARC server.

        :param config_path: Path to config JSON file, or ``None`` to use the default settings
        :param log:         File-like object to write log messages to, or ``None`` to disable
                            logging. Use ``sys.stdin`` or ``sys.stdout`` to print messages
        :param log_level:   The level of detail logs should show (default: :attr:`.LogLevels.INFO`).
                            See :class:`.LogLevels` for the available levels

        :raises InvalidConfigError: if config is not valid JSON or is otherwise invalid
        """
        try:
            config_dict = None

            if config_path:
                # Let errors reading file bubble to calling code
                with open(config_path) as config_file:
                    config_dict = json.load(config_file)

            self.config = ConnectionConfig.create_config(config_dict)
            ConnectionConfig.validate(self.config)

        # Catch JSON parsing errors
        except ValueError as e:
            raise InvalidConfigError(e.message)

        # Create jinja2 environment for loading JSDL template(s)
        self.env = Environment(loader=PackageLoader(__name__, TEMPLATES_DIR),
                               autoescape=select_autoescape(["xml"]))

        self.logger = arc.Logger(arc.Logger_getRootLogger(), "jobsubmit")
        # Add a log destination if the user has provided one
        if log:
            log_dest = arc.LogStream(log)
            log_dest.setFormat(arc.ShortFormat)
            arc.Logger_getRootLogger().addDestination(log_dest)
            arc.Logger_getRootLogger().setThreshold(log_level.value)

    def submit_job(self, executable, *args):
        """
        Submit a job and return the job ID

        :param executable: The command to run on the LOTUS cluster
        :param *args:      Arguments to pass to the executable

        :raises NoTargetsAvailableError: if no execution targets can be found on the ARC server
        :raises JobSubmissionError:      if the job cannot be submitted to any targets

        :return: Job ID
        """
        endpoint = arc.Endpoint(self.config["arc_server"], arc.Endpoint.COMPUTINGINFO)

        self.create_proxy()
        user_config = self.create_user_config()

        # Get the ExecutionTargets of this ComputingElement
        retriever = arc.ComputingServiceRetriever(user_config, [endpoint])
        retriever.wait()
        targets = retriever.GetExecutionTargets()

        if len(targets) == 0:
            raise NoTargetsAvailableError("No targets available")

        template = self.env.get_template("job_template.xml")
        jsdl = template.render({
            "name": "ARC job",  # TODO: Use sensible name or omit
            "executable": executable,
            "arguments": args
        })
        job_descriptions = self.get_job_descriptions(jsdl)

        # Create an empty job object which will contain our submitted job
        job = arc.Job()

        # Submit job directly to the execution targets, without a broker
        # Try each target until successfully submitted
        for target in targets:
            msg = "Attempting to submit job to {} ({})".format(target.ComputingEndpoint.URLString,
                                                               target.ComputingEndpoint.InterfaceName)
            self.logger.msg(arc.DEBUG, msg)

            if target.Submit(user_config, job_descriptions[0], job):
                break
            else:
                self.logger.msg(arc.DEBUG, "Failed to submit job")
        else:
            raise JobSubmissionError("Could not submit job to any of the {} available target(s)"
                                     .format(len(targets)))

        self.logger.msg(arc.INFO, "Started job with ID: {}".format(job.JobID))
        return job.JobID

    def get_job_status(self, job_id):
        """
        Return the status of the given job
        """
        return JobStatuses.COMPLETED

    def cancel_job(self, job_id):
        """
        Cancel the given job
        """
        self.logger.msg(arc.INFO, "Cancelling job {}".format(job_id))

    def save_job_outputs(self, job_id, output_path=None, errors_path=None):
        """
        Retrieve the output and errors files for a job and save them to the paths given
        """
        if output_path:
            self.logger.msg(arc.INFO, "Saving output file to '{}'".format(output_path))

        if errors_path:
            self.logger.msg(arc.INFO, "Saving errors file to '{}'".format(errors_path))

    def create_proxy(self):
        """
        Use ``arcproxy`` to create a proxy certificate from private key and certificate, and save
        it to the path given in the config

        :raises ProxyGenerationError: if the certificate cannot be generated
        """
        try:
            output = subprocess.check_output([self.config["arcproxy_path"],
                                             "-C", self.config["client_cert_file"],
                                             "-K", self.config["pem_file"],
                                             "-P", self.config["proxy_file"]])
        except subprocess.CalledProcessError:
            raise ProxyGenerationError("Could not create proxy with arcproxy")

        except OSError as ex:
            raise OSError("Failed to run arcproxy command: {}".format(ex))

        self.logger.msg(arc.INFO, "arcproxy output:\n{}".format(output))

    def create_user_config(self):
        """
        Create a user config for use with ARC client. Must be called after proxy has been created
        with :meth:`create_proxy`.

        :return: An instance of ``arc.UserConfig`` containing information about the necessary
                 keys, certificates and proxy files
        """
        # Write client config to temp file - arc python library seems buggy when using a
        # proxy file in non-default location. Default location has the current user's
        # UID appended to it, so this is probably the cleanest way
        conf_template = self.env.get_template("arc_config.ini")
        conf_filename = None
        with NamedTemporaryFile(delete=False) as conf_file:
            conf_filename = conf_file.name
            conf_file.write(conf_template.render({
                "proxy_file": self.config["proxy_file"],
                "certs_dir": self.config["certs_dir"]
            }))

        user_config = arc.UserConfig(conf_filename)
        os.unlink(conf_filename)
        return user_config

    def get_job_descriptions(self, jsdl):
        """
        Return an instance of ``arc.JobDescriptionList`` containing the job described by the given JSDL

        :param jsdl: String containing the job description in JSDL format
        """
        job_descriptions = arc.JobDescriptionList()
        temp_filename = None
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
            temp_file.write(jsdl)

        try:
            if not arc.JobDescription_ParseFromFile(temp_filename, job_descriptions):
                raise InvalidJobDescription("Could not parse job description XML")
        finally:
            # Delete the temp file - finally clause is run even if exception is raised
            os.unlink(temp_filename)

        return job_descriptions

