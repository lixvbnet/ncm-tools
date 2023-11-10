## ncm-tools
Music tools.

> For GitHub Actions, refer to [Actions](./Actions.md).

## install
```shell
git clone https://github.com/lixvbnet/ncm-tools.git
cd ncm-tools
pip3 install -r requirements.txt
make install
```

> `BIN_DIR = ~/bin`, make sure this directory is added to PATH.


## usage
- ncm_clean.py
```shell
$ ncm_clean.py -h
usage: ncm_clean.py [-h] [-f | --force | --no-force]

Clean up decoded files in current directory. For each NCM file (with extension ['.ncm']), delete its decoded files (with extension ['.flac', '.mp3']).

options:
  -h, --help            show this help message and exit
  -f, --force, --no-force
                        force delete (default: False)
```

- ncm_upload.py
```shell
$ ncm_upload.py -h
usage: ncm_upload.py [-h] [filepath]

Upload music files in current directory ('.ncm' files will be automatically decoded).

positional arguments:
  filepath    a single file or directory, defaults to current directory

options:
  -h, --help  show this help message and exit
```

- ncm_cloud_get.py & ncm_rectify.py

Some songs are not correctly matched. Rectify this way:

```shell
# get target song id
ncm_cloud_get.py | grep KEYWORD
oldSongId=xxx
# rectify with correct song id
newSongId=yyy
ncm_rectify.py $oldSongId $newSongId
```

> Correct song id can be obtained by searching the correct song and sharing its link. The song id is included in the link.

- ncm_sync_fav.py

```shell
$ ncm_sync_fac.py -h
usage: ncm_sync_fav.py [-h] [-n | --nocleanup | --no-nocleanup]

Sync favorite songs (first playlist) to cloud disk.

options:
  -h, --help            show this help message and exit
  -n, --nocleanup, --no-nocleanup
                        no cleanup: do not delete downloaded file (default: False)
```



## thanks
- [magic-akari/ncmc](https://github.com/magic-akari/ncmc)
- [mos9527/pyncm](https://github.com/mos9527/pyncm)
- [CareCoder/CloudMusicUploadHelper](https://github.com/CareCoder/CloudMusicUploadHelper)

