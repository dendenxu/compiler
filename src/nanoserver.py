from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from io import BytesIO
import sys
import json
import urllib


class NanoRequestHandler(SimpleHTTPRequestHandler):

    _legal_path = [
        "/tree.json",
        "/src/tree.json",
    ]

    def do_POST(self):
        try:
            print(f'Address: {self.address_string()}')
            print(f'Request: {self.requestline}')
            print(f'Path: {self.path}')
            print(f'Headers:\n{self.headers}')

            if self.path in NanoRequestHandler._legal_path:
                path = self.translate_path(self.path)
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                print(f"Got payload {body}")
                body = json.loads(body.decode('utf-8'))
                body["address"] = self.address_string()
                body = json.dumps(body).encode('utf-8')
                with open(path, 'wb') as f:
                    f.write(body)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(f"POST request for {self.path}".encode('utf-8'))
                print(f"Response Sent")
                return
            raise Exception("Unsupported file type or filename")
        except Exception as e:
            self.send_error(404, f'{e}')
            print(sys.exc_info())


httpd = ThreadingHTTPServer(('0.0.0.0', 8000), NanoRequestHandler)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nKeyboard interrupt received, exiting.")
    sys.exit(0)