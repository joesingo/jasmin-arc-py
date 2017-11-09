"""
arc_iface.py
============

Interface functions to ARC CE python client.

"""

# Standard library imports
import os
import time

# Local imports
from arcapp.models import *
from arcapp.vocabs import STATUS_VALUES
from arcproj.settings import OUTPUTS_DIR

# Import ARC CE library
from jasmin_arc import arclib


# Location of wrapper script
JOB_FILES_DIR = "/tmp/arc-app/job_files"

if not os.path.isdir(JOB_FILES_DIR):
    os.makedirs(JOB_FILES_DIR)


def submit_job(job_id, executable, *arguments, **kwargs):
    """
    Submit a job to ARC CE.

    :param job_id: string (local job id)
    :param executable: path to executable
    :param *arguments: list of arguments (interpreted as strings) starting with main script path.
    :param **kwargs (can include input_file_path: path to an input file to provide as input to process.)

    :returns: tuple of (STATUS_VALUE, job_id|False)
    """
#    if kwargs.has_key("input_file_path"):
#        raise NotImplementedError

    job_file_path = os.path.join(JOB_FILES_DIR, "job_{0}.jsdl".format(job_id))

    arclib.write_job_file(job_file_path, executable, arguments)

    job_id = arclib.submit_job(job_file_path)

    if not job_id:
       return STATUS_VALUES.FAILED, False

    return STATUS_VALUES.IN_PROGRESS, job_id


def _map_arc_status(status):
    "Maps ARC status to local app status."
    if status: status == status.lower().strip()

    if not status or status == 'failed':
        return STATUS_VALUES.FAILED
    elif status != arclib.ARC_FINISHED_STATUS:
        return STATUS_VALUES.IN_PROGRESS
    else:
        return STATUS_VALUES.COMPLETED


def _cache_outputs_on_disk(remote_job_id, job_id):
    """
    Save the outputs to disk if not already saved.

    :param remote_job_id [string]
    :param job_id [string]
    :return: boolean (True if saved; False if already saved).
    """
    output_path = "{0}/{1}/outputs.zip".format(OUTPUTS_DIR, job_id)

    if os.path.isfile(output_path):
        return False

    dr = os.path.dirname(output_path)
    if not os.path.isdir(dr):
        os.mkdir(dr)

    arclib.save_responses(remote_job_id, output_path)
    return True


def get_arc_job_status(remote_job_id, job_id):
    """
    Get remote job details from ARC CE. If the job status is COMPLETED then
    download outputs if not already retrieved.

    :param remote_job_id (string): remote (ARC) job ID.
    :param job_id (string): local job ID.
    :return: tuple of (STATUS_VALUE, <dict_of_results>|None)
    """
    job = Job.objects.get(job_id=job_id)
    download_url = "/download/{0}/".format(job_id)

    if job.status == STATUS_VALUES.COMPLETED:
        return job.status, {"output_path_uri": download_url}

    # If status is not COMPLETED then talk to ARC server
    job_status = arclib.get_job_status(remote_job_id)

    status = _map_arc_status(job_status)
    if status == STATUS_VALUES.COMPLETED:
        _cache_outputs_on_disk(remote_job_id, job_id)

    return status, {"output_path_uri": download_url}
