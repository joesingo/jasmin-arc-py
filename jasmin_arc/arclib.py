"""
arclib.py
=============

Script for end-to-end testing of ARC CE client in python.

"""
import arc
import sys
import subprocess
import urllib
import time
import httplib
import urllib2
import re
import os
import logging

logging.basicConfig()
log = logging.getLogger('__name__')
log.setLevel(logging.DEBUG)

# Get linux USER
USER = 'user1' # os.environ["USER"]

# CERTIFICATE-related files
PEM_FILE = '/home/{0}/.arc/userkey-nopass.pem'.format(USER)
CLIENT_CERT_FILE = '/home/{0}/.arc/usercert.pem'.format(USER)
BROWSER_CERT_FILE = '/home/{0}/certBundle.p12'.format(USER)
CERTS_DIR = '/etc/grid-security/certificates'

# Command-line scripts
ARC_PROXY_CMD = '/usr/bin/arcproxy'
MYPROXY_FILE = '/tmp/x509up_u502'

# ARC Server
JASMIN_ARC_SERVER = 'jasmin-ce.ceda.ac.uk:60000/arex'
ARC_FINISHED_STATUS = 'Finished'

# Job file template
JSDL_TEMPLATE = """<JobDefinition
 xmlns="http://schemas.ggf.org/jsdl/2005/11/jsdl"
 xmlns:posix="http://schemas.ggf.org/jsdl/2005/11/jsdl-posix">
 <JobDescription>
   <JobIdentification>
     <JobName>Example job</JobName>
   </JobIdentification>
   <Application>
     <posix:POSIXApplication>
       <posix:Executable>{executable}</posix:Executable>
__INSERT_ARGS_HERE__
       <posix:Output>outputs.zip</posix:Output>
       <posix:Error>errors.txt</posix:Error>
     </posix:POSIXApplication>
   </Application>
   </JobDescription>
</JobDefinition>"""

# Job files
OUTPUTS_FILE = "outputs.zip"
ERRORS_FILE = "errors_file.txt"


class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    "Basic HTTPS Auth handler for requests."

    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)


def create_myproxy_config():
    """
    Create a user proxy file name for myproxy using a passwordless userkey.pem.
    :return: ARC UserConfig instance.
    """
    subprocess.check_call(ARC_PROXY_CMD, universal_newlines=True)

    # Create a UserConfig object with the user's proxy
    uc = arc.UserConfig()

    if not os.path.isfile(MYPROXY_FILE):
        raise Exception("Myproxy x509 certificate is required, cannot find at: {0}".format(MYPROXY_FILE))

    uc.ProxyPath(MYPROXY_FILE)

    # Add the path of the trusted CA certificates
    uc.CACertificatesDirectory(CERTS_DIR)
    return uc


def get_retriever(uc, endpoints):
    """
    Returns retriever object after waiting for responses.

    :param uc: ARC UserConfig instance.
    :param endpoints: Endpoints to contact.
    :return: ARC ComputingServiceRetriever instance.
    """
    # Create retriever instance with required endpoints
    retriever = arc.ComputingServiceRetriever(uc, endpoints)

    log.debug('ComputingServiceRetriever created with the following endpoints:')
    for endpoint in endpoints:
        log.debug('Enpoint: {0}'.format(endpoint.str()))

    log.debug('Waiting for results')
    retriever.wait()
    return retriever


def download_file(url, filepath):
    'Download a file from `url` and save to `filepath`.'
    getter = urllib.URLopener()
    getter.retrieve(url, filepath)


def discover_compute_services():
    'Discovers compute services available and reports to terminal. Returns None.'
    uc = create_myproxy_config()
    registries = [arc.Endpoint("jasmin-ce.ceda.ac.uk:2135/Mds-Vo-name=local,o=grid",
                               arc.Endpoint.REGISTRY, "org.nordugrid.ldapegiis")]
    reg_retriever = get_retriever(uc, registries)

    # The retriever acts as a list containing all the discovered ComputingServices:
    print "Discovered ComputingServices: ", ", ".join([service.Name for service in reg_retriever])

    # Query the local infosys (COMPUTINGINFO) of computing elements
    computing_elements = [arc.Endpoint("jasmin-ce.ceda.ac.uk", arc.Endpoint.COMPUTINGINFO,
                                       "org.nordugrid.ldapglue2")]
    ce_retriever = get_retriever(uc, computing_elements)
    targets = ce_retriever.GetExecutionTargets()

    print "The discovered ExecutionTargets:"
    for target in targets:
        print "\t", target

    # Query both registries and computing elements at the same time:
    endpoints = [arc.Endpoint("jasmin-ce.ceda.ac.uk/O=Grid/Mds-Vo-Name=local", arc.Endpoint.REGISTRY),
                 arc.Endpoint("jasmin-ce.ceda.ac.uk", arc.Endpoint.COMPUTINGINFO, "org.nordugrid.ldapglue2")]
    both_retriever = get_retriever(uc, endpoints)
    
    print "Discovered ComputingServices:", ", ".join([service.Name for service in both_retriever])

    
