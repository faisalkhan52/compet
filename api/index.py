"""
Vercel serverless function entrypoint.

NOTE: This is a Streamlit application. Streamlit requires persistent WebSocket
connections and a long-running process, which is incompatible with Vercel's
ephemeral Serverless Functions.

This file exists solely to satisfy Vercel's Python entrypoint detection.
For production deployment, use one of these platforms instead:
  - Streamlit Community Cloud: https://streamlit.io/cloud
  - Google Cloud Run (Dockerfile is already configured)
  - Render.com or Railway.app
"""

def app(environ, start_response):
    message = (
        b"This repository contains a Streamlit application.\n\n"
        b"Streamlit requires persistent WebSocket connections and cannot run on "
        b"Vercel Serverless Functions.\n\n"
        b"Please deploy using:\n"
        b"  - Streamlit Community Cloud: https://streamlit.io/cloud\n"
        b"  - Google Cloud Run (Dockerfile included)\n"
        b"  - Render.com or Railway.app\n"
    )
    status = "200 OK"
    headers = [
        ("Content-Type", "text/plain; charset=utf-8"),
        ("Content-Length", str(len(message))),
    ]
    start_response(status, headers)
    return [message]


# All three names that Vercel's runtime looks for
application = app
handler = app
