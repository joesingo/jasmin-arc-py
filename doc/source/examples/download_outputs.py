###################
#   config.json   #
###################
{
    "OUTPUT_FILE": "output.txt",
    ...
}

#################
#   script.py   #
#################
import time
from jasmin_arc import ArcInterface, JobStatuses

arc_iface = ArcInterface("/path/to/config.json")

script = "echo 'This will be deleted' > myfile.txt;" + \
         "echo 'This will be downloaded' > output.txt;" + \
         "ls -l"
job_id = arc_iface.submit_job("/bin/bash", args=["-c", script])

# Wait for job to complete
while arc_iface.get_job_status(job_id) != JobStatuses.COMPLETED:
    time.sleep(1)

out_dir = arc_iface.save_job_outputs(job_id)
print("Outputs saved to {}".format(out_dir))

# The directory `out_dir' now contains 3 files - `output.txt', `stdout.txt' and
# `stderr.txt'. Checking the contents of `stdout.txt' we can see that when the
# job ran there were 4 files, but `myfile.txt' was deleted when the job ended.
