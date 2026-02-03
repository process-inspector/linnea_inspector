import sys
import os
from rocksdict import Rdict

def list_keys_with_size(db_path):
    if not os.path.exists(db_path):
        print(f"Error: The path '{db_path}' does not exist.")
        sys.exit(1)

    total_bytes = 0
    key_count = 0

    try:
        # Opening the DB
        db = Rdict(db_path)
        
        print(f"{'KEY':<40} | {'SIZE (bytes)':<15}")
        print("-" * 58)
        
        for key, value in db.items():
            # Calculate size
            size = len(value) if value is not None else 0
            total_bytes += size
            key_count += 1
            
            # Print individual entry
            print(f"{str(key):<40} | {size:<15,}")
            
        # Conversion
        total_mb = total_bytes / (1024 * 1024)
        
        print("-" * 58)
        print(f"Total Keys:  {key_count}")
        print(f"Total Size:  {total_mb:.2f} MB")
        print("-" * 58)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'db' in locals():
            db.close()

def list_keys(db_path):
    # Check if the path exists before trying to open it
    if not os.path.exists(db_path):
        print(f"Error: The path '{db_path}' does not exist.")
        sys.exit(1)

    try:
        # Open the DB in read-only mode to avoid locking issues
        # (rocks_dict handles options via the Rdict constructor)
        db = Rdict(db_path)
        
        print(f"--- Scanning keys in: {db_path} ---")
        for key in db.keys():
            print(key)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure the DB connection is closed properly
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python list_keys.py <path_to_db>")
        sys.exit(1)

    target_db = sys.argv[1]
    list_keys_with_size(target_db)
