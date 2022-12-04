## ncm-tools
Upload music with ease.

- Upload music to NetEase Cloud in Mac, Linux, and of course, Windows
- Automatically retry when upload fails (up to 5 times)
- Reserve music meta info when decoding `.ncm` files

## install
```shell
# install dependencies
pip3 install pyncm tinytag qrcode

# clone this repo and install the python scripts
git clone https://github.com/lixvbnet/ncm-tools.git
cd ncm-tools
make install
```

> `BIN_DIR = ~/bin`, make sure this directory is added to PATH.

## workflow
```shell
# 1. clean up decoded files in current directory
ncm_clean.py [-f]
# 2. decode .ncm files in current directory
ncmc
# 3. upload music files (except .ncm files) in current directory
ncm_upload.py
```

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

Upload music files (except .ncm files) in current directory.

positional arguments:
  filepath    a single file or directory, defaults to current directory

options:
  -h, --help  show this help message and exit
```

## thanks
- [magic-akari/ncmc](https://github.com/magic-akari/ncmc)
- [mos9527/pyncm](https://github.com/mos9527/pyncm)
- [CareCoder/CloudMusicUploadHelper](https://github.com/CareCoder/CloudMusicUploadHelper)
