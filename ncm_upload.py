#!/usr/bin/env python3

import argparse
import pyncm
import hashlib
import tinytag
import os
import pickle
import re
import time
from pyncm.apis.login import GetCurrentLoginStatus
from ncm_login import login

DEBUG = False
BASE_DIR = "."

MUSIC_EXTENSIONS = [
    '.ncm', '.flac', '.mp3', '.ogg', 'mogg', '.wav', '.wma', '.m4a', '.aa', '.aac', '.aax', '.ape', '.au', '.gsm'
]
IGNORED_MUSIC_EXTENSIONS = ['.ncm']


def md5sum(file):
    md5sum = hashlib.md5()
    with open(file, 'rb') as f:
        while chunk := f.read():
            md5sum.update(chunk)
    return md5sum


COUNT = 0
UPLOAD_FAILED = []
UPLOAD_FAILED_FILE = "upload_failed.txt"


# if no runtime error, then upload is successful.
def __upload(f, md5, fname, fsize, fext, song, artist, album, bitrate):
    cresult = pyncm.apis.cloud.GetCheckCloudUpload(md5)
    songId = cresult['songId']
    time.sleep(0.2)

    token = pyncm.apis.cloud.GetNosToken(fname, md5, str(fsize), fext)['result']
    time.sleep(0.3)
    if cresult['needUpload']:
        pyncm.apis.cloud.SetUploadObject(open(f, 'rb'), md5, fsize, token['objectKey'], token['token'])
        time.sleep(2)

    submit_result = pyncm.apis.cloud.SetUploadCloudInfo(token['resourceId'], songId, md5, fname, song, artist, album, bitrate)
    if DEBUG: print(f"submit_result:\n{submit_result}")
    time.sleep(0.2)
    publish_result = pyncm.apis.cloud.SetPublishCloudResource(submit_result['songId'])
    if DEBUG: print(f"publish_result:\n{publish_result}")
    publish_songId = publish_result['privateCloud']['simpleSong']['id']
    return publish_songId


# upload a single file
def upload(f, sleep=3):
    global COUNT, UPLOAD_FAILED
    if os.path.isdir(f):
        print(f"ERROR: {f} is a directory!")
        exit(1)
    print("\n-------------------------------------------------")

    fname = os.path.basename(f)
    # name  .ext
    fname_without_ext, ext = os.path.splitext(fname)
    ext = ext.lower()
    if (ext not in MUSIC_EXTENSIONS) or (ext in IGNORED_MUSIC_EXTENSIONS):
        print(f"[WARN] Ignoring {f}")
        return

    print(f'[INFO] Uploading {f}')

    # ext (without '.')
    fext = f.split('.')[-1]
    fsize = os.stat(f).st_size
    md5 = md5sum(f).hexdigest()

    song = fname_without_ext
    artist = ""
    # artist - song
    if ' - ' in fname_without_ext:
        arr = re.split(r'\s+-\s+', fname_without_ext)
        artist, song = arr[0], arr[1]
        # print(f"[Extracted from filename] artist={artist}, song={song}\n")

    album = ""
    bitrate = 1280

    try:
        info = tinytag.TinyTag.get(f)
        if info.title:
            song = info.title
        if info.artist:
            artist = info.artist
        if info.album:
            album = info.album
        if info.bitrate:
            bitrate = int(info.bitrate)
    except Exception as ex:
        print("[INFO] unable to read tag info from the file:", ex)

    song = song.replace(".", "").replace("/", "")
    print(f"[song={song}], [artist={artist}], [album={album}], [bitrate={bitrate}]")

    max_retry = 5
    publish_songId = None
    successful = False
    for index in range(max_retry):
        try:
            publish_songId = __upload(f, md5, fname, fsize, fext, song, artist, album, bitrate)
            print(f"publish_songId=[{publish_songId}]")
            successful = True
            break
        except Exception as ex:
            print(ex)
        sec = 2
        print(f"re-trying {index+1} time after {sec} seconds...")
        time.sleep(sec)

    if not successful:
        print(f"FAILED to upload the file after retrying {max_retry} times!")
        if f not in UPLOAD_FAILED:
            UPLOAD_FAILED.append(f)
            print(f"Appended to fail-list (in memory)")
        return

    print("Upload successfully!")
    COUNT += 1
    if UPLOAD_FAILED and f in UPLOAD_FAILED:
        UPLOAD_FAILED.remove(f)
        print(f"Removed from failed list ({len(UPLOAD_FAILED)}): {f}")
    # sleep some time after upload a file successfully
    if sleep:
        print(f"Sleep {sleep} seconds...")
        time.sleep(sleep)
    return publish_songId


def upload_dir(root):
    global COUNT, UPLOAD_FAILED, UPLOAD_FAILED_FILE
    if not os.path.isdir(root):
        print(f"ERROR: {root} is not a directory!")
        exit(1)

    fileList = None
    if os.path.exists(UPLOAD_FAILED_FILE):
        with open(UPLOAD_FAILED_FILE, 'rb') as fp:
            UPLOAD_FAILED = pickle.load(fp)
            print(f"[INFO] Only uploading files in {UPLOAD_FAILED_FILE}:")
            print(f"{UPLOAD_FAILED}")
            fileList = UPLOAD_FAILED.copy()

    if not fileList:
        fileList = os.listdir(root)

    for i, file in enumerate(fileList):
        filepath = os.path.join(root, file)
        basename = os.path.basename(file)
        _, ext = os.path.splitext(basename)
        ext = ext.lower()
        if os.path.isfile(filepath) and (ext in MUSIC_EXTENSIONS) and (ext not in IGNORED_MUSIC_EXTENSIONS):
            if i == len(fileList)-1:
                upload(filepath, sleep=0)
            else:
                upload(filepath)

    # save failed ones to file, if any. Otherwise, delete the file
    if UPLOAD_FAILED:
        print("\n\nSaving failed ones to file\n")
        with open(UPLOAD_FAILED_FILE, 'wb') as fp:
            pickle.dump(UPLOAD_FAILED, fp)
    elif os.path.exists(UPLOAD_FAILED_FILE):
        print("\n\nDelete file fail-list file.\n")
        os.remove(UPLOAD_FAILED_FILE)
    print(f'\n\nUploaded {COUNT} songs. Failed {len(UPLOAD_FAILED)}.\n')


# ============================ Main ============================ #
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Upload music files in current directory ('.ncm' files will be automatically decoded).")
    parser.add_argument("filepath", nargs='?', default=BASE_DIR, help="a single file or directory, defaults to current directory")
    args = parser.parse_args()

    filepath = os.path.abspath(args.filepath)
    isdir = os.path.isdir(filepath)
    print(f"{filepath} \t isdir={isdir}")

    login()
    if isdir:
        print(f"\n[INFO] Decoding .ncm files in {filepath}")
        os.system('ncmc ' + filepath)
        print("===============================================================\n\n")
        print(f"[INFO] Uploading music files")
        upload_dir(filepath)
    else:
        upload(filepath, sleep=0)
