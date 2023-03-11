#!/usr/bin/env python3
import re
import requests
from pyncm.apis import *
from ncm_login import login


def download(songId, fileNameWithoutExt):
    """
    :param songId: songId
    :param fileNameWithoutExt: target filename (without extension)
    :return: full filename if successful, or None if failed
    """
    # Highest Quality
    res = track.GetTrackAudio([songId], bitrate=3200*1000)
    # with open('tmp.json', 'w') as f: f.write(json.dumps(res))
    audio = res['data'][0]

    if audio['type'] is None or audio['url'] is None:
        print(f"[WARN] [songId={songId}] Audio url is not found!")
        return None

    type = audio['type'].lower()
    size = round(audio['size'] / 1000 / 1000, 2)
    url = audio['url']
    print(f"type: {type}, size: {size}M, url: {url}")

    # remove invalid characters
    fileNameWithoutExt = re.sub('[^\\w_.)( -]', '', fileNameWithoutExt)
    fileName = fileNameWithoutExt + '.' + type
    r = requests.get(url)
    with open(fileName, 'wb') as f: f.write(r.content)
    # return full fileName
    return fileName


# ============================ Main ============================ #
if __name__ == '__main__':
    login()

    # songId = 119659   # No copyright (url is null)
    songId = 287057   # flac (seems won't appear ncm)

    fileName = download(songId, "tmp")
    print(fileName)
