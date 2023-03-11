#!/usr/bin/env python3

import random
import time
from pyncm.apis import *
from ncm_login import login

DEBUG = False
MAX_LISTEN = random.randint(320, 500)


@WeapiCryptoRequest
@LoginRequiredApi
def get_recommend_resource():
    return "/weapi/v1/discovery/recommend/resource", {}


@WeapiCryptoRequest
@LoginRequiredApi
def weblog(logs):
    """
    Args:
        logs (list)
    """
    return "/weapi/feedback/weblog", {"logs": json.dumps(logs)}


class Song:
    def __init__(self, songId, sourceId, listenTime):
        self.songId = songId
        self.sourceId = sourceId
        self.listenTime = listenTime


def listen(songs):
    """
    Args:
        songs (list)
    """
    logs = list(map(lambda song:
                    {
                        'action': 'play',
                        'json': {
                            'download': 0,
                            'end': 'playend',
                            'id': song.songId,
                            'sourceId': song.sourceId,
                            'time': song.listenTime,
                            'type': 'song',
                            'wifi': 0,
                            'source': 'list'
                        }
                    }, songs))
    return weblog(logs)


# ============================ Main ============================ #
login()

res = get_recommend_resource()
# print(res)
if res['code'] != 200:
    raise Exception(f"获取每日推荐歌单失败！")

playlists = res['recommend']
print(f"成功获取每日推荐歌单，共 {len(playlists)} 个")

count = 0
listenCount = 0

# random choose playlists
for p in random.sample(playlists, len(playlists)):
    try:
        pInfo = playlist.GetPlaylistInfo(p['id'])
        pList = pInfo['playlist']
        print(f"\nCurrent playlist: [{pList['name']}]")
        songIds = list(map(lambda item: item['id'], pList['trackIds']))
        songList = track.GetTrackDetail(songIds)['songs']
        print(f"{len(songList)} songs")
        print(f"------------------------------------------")

        exit_flag = False
        songs = []
        # random choose songs
        max_listen_per_playlist = random.randint(15, 35)
        for i, song in enumerate(random.sample(songList, len(songList))[:max_listen_per_playlist]):
            if count >= MAX_LISTEN:
                exit_flag = True
                break
            if DEBUG: print(f"Adding '{song['name']}', id={song['id']}, album: {song['al']['name']} ({song['al']['id']})")
            songs.append(Song(songId=song['id'], sourceId=pList['id'], listenTime=song['dt']))
            count += 1
            if DEBUG: print(f"count = {count}")

        # listen songs
        if songs:
            print(f"Listening {len(songs)} songs from playlist '{pList['name']}'")
            listen(songs)
            listenCount += len(songs)
            sec = 1
            print(f"Sleeping {sec} seconds...")
            time.sleep(sec)

        if exit_flag:
            break
    except Exception as ex:
        print("Error:", ex)
        continue

print(f"\n完成！一共听歌{listenCount}首。")
