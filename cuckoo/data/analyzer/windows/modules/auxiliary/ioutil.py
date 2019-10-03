import os.path
import subprocess
import threading

from lib.common.abstracts import Auxiliary
from lib.common.results import upload_to_host

class ioutil(threading.Thread, Auxiliary):
    """Allow typeperf to be run on the side."""
    def __init__(self, options={}, analyzer=None):
        threading.Thread.__init__(self)
        Auxiliary.__init__(self, options, analyzer)

    def init(self):
        bin_path = os.path.join(self.analyzer.path, "bin")
        self.output = os.path.join(bin_path, "disk.csv")

    def start(self):

        config = ["\PhysicalDisk(0 C:)\Disk Read Bytes/sec",
                  "\PhysicalDisk(0 C:)\Disk Write Bytes/sec"]
        counters_string = ' '.join("\"%s\""%c for c in config)
        command = "typeperf -f CSV -y -o {o} {counters}".format(**{"o": self.output,
                                                                "counters": counters_string})
        # Start process monitor in the background.
        subprocess.Popen(command, shell="True")

    def stop(self):
        # Upload the CSV file to the host.
        upload_to_host(self.output, os.path.join("shots", "diskutil.csv"))
