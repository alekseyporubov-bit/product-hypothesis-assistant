"""
WSGI entry point for production deployment (Gunicorn)
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import app from original app.py
from app import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
