import html
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from task_5 import load_doc_vectors, load_index, search


HOST = "127.0.0.1"
PORT = 8000
TOP_K = 10

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXT_DIR = os.path.join(BASE_DIR, "text")

DOC_URLS = load_index()
DOC_VECTORS, DOC_NORMS, IDF_DICT = load_doc_vectors()


def make_snippet(doc_id, max_len=220):
    path = os.path.join(TEXT_DIR, f"{doc_id}.txt")
    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip().replace("\n", " ")

    if len(text) <= max_len:
        return text

    return text[:max_len].rstrip() + "..."


def render_page(query, results):
    query_escaped = html.escape(query or "")

    if not query:
        body = "<p>Введите запрос и нажмите «Найти».</p>"
    elif not results:
        body = f"<p>По запросу <b>{query_escaped}</b> ничего не найдено.</p>"
    else:
        rows = []
        for rank, (doc_id, score) in enumerate(results, start=1):
            url = DOC_URLS.get(doc_id, "URL не найден")
            snippet = make_snippet(doc_id)

            rows.append(
                "<tr>"
                f"<td>{rank}</td>"
                f"<td>{doc_id}</td>"
                f"<td>{score:.6f}</td>"
                f"<td><a href='{html.escape(url)}' target='_blank'>{html.escape(url)}</a></td>"
                f"<td>{html.escape(snippet)}</td>"
                "</tr>"
            )

        body = (
            f"<p>Результаты для запроса: <b>{query_escaped}</b>. "
            f"Показаны top-{TOP_K} документов.</p>"
            "<table>"
            "<thead><tr>"
            "<th>#</th><th>doc_id</th><th>score</th><th>url</th><th>фрагмент</th>"
            "</tr></thead>"
            f"<tbody>{''.join(rows)}</tbody>"
            "</table>"
        )

    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Векторный поиск</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f9fc;
      --panel: #ffffff;
      --text: #101828;
      --accent: #0057b8;
      --muted: #667085;
      --border: #d0d5dd;
    }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      color: var(--text);
      background: linear-gradient(135deg, #eef4ff 0%, var(--bg) 50%, #eefcf4 100%);
    }}
    main {{
      max-width: 1100px;
      margin: 36px auto;
      padding: 24px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(16, 24, 40, 0.08);
    }}
    h1 {{ margin-top: 0; }}
    .hint {{ color: var(--muted); margin-top: -6px; }}
    form {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin: 20px 0;
    }}
    input[type="text"] {{
      flex: 1;
      min-width: 260px;
      font-size: 16px;
      padding: 10px 12px;
      border: 1px solid var(--border);
      border-radius: 8px;
    }}
    button {{
      font-size: 16px;
      font-weight: 600;
      color: white;
      background: var(--accent);
      border: none;
      border-radius: 8px;
      padding: 10px 18px;
      cursor: pointer;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      border-top: 1px solid var(--border);
      padding: 10px 8px;
      vertical-align: top;
    }}
    th {{
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--muted);
    }}
    a {{ color: var(--accent); }}
  </style>
</head>
<body>
  <main>
    <h1>Поисковая система (векторный поиск)</h1>
    <p class="hint">Ранжирование по косинусному сходству TF-IDF векторов.</p>
    <form method="get" action="/">
      <input name="q" type="text" placeholder="Введите поисковый запрос" value="{query_escaped}" />
      <button type="submit">Найти</button>
    </form>
    {body}
  </main>
</body>
</html>
"""


class SearchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        query = params.get("q", [""])[0].strip()

        results = []
        if query:
            results = search(query, DOC_VECTORS, DOC_NORMS, IDF_DICT, top_k=TOP_K)

        content = render_page(query, results).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main():
    server = HTTPServer((HOST, PORT), SearchHandler)
    print(f"Сервер запущен: http://{HOST}:{PORT}")
    print(f"Загружено документов: {len(DOC_VECTORS)}")
    server.serve_forever()


if __name__ == "__main__":
    main()
