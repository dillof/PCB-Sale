import os
import sys


class Messages:
    def __init__():
        self.ok = True
        self.program = os.argv[0]

    def error(self, message, file=None, line=None):
        self.ok = False
        if file is not None:
            preamble = file
            if line is not None:
                preamble += f":{line}"
        else:
            preamble = self.program
        print(f"{preamble}: {message}", file=sys.stderr)

messages = Messages()
