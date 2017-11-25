import unittest

from base import ArcTestCase


class ManualTests(ArcTestCase):
    """
    Perform tests that require some element of manual input, e.g. logging in to JASMIN to check
    the status of a job.

    These tests could become fully automated if/when ARC job status changes when job status changes
    in LSF (currently there is a big time delay).
    """

    def test_cancel_job(self):
        """
        Submit a long-running job, cancel is, and check that the job is actually cancelled
        """
        a = self.ARC_INTERFACE
        # Submit a job that would take a very long to finish
        script = "seq 1 10000 | while read x; do echo '$x'; sleep 1; done"
        job_id = a.submit_job("/bin/bash", ["-c", script])

        print("")
        print("Press return when job has started (run `bjobs -a` on JASMIN to see running jobs)")
        raw_input()

        a.cancel_job(job_id)
        answer = None
        while answer not in ("y", "n"):
            print("Has job been cancelled successfully? (y/n)")
            answer = raw_input()

        if answer == "n":
            self.fail("Job not cancelled")


if __name__ == "__main__":
    unittest.main()
