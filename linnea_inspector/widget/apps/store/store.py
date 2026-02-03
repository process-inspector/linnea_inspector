from flask import Blueprint, render_template, redirect, url_for, request

from . import config
from .actions import experiments_handler
import os

import logging
logger = logging.getLogger(__name__)


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
    return redirect(url_for(f'{name}.experiments'))
    
@bp.route('/experiments')
def experiments():
    data = experiments_handler.prepare_experiments_table(config.READER.run_configs)
    return render_template(f'{name}/experiments.html', 
                           col_schema=data['col_schema'],
                           records=data['records']
                           )

@bp.route('/experiments/edit')
def experiments_edit():
    data = experiments_handler.prepare_experiments_table(config.READER.run_configs)
    return render_template(f'{name}/experiments_edit.html', 
                           col_schema=data['col_schema'],
                           records=data['records'],
                           pk=data['pk']
                           )
    
@bp.route('/experiments/delete', methods=['POST'])
def experiments_delete():
    selected_ids = request.get_json().get('ids', [])
    if selected_ids:
        experiments_handler.delete_runs(selected_ids, config.get_reader().run_configs)
        config.init()  # Re-initialize to refresh data after deletion
    return '', 204
    