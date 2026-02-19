import os
import json
from metascribe.rocks_store import RocksStore
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import glob
import tarfile
import shutil

def add_parser(subparsers):
    p = subparsers.add_parser('store',
                              usage="linnea-inspector store  [clean-logs, compress, extract,  modify] -s=<path_to_store>",
                              help="Commands to interact with the store. Subcommands: clean-logs, archive, extract, modify")
    store_subparsers = p.add_subparsers(dest='store_command', help='Store subcommands', required=True)
    
    clean_parser = store_subparsers.add_parser('clean-logs', help='Removes old log files from rocks store')
    clean_parser.add_argument('-s', required=True, help='Path to the store directory to be cleaned.')
    
    widget_parser = store_subparsers.add_parser('modify', help='Launch the web application to modify store data.')
    widget_parser.add_argument('-s', required=True, help='Path to the store directory to be modified through the web application.')
    widget_parser.add_argument('-p', '--port', required=False, default=8082, help='Port to run the web application on. Default is 8082.')
    
    compress_parser = store_subparsers.add_parser('archive', help='Compress the store into tar.gz')
    compress_parser.add_argument('-s', required=True, help='Path to the store directory to be compressed.')

    extract_parser = store_subparsers.add_parser('extract', help='Extract a compressed tar.gz store into a directory')
    extract_parser.add_argument('-s', required=True, help='Path to the compressed store archive (tar.gz) to be extracted.')

def clean_old_logs(db_path):
    for f in glob.glob(os.path.join(db_path, "LOG.old.*")):
        os.remove(f)
        
def clean_logs(store_dir):
    if not os.path.exists(store_dir):
        logger.error(f"Store directory does not exist: {store_dir}")
        raise FileNotFoundError(f"Store directory does not exist: {store_dir}")

    logs_store = os.path.join(store_dir, "logs")
    synthesis_store = os.path.join(store_dir, "synthesis")
    algs_store = os.path.join(store_dir, "algorithms")
    
    inode_count = sum(len(dirs) + len(files) for _, dirs, files in os.walk(store_dir)) + 1
    logger.info(f"Starting compaction: {inode_count} inodes.")
    
    clean_old_logs(logs_store)
    clean_old_logs(synthesis_store)
    clean_old_logs(algs_store)

    inode_count = sum(len(dirs) + len(files) for _, dirs, files in os.walk(store_dir)) + 1
    logger.info(f"Compaction complete: {inode_count} inodes.")

def archive_store(store_dir):
    if not os.path.isdir(store_dir):
        raise ValueError(f"{store_dir} is not a valid directory")

    archive_path = f"{store_dir.rstrip(os.sep)}.tar.gz"

    with tarfile.open(archive_path, "w:gz") as tar:
        # arcname ensures the directory structure inside the tar is clean
        tar.add(store_dir, arcname=os.path.basename(store_dir))
        
    logger.info(f"Store directory compressed to {archive_path}")

def extract_store(archive_path):
    if not os.path.isfile(archive_path):
        raise ValueError(f"{archive_path} is not a valid file")

    extract_dir = os.path.dirname(os.path.abspath(archive_path))
    store_name = os.path.basename(archive_path).replace(".tar.gz", "")
    target_dir = os.path.join(extract_dir, store_name)

    # Remove existing directory completely
    if os.path.isdir(target_dir):
        logger.warning(f"Target directory {target_dir} already exists. Removing it before extraction.")
        shutil.rmtree(target_dir)

    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=target_dir)

    logger.info(f"Archive extracted to {target_dir}")
         
def store(args):
    if args.store_command == "clean-logs":
        clean_logs(args.s)
    elif args.store_command == "modify":
        from ..widget.store import main as store_main
        #set env variable LI_STORE_ROOTS to the store directory
        os.environ["LI_STORE_ROOTS"] = args.s
        os.environ["TVST_PORT"] = str(args.port)
        store_main()
    elif args.store_command == "archive":
        archive_store(args.s)
    elif args.store_command == "extract":
        extract_store(args.s)
    else:
        raise ValueError(f"Unknown store command: {args.store_command}")