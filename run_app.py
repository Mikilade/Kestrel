import subprocess
import os
from app import create_app

def run_backend(environ, start_response):
    app = create_app()
    return app(environ, start_response)

if __name__ == '__main__':
    app.run()

