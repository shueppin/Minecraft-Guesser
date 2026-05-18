"""
This is a testing server to display the website locally.

Just run "python test_server.py" in terminal. 
The standard instance of Python should have all the needed libraries.
"""


from http.server import BaseHTTPRequestHandler, HTTPServer

class TestServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        try:
            # Open the requested file and serve the content
            file_to_open = open(self.path[1:], 'rb').read()
            self.send_response(200)
        except:
            # If the file is not found, return a 404 error
            file_to_open = b'File not found!'
            self.send_response(404)

        self.end_headers()
        self.wfile.write(file_to_open)

def run(server_class=HTTPServer, handler_class=TestServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()