from http.server import SimpleHTTPRequestHandler
import os


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to the HTTP response
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Origin, Content-Type, Accept, Authorization')
        super().end_headers()

    def translate_path(self, path):
        # Override translate_path to serve static files from the current working directory
        # This assumes that static files are served from the same directory as the script
        root = os.getcwd()
        return super().translate_path(path)


if __name__ == '__main__':
    from http.server import HTTPServer
    import sys

    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <port>')
        sys.exit(1)

    port = int(sys.argv[1])
    server_address = ('', port)

    try:
        httpd = HTTPServer(server_address, CORSRequestHandler)
        print(f'Starting CORS-enabled HTTP server on port {port}...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down the server')
        httpd.server_close()
