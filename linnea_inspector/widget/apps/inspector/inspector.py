# Linnea Inspector
# Copyright (c) 2021-2026 Aravind Sankaran
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.

from flask import Blueprint, render_template, redirect, url_for, request

from . import config
from .actions import synthesis_handler
from .actions import rundata_handler
from ..store.actions import experiments_handler
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
    #reedirect to reports page
    return redirect(url_for(f'{name}.facts_index'))
    
@bp.route('/experiments')
def experiments():
    data = experiments_handler.prepare_experiments_table(config.READER.run_configs)
    return render_template(f'{name}/experiments.html', 
                           col_schema=data['col_schema'],
                           records=data['records']
                           )
       
@bp.route('/facts_index')
def facts_index():
    data = config.FACTS_INDEX_ALGS
    
    return render_template(f'{name}/facts_index.html',
                           col_schema=data['col_schema'],
                           records=data['records']
                           )
    
@bp.route('/facts/algorithms/<ranking_method>/<language>/<expr>/<cluster_name>/<arch>/<precision>/<nthreads>/<prob_size>')
def facts_algorithms(ranking_method, language, expr, cluster_name, arch, precision, nthreads, prob_size):
    try:
        dfg_svg, node_info, object_info, fact_details = synthesis_handler.get_facts_algs(ranking_method, language, expr, cluster_name, arch, precision, nthreads, prob_size)
    except Exception as e:
        # TODO: may be try by getting the activity log..
        return render_template(f'{name}/error.html', message=str(e))
    
    return render_template(f'{name}/facts_algorithms.html',
                            dfg_svg=dfg_svg,
                            node_info=node_info,
                            object_info=object_info,
                            **fact_details
                           )
    
@bp.route('/code/<alg_name>/<language>/<expr>/<cluster_name>/<arch>/<precision>/<nthreads>/<prob_size>')
def algorithm_code(alg_name, language, expr, cluster_name, arch, precision, nthreads, prob_size):
    code, gen_steps = rundata_handler.get_alg_code(alg_name, language, expr, cluster_name, arch, precision, nthreads, prob_size)
    return render_template(f'{name}/algorithm_code.html',
                            code=code,
                            gen_steps=gen_steps,
                            **request.view_args
                           )