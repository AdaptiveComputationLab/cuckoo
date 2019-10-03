import os.path
import subprocess
import threading

from lib.common.abstracts import Auxiliary
from lib.common.results import upload_to_host

class procutil(threading.Thread, Auxiliary):
    """Allow procmon to be run on the side."""
    def __init__(self, options={}, analyzer=None):
        threading.Thread.__init__(self)
        Auxiliary.__init__(self, options, analyzer)

    def init(self):
        bin_path = os.path.join(self.analyzer.path, "bin")
        self.output = os.path.join(bin_path, "process.csv")
        self.interval = 2
        self.samples = 20

        # specify which process to capture perf counter for
        if self.options.has_key("process"):
            self.process = self.option.get("process")
        else:
            self.process = "*"

    def start(self):

        config = ["\Process({process})\ID Process",
                "\Process({process})\% Processor Time"]
        counters_string = ' '.join("\"%s\""%c.format(**{"process": self.process}) for c in config)
        command = "typeperf -si {si} -sc {sc} -f CSV -y -o {o} {counters}".format(**{"si": self.interval,
                                                                "sc": self.samples,
                                                                "o": self.output,
                                                                "counters": counters_string})
        # Start process monitor in the background.
        subprocess.Popen(command, shell="True")

    def stop(self):
        # Upload the CSV file to the host.
        upload_to_host(self.output, os.path.join("shots", "procutil.csv"))
