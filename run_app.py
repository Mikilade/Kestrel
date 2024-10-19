import subprocess
import os
from app import create_app

def run_frontend():
    os.chdir('kestrel-frontend')
    subprocess.Popen(['npm', 'start'])
    os.chdir('..')

def run_backend(environ, start_response):
    app = create_app()
    return app(environ, start_response)

if __name__ == '__main__':
    #run_frontend()
    app = create_app()
    app.run()

