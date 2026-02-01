#!/bin/bash

# Configuration
REPO_URL="https://github.com/mlr2d/tvastar.git"
TARGET_FOLDER="tvastar"
TEMP_DIR="tmp"

echo "Starting update process..."

# 1. Clean up any existing temp directory
if [ -d "$TEMP_DIR" ]; then
    echo "Cleaning up old $TEMP_DIR directory..."
    rm -rf "$TEMP_DIR"
fi

# 2. Clone the repository
echo "Cloning repository into $TEMP_DIR..."
if git clone --depth 1 "$REPO_URL" "$TEMP_DIR"; then
    
    # 3. Check if the source folder exists in the cloned repo
    if [ -d "$TEMP_DIR/$TARGET_FOLDER" ]; then
        echo "Updating $TARGET_FOLDER..."

        # 4. Remove the existing local folder
        if [ -d "$TARGET_FOLDER" ]; then
            rm -rf "$TARGET_FOLDER"
        fi

        # 5. Copy the new folder from the temp repo to current dir
        cp -r "$TEMP_DIR/$TARGET_FOLDER" .
        
        echo "Successfully updated $TARGET_FOLDER!"
    else
        echo "Error: Folder '$TARGET_FOLDER' not found in the repository."
    fi

    # 6. Cleanup the temp directory
    rm -rf "$TEMP_DIR"
    echo "Cleanup complete."
else
    echo "Error: Failed to clone the repository."
    exit 1
fi
