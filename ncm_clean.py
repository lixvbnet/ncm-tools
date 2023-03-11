#!/usr/bin/env python3

import argparse
import os

BASE_DIR = '.'
NCM_EXTENSIONS = ['.ncm']
# extensions for decoded music files, used for cleanup. (Do NOT include '.ncm')
MUSIC_DECODED_EXTENSIONS = ['.flac', '.mp3']


def clean(force=False):
    deleted = 0
    skipped = 0

    root = BASE_DIR
    print("[clean] root=" + root)

    fileList = os.listdir(root)
    for file in fileList:
        filepath = os.path.join(root, file)
        basename = os.path.basename(filepath)
        fileNameWithoutExt, ext = os.path.splitext(basename)
        if os.path.isfile(filepath) and ext in NCM_EXTENSIONS:
            # cleanup decoded music files of this ncm file
            for decoded_ext in MUSIC_DECODED_EXTENSIONS:
                decoded_filepath = os.path.join(root, fileNameWithoutExt + decoded_ext)
                if os.path.isfile(decoded_filepath):
                    print()
                    if force or input("Delete file\t" + decoded_filepath + "? [Y/n] ").lower().strip() in ['', 'y', 'yes']:
                        print("Deleting\t", decoded_filepath)
                        os.remove(decoded_filepath)
                        deleted += 1
                    else:
                        print("Skipping\t", decoded_filepath)
                        skipped += 1
    print(f"\n\nDeleted {deleted} files. Skipped {skipped}.")


# ============================ Main ============================ #
desc = f"""Clean up decoded files in current directory.
For each NCM file (with extension {NCM_EXTENSIONS}), delete its decoded files (with extension {MUSIC_DECODED_EXTENSIONS}). 
"""
parser = argparse.ArgumentParser(description=desc)
parser.add_argument("-f", "--force", action=argparse.BooleanOptionalAction, default=False, help="force delete")
args = parser.parse_args()

force = args.force
print(f"force={force}")

clean(force)
