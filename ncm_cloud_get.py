#!/usr/bin/env python3
from pyncm.apis import *
from ncm_login import login


# ============================ Main ============================ #
login()

res = cloud.GetCloudDriveInfo(limit=10000, offset=0)

count = res['count']
songs = res['data']
print(f'{count} songs in total.\n\n')

for song in songs:
    print("songId=[%d], songName=[%s], artist=[%s], album=[%s], bitrate=[%d], fileName=[%s]" %
          (song['songId'], song['songName'], song['artist'], song['album'], song['bitrate'], song['fileName']))
