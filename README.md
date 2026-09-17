# Amvex Technologies — Website + API

## What's in this folder
- `index.html` — the full website (self-contained: HTML, CSS and JS in one file).
  All editable content lives in the `window.AMVEX_CONFIG` object near the top
  of the `<script>` tag — edit that object to change any text, service,
  project, stack chip, process step, or contact detail.
- `main.py` — a FastAPI backend that serves the same content as JSON, plus a
  working `/api/contact` endpoint for the contact form.
- `requirements.txt` — Python packages `main.py` needs.

## Run it locally
See the step-by-step guide in chat, or the short version:

```bash
# 1. Open the website by itself (no backend needed to just view it)
#    Just double-click index.html, or serve it properly:
python3 -m http.server 5500
# then visit http://127.0.0.1:5500/index.html

# 2. Run the API (optional, for the contact form / JSON endpoints)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
# then visit http://127.0.0.1:8000/docs
```

## Deploy to a real domain
- Frontend (`index.html`): any static host — Netlify, Vercel, GitHub Pages,
  Cloudflare Pages, or a plain Nginx/Apache server.
- Backend (`main.py`): any Python host — Render, Fly.io, Railway, a VPS with
  Nginx + Gunicorn/Uvicorn, or a Docker container.
- Point your domain's DNS at whichever host you choose, add HTTPS (most of
  the hosts above do this for free automatically), and update the CORS
  `allow_origins` list in `main.py` to include your real website domain.
- In `index.html`, replace the contact form's client-side handler with a
  `fetch()` call to your deployed API's `/api/contact` — there's a commented
  example already in the file, right after the form's submit handler.
