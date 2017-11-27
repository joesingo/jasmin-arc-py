import os
import sys
import tempfile
import json
import subprocess

from jinja2 import Environment, PackageLoader, select_autoescape
import arc

from constants import JobStatuses, ARC_STATUS_MAPPING, LogLevels
from config import ConnectionConfig
from exceptions import (InvalidConfigError, ProxyGenerationError, InvalidJobDescription,
                        JobSubmissionError, NoTargetsAvailableError, JobNotFoundError,
                        InputFileError)


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
                            logging. Use ``sys.stdout`` or ``sys.stderr`` to print messages
                            (default: ``sys.stdout``).
        :param log_level:   The level of detail logs should show (default: `LogLevels.INFO`).
                            See `LogLevels` for the available levels

        :raises InvalidConfigError: if config is not valid JSON or is otherwise invalid
        """

        self.logger = arc.Logger(arc.Logger_getRootLogger(), "jobsubmit")
        # Add a log destination if the user has provided one
        if log:
            log_dest = arc.LogStream(log)
            log_dest.setFormat(arc.ShortFormat)
            arc.Logger_getRootLogger().addDestination(log_dest)
            arc.Logger_getRootLogger().setThreshold(log_level.value)

        config_dict = {}
        if config_path:
            try:
                self.logger.msg(arc.DEBUG, "Using jasmin_arc config: {}".format(config_path))
                # Let errors reading file bubble to calling code
                with open(config_path) as config_file:
                    config_dict = json.load(config_file)

            # Catch JSON parsing errors
            except ValueError as e:
                raise InvalidConfigError(e.message)

        self.config = ConnectionConfig(config_dict, logger=self.logger)

        # Create jinja2 environment for loading JSDL template(s)
        self.env = Environment(loader=PackageLoader(__name__, TEMPLATES_DIR),
                               autoescape=select_autoescape(["xml"]))

        self.cached_user_config = None

    def submit_job(self, executable, args=[], input_files=[]):
        """
        Submit a job and return the job ID

        :param executable:  The command to run on the LOTUS cluster
        :param args:        List of arguments to pass to the executable
        :param input_files: A list of paths to local files to copy to the remote session directory
                            (the directory the job will run from on JASMIN)

        :raises InputFileError:          if any of the specified input files do not exist or are
                                         directories
        :raises NoTargetsAvailableError: if no execution targets can be found on the ARC server
        :raises JobSubmissionError:      if the job cannot be submitted to any targets

        :return: Job ID
        """
        endpoint = arc.Endpoint(self.config.ARC_SERVER, arc.Endpoint.COMPUTINGINFO)

        user_config = self.get_user_config()

        # Get the ExecutionTargets of this ComputingElement
        retriever = arc.ComputingServiceRetriever(user_config, [endpoint])
        retriever.wait()
        targets = retriever.GetExecutionTargets()

        if len(targets) == 0:
            raise NoTargetsAvailableError("No targets available")

        input_files_map = {}  # Map local paths to destination file names
        for filename in input_files:
            if not os.path.isfile(filename):
                raise InputFileError("{} is not a file".format(filename))

            # Use absolute local path
            input_files_map[os.path.abspath(filename)] = os.path.basename(filename)

        template = self.env.get_template("job_template.xml")
        jsdl = template.render({
            "name": "ARC job",  # TODO: Use sensible name or omit
            "executable": executable,
            "arguments": args,
            "input_files_map": input_files_map,
            "output_file": self.config.OUTPUT_FILE
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

        # Write information on submitted job to local job list so standard arc tools (arcstat,
        # arcget etc) can be used with this job
        job_list = arc.JobInformationStorageBDB(self.config.JOBS_INFO_FILE)
        if not job_list.Write([job]):
          self.logger.msg(arc.WARNING, "Failed to write to local job list {}".format(self.config.JOBS_INFO_FILE))

        return job.JobID

    def get_job_status(self, job_id):
        """
        Return the status of the given job

        :param job_id:            ID of the job as returned by `submit_job`
        :raises JobNotFoundError: if no job with the given ID could be found

        :return: The status of the job (see `JobStatuses` for the available values)
        """
        job = self.get_job(job_id)
        # Map ARC status to a value in JobStatuses
        return ARC_STATUS_MAPPING[job.State.GetGeneralState()]

    def cancel_job(self, job_id):
        """
        Cancel the given job

        :param job_id:            ID of the job as returned by `submit_job`
        :raises JobNotFoundError: if no job with the given ID could be found
        """
        self.logger.msg(arc.INFO, "Cancelling job {}".format(job_id))
        job = self.get_job(job_id)
        if not job.Cancel():
            self.logger.msg(arc.WARNING, "Failed to cancel job")

    def save_job_outputs(self, job_id):
        """
        Retrieve output files from a job and save them to a temp directory. The file/directory
        specified in `OUTPUT_FILE` will be downloaded, and ``stdout`` and ``stderr`` outputs are
        saved as ``stdout.txt`` and ``stderr.txt`` respectively.

        :param job_id:            ID of the job as returned by `submit_job`
        :raises JobNotFoundError: if no job with the given ID could be found

        :return: Path to the directory the output files were saved in, or ``None`` if no files
                 were saved
        """
        job = self.get_job(job_id)
        user_config = self.get_user_config()
        temp_dir = tempfile.mkdtemp()
        # Last argument is 'force' - whether to continue if destination directory already exists
        success = job.Retrieve(user_config, arc.URL("file://{}".format(temp_dir)), True)

        # Remove temp dir and fail if no files were downloaded
        if not os.listdir(temp_dir):
            success = False
            os.rmdir(temp_dir)

        return temp_dir if success else None

    def create_proxy(self):
        """
        Use ``arcproxy`` to create a proxy certificate from private key and certificate, and save
        it to the path given in the config

        :raises ProxyGenerationError: if the certificate cannot be generated
        """
        try:
            output = subprocess.check_output([
                self.config.ARCPROXY_PATH,
                "-C", self.config.CLIENT_CERT,
                "-K", self.config.CLIENT_KEY,
                "-P", self.config.PROXY_FILE,
                "-c", "validityPeriod={}".format(self.config.PROXY_VALIDITY_PERIOD)
            ])

        except subprocess.CalledProcessError:
            raise ProxyGenerationError("Could not create proxy with arcproxy")

        except OSError as ex:
            raise OSError("Failed to run arcproxy command: {}".format(ex))

        self.logger.msg(arc.INFO, "arcproxy output:\n{}".format(output))

    def get_job(self, job_id):
        """
        Return an instance of ``arc.Job`` representing the job with the given ID

        :param job_id:            ID of the job as returned by `submit_job`
        :raises JobNotFoundError: if no job with the given ID could be found
        :return:                  Instance of ``arc.Job`` representing the job
        """
        user_config = self.get_user_config()

        # Create a JobSupervisor to handle all the jobs
        job_supervisor = arc.JobSupervisor(user_config)

        # Retrieve all the jobs from this computing element
        endpoint = arc.Endpoint(self.config.ARC_SERVER, arc.Endpoint.JOBLIST)
        retriever = arc.JobListRetriever(user_config)
        retriever.addConsumer(job_supervisor)
        retriever.addEndpoint(endpoint)
        retriever.wait()

        # Update the states of the jobs
        job_supervisor.Update()

        # Get all jobs and find job by ID
        jobs = job_supervisor.GetAllJobs()

        for job in jobs:
            if job.JobID == job_id:
                return job

        raise JobNotFoundError("Could not find a job with ID '{}'".format(job_id))

    def get_user_config(self):
        """
        Return the cached user config, or create a new one. Also check if proxy has expired, and
        create a new one if so

        :return: An instance of ``arc.UserConfig`` (see `create_user_config`)
        """
        # Create a new config if this is the first time
        if not self.cached_user_config:
            self.cached_user_config = self.create_user_config()
            return self.cached_user_config

        # Check proxy is still valid if using cached user config
        # Call arcproxy to query how many seconds proxy is valid for
        try:
            output = subprocess.check_output([self.config.ARCPROXY_PATH, "-P",
                                              self.config.PROXY_FILE, "-i", "validityLeft"])
        except subprocess.CalledProcessError:
            raise ProxyGenerationError("Failed to check proxy expiry time")
        except OSError as ex:
            raise OSError("Failed to run arcproxy command: {}".format(ex))

        try:
            seconds_left = int(output)
        except ValueError as ex:
            raise ProxyGenerationError("Failed to determine proxy expiry time: {}".format(ex))

        if seconds_left <= self.config.PROXY_RENEWAL_THRESHOLD:
            self.logger.msg(arc.INFO, "Renewing proxy")
            self.create_proxy()

        return self.cached_user_config

    def create_user_config(self):
        """
        Create a user config for use with ARC client

        :return: An instance of ``arc.UserConfig`` containing information about the necessary
                 keys, certificates and proxy files
        """
        self.create_proxy()

        # Write client config to temp file - arc python library seems buggy when using a
        # proxy file in non-default location. Default location has the current user's
        # UID appended to it, so this is probably the cleanest way
        conf_template = self.env.get_template("arc_config.ini")
        conf_filename = None
        with tempfile.NamedTemporaryFile(delete=False) as conf_file:
            conf_filename = conf_file.name
            conf_file.write(conf_template.render({
                "proxy_file": self.config.PROXY_FILE,
                "certs_dir": self.config.CERTS_DIR
            }))

        user_config = arc.UserConfig(conf_filename)
        os.unlink(conf_filename)
        return user_config

    def get_job_descriptions(self, jsdl):
        """
        Return an instance of ``arc.JobDescriptionList`` containing the job described by the
        given JSDL

        :param jsdl: String containing the job description in JSDL format
        """
        job_descriptions = arc.JobDescriptionList()
        temp_filename = None
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
            temp_file.write(jsdl)

        try:
            if not arc.JobDescription_ParseFromFile(temp_filename, job_descriptions):
                raise InvalidJobDescription("Could not parse job description XML")
        finally:
            # Delete the temp file - finally clause is run even if exception is raised
            os.unlink(temp_filename)

        return job_descriptions
