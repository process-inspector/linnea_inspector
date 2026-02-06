# Linnea Inspector
# Copyright (c) 2021-2026 Aravind Sankaran
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.

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

from .apps.store import store
app.register_blueprint(store.bp, url_prefix=f'{app_mount}/')


def main():
    app.run(debug=True, port=app_port)

if __name__ == '__main__':
    main()