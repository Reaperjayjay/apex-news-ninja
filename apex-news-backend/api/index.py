@"
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from mangum import Mangum

# Vercel ASGI handler
handler = Mangum(app, lifespan='off')
"@ | Out-File -FilePath api/index.py -Encoding utf8