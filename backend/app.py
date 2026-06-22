import os

# Load .env before any other imports so env vars are available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.stocks import stocks_bp
from routes.watchlist import watchlist_bp
from routes.news import news_bp
from routes.discovery import discovery_bp
from routes.viop import viop_bp
from routes.bist import bist_bp
from flask import send_file
from routes.chat import chat_bp
from routes.indices import indices_bp

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(stocks_bp, url_prefix="/api/stocks")
app.register_blueprint(watchlist_bp, url_prefix="/api/watchlist")
app.register_blueprint(news_bp, url_prefix="/api/news")
app.register_blueprint(discovery_bp, url_prefix="/api/discover")
app.register_blueprint(viop_bp, url_prefix="/api/viop")
app.register_blueprint(bist_bp, url_prefix="/api/bist")
app.register_blueprint(chat_bp, url_prefix="/api/chat")
app.register_blueprint(indices_bp, url_prefix="/api/indices")

@app.route("/qr")
def qr_code():
    return send_file("/home/yasin/QR.png", mimetype="image/png")

@app.route("/")
@app.route("/<path:path>")
def serve_frontend(path=""):
    if path and os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, "index.html")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5001)
