#!/usr/bin/env python3

import argparse
import pyncm
import getpass
import hashlib
import tinytag
import os
import pickle
import re
import time
import qrcode
from pyncm import GetCurrentSession, LoadSessionFromString
from pyncm.apis.login import GetCurrentLoginStatus, WriteLoginInfo

SESSION_FILE = os.getenv("HOME") + "/.ncm_cloud.key"
DEBUG = False

BASE_DIR = "."

MUSIC_EXTENSIONS = [
    '.ncm', '.flac', '.mp3', '.ogg', 'mogg', '.wav', '.wma', '.m4a', '.aa', '.aac', '.aax', '.ape', '.au', '.gsm'
]
IGNORED_MUSIC_EXTENSIONS = ['.ncm']


def login():
    if os.path.isfile(SESSION_FILE):
        with open(SESSION_FILE) as f:
            print(f"Loading session info from {SESSION_FILE}")
            pyncm.SetCurrentSession(LoadSessionFromString(f.read()))
            print("读取登录信息成功:[ %s ]" % pyncm.GetCurrentSession().login_info['content']['profile']['nickname'])
            return
    else:
        print("请选择登录方式:\n[1]手机号+密码登录  [2]手机号+验证码登录  [3]二维码登录")
        login_method = int(input())
        if login_method == 1:
            phone = input('手机 >>>')
            if DEBUG:
                password = input('密码 >>>')
            else:
                password = getpass.getpass('密码 >>>')
            pyncm.apis.login.LoginViaCellphone(phone, password)
            WriteLoginInfo(GetCurrentLoginStatus())
        elif login_method == 2:
            phone = input("手机 >>>")
            if pyncm.apis.login.CheckIsCellphoneRegistered(phone)['exist'] != 1:
                print("手机号未注册,是否注册?")
                YN = input("Y/n >>>")
                if YN in ['y', 'Y']:
                    pyncm.apis.login.SetSendRegisterVerifcationCodeViaCellphone(phone)
                    print("验证码发送成功\请依次输入验证码,昵称,密码.\n以空格分割")
                    VERIFY, NICKNAME, PASSWORD = input(">>>").split(" ")
                    pyncm.apis.login.SetRegisterAccountViaCellphone(phone, VERIFY, NICKNAME, PASSWORD)
                elif YN in ['n', 'N']:
                    exit()
            elif pyncm.apis.login.SetSendRegisterVerifcationCodeViaCellphone(phone)['data']:
                print("验证码发送成功!")
                VERIFY_CODE = input("验证码 >>>")
                if pyncm.apis.login.GetRegisterVerifcationStatusViaCellphone(phone, VERIFY_CODE)['data']:
                    print("该手机号已注册" + pyncm.apis.login.CheckIsCellphoneRegistered(phone)['nickname'])
                    print("如果这是您要登录的账号,请输入密码")
                    if DEBUG:
                        PASSWORD = input("密码 >>>")
                    else:
                        PASSWORD = getpass.getpass('密码 >>>')
                    pyncm.apis.login.LoginViaCellphone(phone, PASSWORD)
                    WriteLoginInfo(GetCurrentLoginStatus())
            else:
                print("发送失败!可能是当时发送数量达到上限!")
                exit()
        elif login_method == 3:
            def dot_thingy():
                while True:
                    s = list('   ')
                    while s.count('.') < len(s):
                        s[s.count('.')] = '.'
                        yield ''.join(s)

            dot = dot_thingy()
            uuid = pyncm.apis.login.LoginQrcodeUnikey()['unikey']
            url = f'https://music.163.com/login?codekey={uuid}'
            IMG = qrcode.make(url)
            IMG.show()
            print('[-] UUID:', uuid)
            while True:
                rsp = pyncm.apis.login.LoginQrcodeCheck(uuid)
                if rsp['code'] == 803 or rsp['code'] == 800: break
                message = f"[!] {rsp['code']} -- {rsp['message']}"
                print(message, next(dot), end='\r')
                time.sleep(1)
            WriteLoginInfo(GetCurrentLoginStatus())
        else:
            exit()
    if pyncm.apis.login.GetCurrentLoginStatus()['code'] == 200:
        with open(SESSION_FILE, 'w+') as f:
            f.write(pyncm.DumpSessionAsString(GetCurrentSession()))
        print('成功登录并保存了登录信息:', pyncm.GetCurrentSession().login_info['content']['profile']['nickname'], '已登录')
    return


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
    if (ext not in MUSIC_EXTENSIONS) or (ext in IGNORED_MUSIC_EXTENSIONS):
        print(f"Ignoring {f}")
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
    successful = False
    for index in range(max_retry):
        try:
            __upload(f, md5, fname, fsize, fext, song, artist, album, bitrate)
            successful = True
            break
        except Exception as ex:
            print(ex)
        sec = 2
        print(f"re-trying {index+1} time after {sec} seconds...")
        time.sleep(sec)

    if not successful:
        print(f"FAILED to upload the file after retrying {max_retry} times!")
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
            fileList = UPLOAD_FAILED

    if not fileList:
        fileList = os.listdir(root)

    for i, file in enumerate(fileList):
        filepath = os.path.join(root, file)
        basename = os.path.basename(file)
        _, ext = os.path.splitext(basename)
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
parser = argparse.ArgumentParser(description="Upload music files (except .ncm files) in current directory.")
parser.add_argument("filepath", nargs='?', default=BASE_DIR, help="a single file or directory, defaults to current directory")
args = parser.parse_args()

filepath = os.path.abspath(args.filepath)
isdir = os.path.isdir(filepath)
print(f"{filepath} \t isdir={isdir}")

login()
if isdir:
    upload_dir(filepath)
else:
    upload(filepath, sleep=0)
