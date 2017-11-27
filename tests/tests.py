import unittest
import os
import subprocess
import json
import tempfile

from jasmin_arc.arc_interface import ArcInterface
from jasmin_arc.exceptions import InvalidConfigError, ProxyGenerationError, JobNotFoundError
from base import ArcTestCase


# Lots of tests create temp files/directories, so put them in a common directory
# that can be deleted at the end
BASE_TEMP_DIR = tempfile.mkdtemp()


class JasminArcTests(ArcTestCase):

    def test_invalid_config(self):
        """
        Test that providing an invalid config file raises the expected exception
        """
        filename = None
        with tempfile.NamedTemporaryFile(delete=False, dir=BASE_TEMP_DIR) as config_file:
            filename = config_file.name
            config_file.write("this is not valid JSON!")

        with self.assertRaises(InvalidConfigError):
            a = ArcInterface(filename)

    def test_proxy_generation_failure(self):
        """
        Test that using a non-existent key file raises the expected exception
        """
        filename = None
        with tempfile.NamedTemporaryFile(delete=False, dir=BASE_TEMP_DIR) as config_file:
            filename = config_file.name
            json.dump({"CLIENT_KEY": "/tmp/nonexistentfile"}, config_file)

        a = ArcInterface(filename)
        with self.assertRaises(ProxyGenerationError):
            a.submit_job("/bin/echo")

    def test_invalid_job_id(self):
        """
        Attempt to retrieve job status using an invalid ID, and check the expected exception is
        raised
        """
        self.assertRaises(JobNotFoundError, self.ARC_INTERFACE.get_job_status, "invalid ID here")

    def test_proxy_renewal(self):
        """
        Test that the proxy file is automatically renewed when it comes close to its expiry time
        """
        a = self.ARC_INTERFACE
        n = 60
        a.config.PROXY_VALIDITY_PERIOD = n
        a.config.PROXY_RENEWAL_THRESHOLD = n - 3

        # Delete proxy if it exists from previous tests
        if os.path.isfile(a.config.PROXY_FILE):
            os.unlink(a.config.PROXY_FILE)

        # Create initial proxy and save creation time
        a.get_user_config()
        t1 = os.path.getmtime(a.config.PROXY_FILE)
        # Wait till after proxy should be renewed
        self.wait(5)
        a.get_user_config()
        # Check proxy file has been modified
        t2 = os.path.getmtime(a.config.PROXY_FILE)
        self.assertTrue(t2 > t1)


class JobSubmissionTests(ArcTestCase):

    # Set how long to wait for different types of job to finish
    BASIC_SUBMISSION_TIMEOUT = 10
    INPUT_FILE_SUBMISSION_TIMEOUT = 120

    def get_output_file_contents(self, job_id, filename):
        """
        Save job outputs, read a specified file, and return the contents as a string
        """
        a = self.ARC_INTERFACE
        out_dir = a.save_job_outputs(job_id)
        # Check files were downloaded
        self.assertTrue(out_dir is not None)

        # Check file exists
        local_filename = os.path.join(out_dir, filename)
        self.assertTrue(os.path.isfile(local_filename))

        # Return contents
        with open(local_filename) as f:
            return f.read()

    def test_basic_submission(self):
        """
        Submit a job basic job with no input or output files
        """
        a = self.ARC_INTERFACE
        message = "hello!"
        job_id = a.submit_job("/bin/echo", [message])
        self.wait(self.BASIC_SUBMISSION_TIMEOUT)
        stdout = self.get_output_file_contents(job_id, "stdout.txt")
        self.assertEqual(stdout.strip(), message)

    def test_get_status(self):
        """
        Submit a job and check that its status can be retrieved
        """
        a = self.ARC_INTERFACE
        job_id = a.submit_job("/bin/ls")
        try:
            status = a.get_job_status(job_id)
        except Exception as ex:
            self.fail(ex)

    def test_output_files(self):
        """
        Submit a job that writes and output file, and check that is it downloaded successfully
        """
        a = self.ARC_INTERFACE
        message = "my message here"
        outfile = "outfile.txt"
        a.config.OUTPUT_FILE = outfile
        job_id = a.submit_job("/bin/bash", ["-c", "echo '{}' > {}".format(message, outfile)])
        self.wait(self.BASIC_SUBMISSION_TIMEOUT)
        outfile_contents = self.get_output_file_contents(job_id, outfile)
        self.assertEqual(outfile_contents.strip(), message)

    def test_input_files(self):
        """
        Create some input files, submit a job that calls `find`, and verify the input files are
        shown in the output
        """
        a = self.ARC_INTERFACE
        n = 2
        format_str = "test_file_{}"
        input_files = []
        temp_dir = tempfile.mkdtemp(dir=BASE_TEMP_DIR)

        # Make some temp files
        for i in range(n):
            filename = os.path.join(temp_dir, format_str.format(i))
            input_files.append(filename)
            with open(filename, "w") as f:
                f.write("hello")

        # Submit a job with the input files - list files in session directory on stdout
        job_id = a.submit_job("/bin/find", args=[], input_files=input_files)
        self.wait(self.INPUT_FILE_SUBMISSION_TIMEOUT)

        # Read stdout and check each input file is present
        stdout = self.get_output_file_contents(job_id, "stdout.txt")
        lines = stdout.split("\n")
        for i in range(n):
            self.assertIn("./" + format_str.format(i), lines)


if __name__ == "__main__":
    unittest.main()
    subprocess.call("rm", ["-r", BASE_TEMP_DIR])
