#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys
import json
from pathlib import Path
from urllib.parse import urlparse
import time

OUT_DIR = Path("/Volumes/M2/TT_Live_AI_TTS/20.1_输出文件_处理完成的音频文件")
INPUT_DIR = Path("/Volumes/M2/TT_Live_AI_TTS/18_批量输入_批量文件输入目录")

def estimate_targets() -> dict:
    # 预估每个 xlsx 目标数量：按每行一条，若不可读则默认 3200
    targets: dict[str, int] = {}
    try:
        import openpyxl  # optional
    except Exception:
        for x in INPUT_DIR.glob("*.xlsx"):
            targets[x.stem] = 3200
        return targets

    for x in INPUT_DIR.glob("*.xlsx"):
        try:
            wb = openpyxl.load_workbook(x, read_only=True)
            total = 0
            for ws in wb.worksheets:
                total += max(0, (ws.max_row or 0) - 1)
            targets[x.stem] = total if total > 0 else 3200
        except Exception:
            targets[x.stem] = 3200
    return targets

TARGETS_CACHE = estimate_targets()

def scan_progress() -> dict:
    data = {"updated_at": int(time.time()), "items": []}
    for xlsx_dir in sorted(OUT_DIR.glob("*")):
        if not xlsx_dir.is_dir():
            continue
        xname = xlsx_dir.name
        total_count = 0
        sheets = []
        for sheet_dir in sorted(xlsx_dir.glob("*")):
            if not sheet_dir.is_dir():
                continue
            count = len(list(sheet_dir.glob("*.mp3")))
            total_count += count
            sheets.append({"sheet": sheet_dir.name, "count": count})
        target = TARGETS_CACHE.get(xname, None)
        data["items"].append({
            "xlsx": xname,
            "count": total_count,
            "target": target,
            "sheets": sheets,
        })
    data["total_generated"] = sum(it["count"] for it in data["items"]) if data["items"] else 0
    data["total_target"] = sum((it.get("target") or 0) for it in data["items"]) if data["items"] else 0
    return data

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>TTS 生成进度看板</title>
  <meta http-equiv="refresh" content="5" />
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; margin: 20px; }
    h1 { font-size: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; font-size: 13px; }
    th { background: #f5f5f5; text-align: left; }
    .bar { height: 8px; background: #eaeaea; position: relative; }
    .bar > span { display: block; height: 100%; background: #4caf50; }
    .muted { color: #777; }
  </style>
  </head>
<body>
  <h1>TTS 生成进度看板</h1>
  <div id="meta"></div>
  <table>
    <thead>
      <tr><th>文件</th><th>已生成</th><th>目标</th><th>进度</th><th>工作表详情</th></tr>
    </thead>
    <tbody>
    {rows}
    </tbody>
  </table>
  <p class="muted">每 5 秒自动刷新</p>
</body>
</html>
"""

def render() -> bytes:
    info = scan_progress()
    rows = []
    for it in info["items"]:
        target = it.get("target")
        count = it.get("count", 0)
        pct = 0
        if target and target > 0:
            pct = int(count * 100 / target)
        bar = f'<div class="bar"><span style="width:{pct}%;"></span></div>'
        sheets = ", ".join(f"{s['sheet']}:{s['count']}" for s in it.get("sheets", []))
        rows.append(f"<tr><td>{it['xlsx']}</td><td>{count}</td><td>{target or '-'}</td><td>{pct}% {bar}</td><td>{sheets}</td></tr>")
    html = HTML.replace("{rows}", "\n".join(rows))
    return html.encode("utf-8")

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            body = render()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path == "/status.json":
            data = json.dumps(scan_progress()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404, "Not Found")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
        print(f"Dashboard running on http://localhost:{port}")
        httpd.serve_forever()


