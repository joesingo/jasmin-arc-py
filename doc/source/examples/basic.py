"""
Submit a job, wait till it completes, and print the stdout output
"""
import time
import os.path
from jasmin_arc import ArcInterface, JobStatuses

arc_iface = ArcInterface("/path/to/config.json")
job_id = arc_iface.submit_job("/bin/bash",
                              args=["-c", "echo 'This job is running on `/bin/hostname`'"])

while True:
    status = arc_iface.get_job_status(job_id)
    print("Job status is {}".format(status))

    if status == JobStatuses.COMPLETED:
       print("Job is finished!")
       break

    time.sleep(1)

out_dir = arc_iface.save_job_outputs(job_id)

if out_dir:
    print("Saved job outputs to {}".format(out_dir))
    print("stdout was:")
    with open(os.path.join(out_dir, "stdout.txt")) as stdout:
       print(stdout.read())
else:
    print("Error saving job outputs")
