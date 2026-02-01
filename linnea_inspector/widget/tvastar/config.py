import os

# get abs path of this file
this_dir = os.path.dirname(os.path.abspath(__file__))
tvst_eg_data = os.getenv('TVST_EG_DATA', os.path.join(this_dir, 'eg_data'))