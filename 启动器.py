import glob
import json
import os
import shutil
import socket
import subprocess
import sys
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(ROOT, 'static')
# 本目录下的书数据文件，形如 xxx_静读书目.json（仓库里不含书，放进去就会自动导入）
BOOK_GLOB = '*_静读书目.json'
PORT = 8765
URL = 'http://127.0.0.1:%d/' % PORT


def log(msg):
    print(msg, flush=True)


def find_book():
    """在本目录找 *_静读书目.json；有多个时选最新的那个。"""
    hits = [p for p in glob.glob(os.path.join(ROOT, BOOK_GLOB)) if os.path.isfile(p)]
    if not hits:
        return None
    return max(hits, key=os.path.getmtime)


def sync_static():
    """把本目录的阅读器和书同步到 static/，这样换目录、更新文件都不会过期。"""
    os.makedirs(os.path.join(STATIC, 'books'), exist_ok=True)
    reader = os.path.join(ROOT, '静读阅读器.html')
    if os.path.exists(reader):
        shutil.copyfile(reader, os.path.join(STATIC, 'index.html'))
    payload = find_book()
    if payload:
        target = os.path.join(STATIC, 'book.json')
        if not os.path.exists(target) or os.path.getmtime(payload) > os.path.getmtime(target):
            shutil.copyfile(payload, target)


def port_in_use():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        return s.connect_ex(('127.0.0.1', PORT)) == 0
    finally:
        s.close()


def open_browser():
    candidates = [
        os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'), 'Google', 'Chrome', 'Application', 'chrome.exe'),
        os.path.join(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'), 'Google', 'Chrome', 'Application', 'chrome.exe'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'Application', 'chrome.exe'),
        os.path.join(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'), 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
        os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'), 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
    ]
    if sys.platform == 'darwin':
        candidates = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    elif not sys.platform.startswith('win'):
        candidates = ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser']
    for p in candidates:
        if os.path.exists(p):
            try:
                subprocess.Popen([p, '--new-window', URL], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, start_new_session=True)
                return p
            except Exception:
                continue
    webbrowser.open(URL)
    return '默认浏览器'


def pause(message='按回车退出…'):
    """双击运行时让窗口停一下，否则报错一闪就没了。非交互环境直接返回。"""
    try:
        if sys.stdin and sys.stdin.isatty():
            input(message)
    except Exception:
        pass


def main():
    os.makedirs(STATIC, exist_ok=True)
    try:
        sync_static()
    except Exception as err:
        log('同步文件时出错（不影响阅读）：%s' % err)

    if not os.path.exists(os.path.join(STATIC, 'index.html')):
        log('找不到阅读器页面，请确认文件夹完整后重新运行。')
        pause()
        return 1

    log('=' * 52)
    log('  静读 · 本地书架    %s' % URL)
    log('  阅读期间请保持这个窗口开着，读完关掉即可。')
    if not find_book():
        log('  没有找到 *_静读书目.json，阅读器会用空书架启动，')
        log('  把 TXT 拖进窗口就能导入自己的书。')
    log('=' * 52)

    if port_in_use():
        log('%s 已经在运行，直接打开浏览器。' % URL)
        open_browser()
        return 0

    log('正在用 %s 打开页面…' % open_browser())

    from importlib import util
    spec = util.spec_from_file_location('jingdu_server', os.path.join(ROOT, '书架服务器.py'))
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        server = module.Server(('127.0.0.1', PORT), module.Handler)
    except OSError as err:
        log('启动失败：端口 %d 被占用（%s）。可把本文件里的 8765 改成 8766。' % (PORT, err))
        pause()
        return 1

    log('服务已就绪。按 Ctrl+C 或关掉本窗口即停止。')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        log('已停止。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
