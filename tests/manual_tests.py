import sys
import os
import unittest
import tempfile
from datetime import datetime

from jasmin_arc import ArcInterface


ARC_INTERFACE = None


class ManualTests(unittest.TestCase):
    """
    Perform tests that require some element of manual input, e.g. logging in to JASMIN to check
    when a job has finished.

    These tests could become fully automated if/when ARC job status changes to 'completed' as soon
    as job actually finishes.
    """

    def get_output_file_contents(self, job_id, filename):
        """
        Save job outputs, read a specified file, and return the contents as a string
        """
        a = ARC_INTERFACE
        out_dir = a.save_job_outputs(job_id)
        with open(os.path.join(out_dir, filename)) as f:
            return f.read()

    def wait_for_completion(self, msg=None, extra=None):
        sub_time = datetime.now().strftime("%H:%M")
        if not msg:
            msg = ("Take note of submission time (~{}) and monitor job progress with `bjobs -a` on "
                   "JASMIN. Press return when job finishes".format(sub_time))
        print("")
        print(msg)
        if extra:
            print(extra)

        x = raw_input()

    def test_basic_submission(self):
        """
        Submit a job basic job with no input or output files
        """
        a = ARC_INTERFACE
        message = "hello!"
        job_id = a.submit_job("/bin/bash", ["-c", "echo '{}'".format(message)])

        self.wait_for_completion()
        stdout = self.get_output_file_contents(job_id, "stdout.txt")
        self.assertEqual(stdout.strip(), message)

    def test_output_files(self):
        """
        Submit a job that writes and output file, and check that is it downloaded successfully
        """
        a = ARC_INTERFACE
        message = "my message here"
        outfile = "outfile.txt"
        job_id = a.submit_job("/bin/bash", ["-c", "echo '{}' > {}".format(message, outfile)])
        self.wait_for_completion()

        out_dir = a.save_job_outputs(job_id)
        local_outfile = os.path.join(out_dir, outfile)
        self.assertTrue(os.path.isfile(local_outfile))

        with open(local_outfile) as f:
            self.assertEqual(f.read().strip(), message)

    def test_input_files(self):
        """
        Create some input files, submit a job that calls `find`, and verify the input files are
        shown in the output
        """
        a = ARC_INTERFACE

        n = 2
        format_str = "test_file_{}"

        input_files = []
        temp_dir = tempfile.mkdtemp()

        # Make some temp files
        for i in range(n):
            filename = os.path.join(temp_dir, format_str.format(i))
            input_files.append(filename)
            with open(filename, "w") as f:
                f.write("hello")

        # Submit a job with the input files - list files in session directory on stdout
        job_id = a.submit_job("/bin/bash", ["-c", "find ."], input_files)
        self.wait_for_completion("Note: It can take some time before job actually starts on LOTUS "
                                 "when copying across input files")

        # Read stdout...
        stdout = self.get_output_file_contents(job_id, "stdout.txt")
        lines = stdout.split("\n")
        # ...and check each input file is present
        for i in range(n):
            self.assertIn("./" + format_str.format(i), lines)

    def test_cancel_job(self):
        """
        Submit a long-running job, cancel is, and check that the job is actually cancelled
        """
        a = ARC_INTERFACE
        # Submit a job that would take a very long to finish
        script = "seq 1 10000 | while read x; do echo '$x'; sleep 1; done"
        job_id = a.submit_job("/bin/bash", ["-c", script])
        self.wait_for_completion(msg="Press return when job has started (run `bjobs` on JASMIN "
                                     "to see running jobs)")
        a.cancel_job(job_id)
        answer = None
        while answer not in ("y", "n"):
            print("Has job been cancelled successfully? (y/n)")
            answer = raw_input()

        if answer == "n":
            self.fail("Job not cancelled")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("Path to config file required\n")
        sys.exit(1)

    ARC_INTERFACE = ArcInterface(sys.argv[1])
    argv = [sys.argv[0]] + sys.argv[2:]
    unittest.main(argv=argv)
