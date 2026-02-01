from flask import Blueprint, render_template

from . import config
import os


config.init()


from pathlib import Path
name = Path(__file__).stem

bp = Blueprint(
    name,
    __name__,
    template_folder=f"templates/", # folder relative to this file!!! Note that same html files are used for different apps, there might be conflicts. Hence, we scope them under app specific folders.
    static_folder=f"static/", # folder relative to this file!!! The static folders are resoled with static_url_path.
    static_url_path=f"/static/{name}/",  
)


@bp.route('/')
def index():
    return render_template(f'{name}/index.html', 
                           data=config.DATA['data'])