def submit_job(job_file_path):
    """
    Submit a job to the server using ARC CE.

    :param job_file_path: Path to the JDSL job file.
    :return: Job ID (string) or False (if job failed).
    """
    # Set up logging
    arc_logger = arc.LogStream(sys.stdout)
    arc.Logger_getRootLogger().addDestination(arc_logger)
    arc.Logger_getRootLogger().setThreshold(arc.ERROR)

    uc = create_myproxy_config()
    # Create an endpoint for a Computing Element
    endpoint = arc.Endpoint(JASMIN_ARC_SERVER, arc.Endpoint.COMPUTINGINFO)
   
    # Get the ExecutionTargets of this ComputingElement
    retriever = arc.ComputingServiceRetriever(uc, [endpoint])
    retriever.wait()
    targets = retriever.GetExecutionTargets()    
      
    # Create a list containing the Job Descriptions and parse job file
    job_descriptions = arc.JobDescriptionList()
    arc.JobDescription_ParseFromFile(job_file_path, job_descriptions)

    # Create a Job object and then submit
    # create an empty job object which will contain our submitted job
    job = arc.Job()

    # Submit job directly to the execution targets, without a broker
    # Try each target until successfully submitted.
    for target in targets:
        log.debug('Submitting to: {0} ({1})'.format(target.ComputingEndpoint.URLString,
                                                    target.ComputingEndpoint.InterfaceName))
        success = target.Submit(uc, job_descriptions[0], job)

        if success:
            log.debug("Job submitted details: {0}".format(job.JobID))
            break
        else:
            log.warn('Failed')
    else:
        return False

    return job.JobID


def get_job_status(job_id):
    """
    Get job status string from job ID.
    If job not found log warning and return False.

    :param job_id: string
    :return: job status: string
    """
    uc = create_myproxy_config()

    # Create a JobSupervisor to handle all the jobs
    job_supervisor = arc.JobSupervisor(uc)

    # Retrieve all the jobs from this computing element
    endpoint = arc.Endpoint('https://{0}'.format(JASMIN_ARC_SERVER), arc.Endpoint.JOBLIST)
    retriever = arc.JobListRetriever(uc)
    retriever.addConsumer(job_supervisor)
    retriever.addEndpoint(endpoint)
    retriever.wait()

    # Update the states of the jobs
    job_supervisor.Update()

    # Get all jobs and find job by ID
    jobs = job_supervisor.GetAllJobs()

    for job in jobs:
        if job_id == job.JobID:
            return job.State.GetGeneralState()

    log.warn('Job status not found for ID: {0}'.format(job_id))
    return False


def save_responses(job_id, output_zip_path, output_stderr_path=None):
    """
    Retrieve responses (output and stderr (if set)) from server and
    save to local files.

    :param job_id [string]
    :param output_zip_path [string]
    :param output_stderr_path [string]
    :return: None
    """
    # Get HTTPS handler to talk to service
    opener = urllib2.build_opener(HTTPSClientAuthHandler(PEM_FILE, CLIENT_CERT_FILE))
    response = opener.open(job_id)
    page = response.read()

    outputs_file_uri = re.split('"', page)[1]
    errors_file_uri =  re.split('"', page)[3]

    log.info('Retrieving results...')
    with open(output_zip_path, 'wb') as res_writer:
        res_writer.write(opener.open(outputs_file_uri).read())

    if output_stderr_path:
        log.info('Retrieving errors (if any)...')
        with open(output_stderr_path, 'w') as err_writer:
            err_writer.write(opener.open(errors_file_uri).read())


def get_job_response(job_id, show_full=False):
    """
    Returns tuple of string contents of (results, errors).
    :param job_id:
    :param show_full: boolean - log full response if True
    :return: None
    """
    # Get HTTPS handler to talk to service
    opener = urllib2.build_opener(HTTPSClientAuthHandler(PEM_FILE, CLIENT_CERT_FILE))
    response = opener.open(job_id)
    page = response.read()

    if show_full:
        log.info("Full response:\n{0}\n".format(page))

    results_file = re.split('"', page)[1]
    errors_file =  re.split('"', page)[3]

    log.info('Retrieving results...')
    with open(OUTPUTS_FILE, 'wb') as res_writer:
        res_writer.write(opener.open(results_file).read())

    log.info('Retrieving errors (if any)...')
    with open(ERRORS_FILE, 'w') as err_writer:
        err_writer.write(opener.open(errors_file).read())


def write_job_file(job_file_path, executable_location, arguments):
    """
    Writes a job file and return True if successful.
    Exception if unsuccessful.

    :param job_file_path: file path
    :param executable_location: file path
    :param arguments: list of command line arguments.
    :return: Success (boolean).
    """
    job_desc = JSDL_TEMPLATE.format(executable=executable_location)
    INSERT_STRING = '__INSERT_ARGS_HERE__\n'

    if not arguments:
        REPLACE_STRING = ''
    else:
        REPLACE_STRING = '\n'.join(['<posix:Argument>{0}</posix:Argument>'.format(arg) for arg in arguments]) + '\n'

    job_desc = job_desc.replace(INSERT_STRING, REPLACE_STRING)

    # Now write the file
    with open(job_file_path, 'w') as writer:
        writer.write(job_desc)

    return True


def main():
    'Main script controller.'
#    discover_compute_services()

    job_file_path = "test_job.jsdl"
    executable = "wrap_job.sh"
    arguments = ['/group_workspaces/jasmin/cedaproc/arc_ce_test/ceda-arc-app/scripts/wrap_diff_nc_era.sh',
                 'tas', '1999-01-01T00:00:00']
    write_job_file(job_file_path, executable, arguments)

    job_id = submit_job(job_file_path)
    if not job_id:
       log.warn('Failed to submit job.')
       return

    log.info('Submitted job with ID: {0}'.format(job_id))

    while True:
        job_status = get_job_status(job_id)
        log.debug('Checking Job Status: {0}'.format(job_status))

        if job_status == ARC_FINISHED_STATUS:
            log.info('Job finished!')
            break

        log.debug('Sleeping for 10 seconds...')
        time.sleep(20)
 
    resp = get_job_response(job_id)


if __name__ == "__main__":


    args = sys.argv[1:]
    if args:
        print get_job_status(args[0])
        get_job_response(args[0], show_full=True)
    else:
        main()

