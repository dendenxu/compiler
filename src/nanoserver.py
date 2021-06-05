from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from io import BytesIO
import sys
import json


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
                content_length = int(self.headers['content-length'])
                body = self.rfile.read(content_length)
                print(f"Got payload {body}")
                body = json.loads(body.decode('utf-8'))
                body["address"] = self.address_string()
                body = json.dumps(body).encode('utf-8')
                with open(path, 'wb') as f:
                    f.write(body)

            self.send_response(200)
            self.end_headers()
            self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
            print(f"Sent response")
        except:
            self.send_error(404, "{}".format(sys.exc_info()[0]))
            print(sys.exc_info())


httpd = ThreadingHTTPServer(('0.0.0.0', 8000), NanoRequestHandler)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nKeyboard interrupt received, exiting.")
    sys.exit(0)
