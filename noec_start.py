import http.server
import threading
import sys
import noec_device_emulator
import asyncio
import noec_ws_server

PORT =8000
DIRECTORY = "d3frontend"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


def main( serial_device=None):
  if serial_device == None:
    use_emul = True
  else:
    use_emul = False
  httpd = http.server.HTTPServer(('localhost', 8000),Handler)
  thread_server = threading.Thread(target=httpd.serve_forever)
  thread_server.start()
  print("HTTP server started")
  if use_emul:
    devicefd,clientfd,serial_device =  noec_device_emulator.openEmulator()
  if use_emul:
    print("emulator started")
    thread_emul = threading.Thread(target=noec_device_emulator.startEmulator, args=(devicefd,clientfd,serial_device))
    thread_emul.start()
  asyncio.run(noec_ws_server.NOECWSServer((str(serial_device))))
  
  

if __name__ == "__main__":
  if len(sys.argv) > 1:
    main(sys.argv[1])
  else:
    main()
