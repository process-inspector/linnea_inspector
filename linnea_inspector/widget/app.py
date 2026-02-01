import os
from flask import Flask, Blueprint
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from . import config
app_mount = config.app_mount
app_port =  config.app_port

app = Flask(__name__)

from .tvastar import tvastar
app.register_blueprint(tvastar.bp, url_prefix=f'{app_mount}/{tvastar.name}')

from .tvastar import tvastar_docs
app.register_blueprint(tvastar_docs.bp, url_prefix=f'{app_mount}/{tvastar_docs.name}')

from .apps.app1 import app1
app.register_blueprint(app1.bp, url_prefix=f'{app_mount}/')

from .apps.app2 import app2
app.register_blueprint(app2.bp, url_prefix=f'{app_mount}/{app2.name}')

def main():
    app.run(debug=True, port=app_port)

if __name__ == '__main__':
    main()