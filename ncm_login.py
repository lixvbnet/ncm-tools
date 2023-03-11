#!/usr/bin/env python3

import pyncm
import getpass
import os
import time
import qrcode
from pyncm import GetCurrentSession, LoadSessionFromString
from pyncm.apis.login import GetCurrentLoginStatus, WriteLoginInfo


SESSION_FILE = os.getenv("HOME") + "/.ncm_cloud.key"
DEBUG = False


def mask(s):
    return s[0] + '*'*(len(s)-2) + s[-1]


def login():
    # try load session
    session_string = os.getenv('SESSION_STRING')
    if session_string:
        print(f"Loading session from OS env 'SESSION_STRING'")
    elif os.path.isfile(SESSION_FILE):
        print(f"Loading session from {SESSION_FILE}")
        with open(SESSION_FILE) as f:
            session_string = f.read()

    if session_string:
        pyncm.SetCurrentSession(LoadSessionFromString(session_string))
        print("读取登录信息成功:[ %s ]" % mask(pyncm.GetCurrentSession().login_info['content']['profile']['nickname']))
        return

    # otherwise prompt for login and save session to file
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


if __name__ == '__main__':
    login()
