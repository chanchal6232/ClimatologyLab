"""
Production WSGI server using Waitress (Windows-compatible).
Usage:  python run_server.py
"""
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    # Ensure Django is set up before importing WSGI app
    import django
    django.setup()

    from config.wsgi import application
    from waitress import serve

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "80"))
    threads = int(os.getenv("WAITRESS_THREADS", "4"))

    print(f"Starting Waitress server on {host}:{port} with {threads} threads...")
    print(f"DEBUG = {os.getenv('DEBUG', 'True')}")
    print("Press Ctrl+C to stop.")

    serve(application, host=host, port=port, threads=threads)

if __name__ == "__main__":
    main()
