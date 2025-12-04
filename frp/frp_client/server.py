from http.server import HTTPServer, BaseHTTPRequestHandler

class HelloHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 设置响应状态码
        self.send_response(200)
        # 设置响应头
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        # 返回Hello World
        self.wfile.write(b'Hello World')

if __name__ == '__main__':
    server_address = ('0.0.0.0', 8000)
    httpd = HTTPServer(server_address, HelloHandler)
    print("服务器运行在 http://localhost:8000")
    httpd.serve_forever()
