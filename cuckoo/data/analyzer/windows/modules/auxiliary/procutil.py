import os.path
import subprocess
import threading
import time
import StringIO
import io

from lib.common.abstracts import Auxiliary
from lib.common.results import NetlogFile

TIMEOUT = 2

class procutil(threading.Thread, Auxiliary):
    """Allow procmon to be run on the side."""
    def __init__(self, options={}, analyzer=None):
        threading.Thread.__init__(self)
        Auxiliary.__init__(self, options, analyzer)

    def init(self):
        bin_path = os.path.join(self.analyzer.path, "bin")
        self.output = os.path.join(bin_path, "process.csv")

        # specify which process to capture perf counter for
        if self.options.has_key("process"):
            self.process = self.option.get("process")
        else:
            self.process = "*"

    def start(self):
        config = ["\Process({process})\ID Process",
                "\Process({process})\% Processor Time"]
        counters_string = ' '.join("\"%s\""%c.format(**{"process": self.process}) for c in config)
        command = "typeperf -f CSV -y -o {o} {counters}".format(**{"o": self.output,
                                                                "counters": counters_string})
        # Start process monitor in the background.
        subprocess.Popen(command, shell="True")

        while self.analyzer.do_run:
            time.sleep(TIMEOUT)

            with io.open(self.output) as f:
                tmpio = StringIO.StringIO(f.read())
                tmpio.seek(0)

                # now upload to host from the StringIO
                try:
                    nf = NetlogFile()
                    nf.init("shots/procutil.csv")

                    for chunk in tmpio:
                        nf.sock.sendall(chunk)
                finally:
                    nf.close()
