from flask import Flask, render_template, request, url_for
from whoosh_crawler import WebCrawler
import os
from pathlib import Path
import traceback
import sys

app = Flask(__name__)


@app.errorhandler(500)
def internal_error(exception):
    print(traceback.format_exc(), file=sys.stderr)  # logging to error log
    return "<pre>" + traceback.format_exc() + "</pre>"

@app.errorhandler(Exception)
def unhandled_exception(e):
    print(traceback.format_exc(), file=sys.stderr)  # logging to error log
    return "<pre>" + traceback.format_exc() + "</pre>"


# Initialize the crawler and build index if needed
BASE_DIR = Path(__file__).resolve().parent
INDEX_DIR = BASE_DIR / "whoosh_index"
START_URL = "https://vm009.rz.uos.de/crawl/index.html"

def init_crawler():
    """Initialize or load the crawler index"""
    crawler = WebCrawler(START_URL, str(INDEX_DIR))
    if not INDEX_DIR.exists() or not any(INDEX_DIR.iterdir()):
        print("Building index...")
        crawler.crawl()
    return crawler

crawler = init_crawler()

@app.route('/')
def home():
    """Display search form"""
    return render_template('search.html')

@app.route('/search')
def search():
    """Handle search requests"""
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html')
    
    try:
        results = crawler.search(query)
        print(f"Query: {query}")  # Debug print
        print(f"Found {len(results)} results")  # Debug print
        for url, title, teaser in results:
            print(f"- {title}: {url}")  # Debug print
            print(f"  {teaser}")  # Debug print
        return render_template('search.html', query=query, results=results)
    except Exception as e:
        print(f"Search error: {e}")  # Debug print
        return render_template('search.html', query=query, error=str(e))

if __name__ == '__main__':
    templates_dir = BASE_DIR / "templates"
    templates_dir.mkdir(exist_ok=True)
    template_path = templates_dir / "search.html"
    if not template_path.exists():
        template_content = """<!DOCTYPE html>
<html>
<head>
    <title>Web Crawler Search</title>
    <style>Search error: too many values
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .search-box {
            margin: 20px 0;
            text-align: center;
        }
        input[type="text"] {
            width: 300px;
            padding: 10px;
            font-size: 16px;
        }
        input[type="submit"] {
            padding: 10px 20px;
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        .results {
            margin-top: 30px;
        }
        .result-item {
            margin: 20px 0;
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        .result-title {
            font-size: 18px;
            margin-bottom: 5px;
        }
        .result-url {
            color: #006621;
            font-size: 14px;
        }
        .result-teaser {
            margin: 10px 0;
            }
        .error {
            color: red;
            margin: 20px 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>Web Crawler Search</h1>
    
    <div class="search-box">
        <form action="/search" method="get">
            <input type="text" name="q" value="{{ query or '' }}" placeholder="Enter search terms...">
            <input type="submit" value="Search">
        </form>
    </div>

    {% if error %}
        <div class="error">{{ error }}</div>
    {% endif %}

    {% if results %}
        <div class="results">
            <h2>Search Results</h2>
            {% for url, title, teaser in results %}
                <div class="result-item">
                    <div class="result-title">
                        <a href="{{ url }}">{{ title or 'Untitled Page' }}</a>
                    </div>
                    <div class="result-url">{{ url }}</div>
                    <div class="result-teaser">{{ teaser|safe }}</div>
                </div>
            {% endfor %}
        </div>
    {% elif query %}
        <p>No results found for "{{ query }}"</p>
    {% endif %}
</body>
</html>"""
        template_path.write_text(template_content)
    
    app.run(debug=True)