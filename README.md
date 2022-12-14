## ncm-tools
Upload music with ease.

![demo](./demo/demo.gif)

- Upload music to NetEase Cloud in Mac, Linux, and of course, Windows
- Automatically retry when upload fails (up to 5 times)
- Reserve music meta info when decoding `.ncm` files

> For other tools, read [docs](./docs) section.

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

## thanks
- [magic-akari/ncmc](https://github.com/magic-akari/ncmc)
- [mos9527/pyncm](https://github.com/mos9527/pyncm)
- [CareCoder/CloudMusicUploadHelper](https://github.com/CareCoder/CloudMusicUploadHelper)
