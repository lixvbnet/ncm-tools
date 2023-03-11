#!/usr/bin/env python3
import argparse
from pyncm.apis import *
from ncm_login import login


# ============================ Main ============================ #
parser = argparse.ArgumentParser(description="")
parser.add_argument("oldSongId", nargs='?', help="")
parser.add_argument("newSongId", nargs='?', help="")
args = parser.parse_args()

oldSongId = args.oldSongId
newSongId = args.newSongId

print("oldSongId=[%s], newSongId=[%s]" % (oldSongId, newSongId))

login()

result = cloud.SetRectifySongId(oldSongId, newSongId)
print(result)
