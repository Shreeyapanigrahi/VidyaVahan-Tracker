"""
Production WSGI entry point.

Usage:
    python wsgi.py          # starts Waitress on 0.0.0.0:8080
    python wsgi.py --port 5000

For development, continue using `flask run` or `python run.py`.
"""
import argparse
from app import create_app

app = create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='EV Tracking – Production Server')
    parser.add_argument('--host', default='0.0.0.0', help='Bind address')
    parser.add_argument('--port', type=int, default=8080, help='Bind port')
    args = parser.parse_args()

    try:
        from waitress import serve
        print(f"[PRODUCTION] Serving on http://{args.host}:{args.port}")
        serve(app, host=args.host, port=args.port, threads=4)
    except ImportError:
        print("[WARNING] waitress not installed – falling back to Flask dev server.")
        print("[WARNING] Do NOT use this in production.")
        app.run(host=args.host, port=args.port, debug=False)
