import unittest
import os
import sys
import subprocess
import json
import tempfile
import time

from jasmin_arc.arc_interface import ArcInterface
from jasmin_arc.exceptions import InvalidConfigError, ProxyGenerationError
from base import ArcTestCase


# Lots of tests create temp files/directories, so put them in a common directory
# that can be deleted at the end
BASE_TEMP_DIR = tempfile.mkdtemp()


class ValidationTests(unittest.TestCase):
    """
    Test things in ArcInterface related to validation
    """

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
            json.dump({"PEM_FILE": "/tmp/nonexistentfile"}, config_file)

        a = ArcInterface(filename)
        with self.assertRaises(ProxyGenerationError):
            a.submit_job("/bin/echo")


class JobSubmissionTests(ArcTestCase):

    # Set how long to wait for different types of job to finish
    BASIC_SUBMISSION_TIMEOUT = 10
    INPUT_FILE_SUBMISSION_TIMEOUT = 120

    def wait(self, n):
        sys.stdout.write("Waiting for {} seconds".format(n))
        for _ in range(n):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\n")

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

    def test_output_files(self):
        """
        Submit a job that writes and output file, and check that is it downloaded successfully
        """
        a = self.ARC_INTERFACE
        message = "my message here"
        outfile = "outfile.txt"
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


if __name__ == "__main__":
    unittest.main()
    subprocess.call("rm", ["-r", BASE_TEMP_DIR])
