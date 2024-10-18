import subprocess
import os
from app import create_app

def run_frontend():
    os.chdir('kestrel-frontend')
    subprocess.Popen(['npm', 'start'])
    os.chdir('..')

def run_backend():
    app = create_app()
    app.run()

if __name__ == '__main__':
    run_backend()
    run_frontend()

