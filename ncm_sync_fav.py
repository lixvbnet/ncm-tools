#!/usr/bin/env python3
import argparse
import os
from pyncm.apis import *
from ncm_login import *
from ncm_download import download
from ncm_upload import upload

"""
Sync favorite songs (first playlist) to cloud disk.
"""
def sync_fav(nocleanup=False):
    # === get all songs in cloud disk === #
    cloud_res = cloud.GetCloudDriveInfo(limit=10000, offset=0)
    cCount = cloud_res['count']
    cSongs = cloud_res['data']
    cSongIds = list(map(lambda item: item['songId'], cSongs))
    if len(cSongIds) != cCount:
        print(f"[ERROR] only got {cSongIds} song ids from {cCount} songs!")
        exit(1)

    print(f'{cCount} songs in cloud disk.\n')


    res = user.GetUserPlaylists(user_id=0, offset=0, limit=2)
    # print(res)
    # with open('tmp.json', 'w') as f: f.write(json.dumps(res))


    # === get first playlist === #
    p = res['playlist'][0]
    print("playlist: [%s]" % mask(p['name']))

    pInfo = playlist.GetPlaylistInfo(p['id'], total=True)
    pList = pInfo['playlist']
    # songIds = list(map(lambda item: item['id'], pList['trackIds']))
    # print(f"{len(songIds)} songs")
    songs = pList['tracks']
    print(f"{len(songs)} songs\n")


    # === download, convert, upload to cloud disk, and rectify === #
    count = 0
    success = 0
    fail = 0
    fail_list = []
    for _, song in enumerate(songs):
        songId = song['id']
        # check if the song is already uploaded to cloud disk
        if songId in cSongIds: continue

        # current song is not in cloud disk
        count += 1
        print(f"\n==================================================")

        songName = song['name']
        arNames = list(map(lambda item: item['name'], song['ar']))
        arNames = list(filter(lambda v: v is not None, arNames))
        artist = ','.join(arNames)  # arName1,arName2,...

        # download
        print("[INFO] Downloading [id=%s], [name=%s], [artist=%s]" % (songId, songName, artist))
        fileNameWithoutExt = "%s - %s" % (artist, songName)
        fileName = download(songId, fileNameWithoutExt)
        if fileName is None:
            fail += 1
            fail_list.append((songId, songName, artist))
            continue
        print(fileName)

        # convert (won't do for now)
        if fileName.lower().endswith('.ncm'):
            print(f"Found NCM file! [{fileName}]")
            exit(1)

        # upload
        publish_songId = upload(fileName, sleep=0)
        # rectify
        if publish_songId != songId:
            print(f"[INFO] Rectifying song id from [{publish_songId}] to [{songId}]")
            result = cloud.SetRectifySongId(publish_songId, songId)
            print(result)
            if result['code'] != 200:
                exit(1)

        success += 1

        if not nocleanup:
            # cleanup download file
            print(f"[INFO] (cleanup) Removing downloaded file {fileName}")
            os.remove(fileName)

    print(f"\n\n==================================================")
    print(f"count: {count}, success: {success}, fail: {fail}")
    print(f"\n--------- fail list ({len(fail_list)}) ---------")
    for item in fail_list:
        print(item)


# ============================ Main ============================ #
parser = argparse.ArgumentParser(description='Sync favorite songs (first playlist) to cloud disk.')
parser.add_argument("-n", "--nocleanup", action=argparse.BooleanOptionalAction, default=False, help="no cleanup: do not delete downloaded file")
args = parser.parse_args()

nocleanup = args.nocleanup
print(f"nocleanup={nocleanup}")

login()

sync_fav(nocleanup=nocleanup)
