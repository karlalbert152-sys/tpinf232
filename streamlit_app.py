# Point d'entrée Streamlit Cloud
# INF232 EC2 - Analyse E-commerce
import sys
from pathlib import Path

ROOT = Path(__file__).parent
API_DIR = ROOT / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

# Exécuter l'application principale
exec(open(ROOT / "app" / "streamlit_app.py").read())
