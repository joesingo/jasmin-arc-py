with open("/tmp/f1.txt", "w") as f1:
    f1.write("This is file 1... ")

with open("/tmp/f2.txt", "w") as f2:
    f2.write("And this is file 2")

arc_iface.submit_job("/bin/bash", args=["-c", "cat *.txt"],
                     input_files=["/tmp/f1.txt", "/tmp/f2.txt"])
