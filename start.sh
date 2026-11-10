#!/usr/bin/env sh
# 静读 · macOS / Linux 启动脚本
# 用法：  chmod +x start.sh && ./start.sh
cd "$(dirname "$0")" || exit 1

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done

if [ -z "$PY" ]; then
  echo
  echo "  这台电脑没找到 Python 3。"
  echo "  阅读器本身不需要 Python，可以直接用浏览器打开："
  echo "      静读阅读器.html"
  echo "  但这样浏览器可能读不到同目录的书；已导入过的书仍能读。"
  echo
  exit 1
fi

exec "$PY" 启动器.py
