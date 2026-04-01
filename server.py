#!/usr/bin/env python3
import http.server
import os

os.chdir("/home/noahs/meridian")

handler = http.server.SimpleHTTPRequestHandler
server = http.server.HTTPServer(("0.0.0.0", 8090), handler)
print("Serving Meridian on http://0.0.0.0:8090")
server.serve_forever()
