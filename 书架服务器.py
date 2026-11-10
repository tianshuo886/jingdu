"""
静读 · 本地书架服务器（只用 Python 标准库，不上传任何内容）
运行后在本机 http://127.0.0.1:8765/ 打开阅读器。
把 TXT 放进 static/books/ 文件夹，阅读器会在列表里显示出来。
"""
import http.server
import json
import os
import socketserver
import sys
import time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(ROOT, 'static')
BOOKS = os.path.join(STATIC, 'books')


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', '/index.html'):
            self.path = '/index.html'
            return super().do_GET()
        if path == '/api/books.json':
            return self.list_books()
        return super().do_GET()

    def list_books(self):
        items = []
        if os.path.isdir(BOOKS):
            for name in sorted(os.listdir(BOOKS)):
                if name.lower().endswith(('.txt', '.md')):
                    full = os.path.join(BOOKS, name)
                    st = os.stat(full)
                    items.append({'file': name, 'size': st.st_size, 'mtime': int(st.st_mtime)})
        body = json.dumps({'books': items}, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        if '/api/books.json' in (self.path or ''):
            return
        sys.stderr.write('[%s] %s\n' % (time.strftime('%H:%M:%S'), fmt % args))


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == '__main__':
    os.makedirs(BOOKS, exist_ok=True)
    with Server(('127.0.0.1', PORT), Handler) as httpd:
        print('静读书架已启动： http://127.0.0.1:%d/' % PORT)
        print('把 TXT 放进 static/books/ 即可作为备选书源；Ctrl+C 停止。')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
