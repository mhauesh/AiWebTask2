import sys
import os
from pathlib import Path

APPLICATION_PATH = Path('/u101/public_html/AiWebTask2').resolve()

if str(APPLICATION_PATH) not in sys.path:
    sys.path.insert(0, str(APPLICATION_PATH))

os.environ['FLASK_ENV'] = 'production'

from app import app as application

INDEX_DIR = APPLICATION_PATH / "whoosh_index"
if not INDEX_DIR.exists():
    try:
        INDEX_DIR.mkdir(parents=True)
    except Exception as e:
        print(f"Failed to create index directory: {e}", file=sys.stderr)

TEMPLATES_DIR = APPLICATION_PATH / "templates"
if not TEMPLATES_DIR.exists():
    try:
        TEMPLATES_DIR.mkdir(parents=True)
    except Exception as e:
        print(f"Failed to create templates directory: {e}", file=sys.stderr)

import logging
logging.basicConfig(
    filename=str(APPLICATION_PATH / 'crawler.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)