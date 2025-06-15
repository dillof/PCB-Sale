import os
import sys


class Messages:
    def __init__(self):
        self.ok = True
        self.program = sys.argv[0]

    def error(self, message, file=None, line=None):
        self.ok = False
        self.print_message(message, None, file, line)
    
    def warning(self, message, file=None, line=None):
        self.print_message(message, "warning", file, line)
    
    def print_message(self, message, severity=None, file=None, line=None):
        if file is not None:
            preamble = file
            if line is not None:
                preamble += f":{line}"
        else:
            preamble = self.program
        if severity is not None:
            preamble += f": {severity}"
        print(f"{preamble}: {message}", file=sys.stderr)


messages = Messages()
