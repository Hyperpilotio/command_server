import socket
from threading import Thread
from subprocess import Popen, PIPE
import SocketServer
import sys
import os
import json

class UnixSocketServer(SocketServer.ThreadingMixIn, SocketServer.UnixStreamServer):
    pass

class TCHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(2048)
        try:
            request = json.loads(data)
            command = request["command"]
            exitcode, stdout, stderr = self.run_command(command)
            self.request.sendall(json.dumps({"exitcode": exitcode, "stdout": stdout, "stderr": stderr}))
        except Exception as e:
            self.request.sendall(json.dumps({"exitcode": 123, "stdout": "", "stderr": str(e)}))

    def run_command(self, command):
        process = Popen(command, shell=True, executable="/bin/bash", stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        return (process.returncode, stdout, stderr)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Unable to find arguments"
        sys.exit(-1)

    server_address = sys.argv[1]
    try:
        os.unlink(server_address)
    except OSError:
        if os.path.exists(server_address):
            raise

    server = UnixSocketServer(server_address, TCHandler)
    print "Starting to run tc server"
    server.serve_forever()
