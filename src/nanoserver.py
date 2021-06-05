from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from io import BytesIO
import sys


class NanoRequestHandler(SimpleHTTPRequestHandler):

    _legal_path = [
        "/tree.json",
        "src/tree.json",
    ]

    def do_POST(self):
        print(f'Address: {self.address_string()}')
        print(f'Request: {self.requestline}')
        print(f'Path: {self.path}')
        print(f'Headers:\n{self.headers}')
        self.send_response(200)
        self.end_headers()

        if self.path in NanoRequestHandler._legal_path:
            path = self.translate_path(self.path)
            content_length = int(self.headers.get('Content-Length'))
            body = self.rfile.read(content_length)
            with open(path, 'wb') as f:
                f.write(body)


httpd = ThreadingHTTPServer(('0.0.0.0', 8000), NanoRequestHandler)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nKeyboard interrupt received, exiting.")
    sys.exit(0)
