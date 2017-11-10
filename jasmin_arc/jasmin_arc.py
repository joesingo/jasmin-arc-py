import json

from jinja2 import Environment, PackageLoader, select_autoescape

from .status import JOB_STATUSES
from .config import ConnectionConfig
from .exceptions import InvalidConfigError


# Location of directory containing templates for JSDL XML
TEMPLATES_DIR = "templates"


class ArcInterface(object):
    """
    Class to handle interactions with the ARC-CE server
    """

    def __init__(self, config_path=None):
        """
        Create an object to interface with the ARC server.

        :param config_path: Path to config JSON file, or None to use the default settings
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

    def submit_job(self, executable, *args):
        """
        Submit a job and return the job ID
        """
        job_id = 1

        template = self.env.get_template("job_template.xml")
        jsdl = template.render({
            "name": "ARC job",  # TODO: Use sensible name or omit
            "executable": executable,
            "arguments": args
        })
        print("JSDL for job is:")
        print(jsdl)

        print("Started job {}".format(job_id))
        return job_id

    def get_job_status(self, job_id):
        """
        Return the status of the given job
        """
        return JOB_STATUSES.COMPLETED

    def cancel_job(self, job_id):
        """
        Cancel the given job
        """
        print("Cancelling job {}".format(job_id))

    def save_job_outputs(self, job_id, output_path=None, errors_path=None):
        """
        Retrieve the output and errors files for a job and save them to the paths given
        """
        if output_path:
            print("Saving output file to '{}'".format(output_path))

        if errors_path:
            print("Saving errors file to '{}'".format(errors_path))


