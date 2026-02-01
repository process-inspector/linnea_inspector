from flask import Blueprint, render_template

from pathlib import Path

name = Path(__file__).stem ## "tvastar"

bp = Blueprint(
    name,
    __name__,
    template_folder=f"templates/", # folder relative to this file!!! Note that if same html file names occur in different apps, there might be conflicts. Hence, we scope them under app specific folders.
    static_folder=f"static/", # folder relative to this file!!! The static folders are resoled with static_url_path.
    static_url_path=f"/static/{name}/",  
)
