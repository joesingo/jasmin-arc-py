from .status import JOB_STATUSES


class ArcInterface(object):
    """
    Class to handle interactions with ARC-CE server
    """

    def __init__(self, config_path):
        print("Initialising api object using config at '{}'".format(config_path))

    def submit_job(self, *args, **kwargs):
        """
        Submit a job and return the job ID
        """
        job_id = 1
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
            print("Saving output file to '{}'".format(errors_path))


