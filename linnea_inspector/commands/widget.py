import os
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_parser(subparsers):
    p = subparsers.add_parser('widget',
                              usage="linnea-inspector store widget -p <store_dir>",
                              help="Launch the Linnea Inspector web application.")
    p.add_argument('-s', required=True, help='Path to the store directories, separated by comma.')
    p.add_argument('-p', '--port', required=False, default=8081, help='Port to run the web application on. Default is 8081.')
    
def widget(args):
    from ..widget.inspector import main as inspector_main
    #set env variable LI_STORE_ROOTS to the store directory
    os.environ["LI_STORE_ROOTS"] = args.s
    os.environ["TVST_PORT"] = str(args.port)
    inspector_main()
    
    