from flask import Blueprint, render_template

from . import config
from .actions import compute_something



from pathlib import Path
name = Path(__file__).stem

bp = Blueprint(
    name,
    __name__,
    template_folder=f"templates/", 
    static_folder=f"static/", 
    static_url_path=f"/static/{name}/",  
)


@bp.route('/')
def index():
    rand_key = compute_something.get_random_value(config.random_seed)
    return render_template(f'{name}/index.html', 
                           rand_key=rand_key)