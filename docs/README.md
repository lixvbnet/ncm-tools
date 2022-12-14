## Checkin And Listen

### 1. Fork this repo

![20200727142541.png](_image/fork.png)

### 2. Get session string

```shell
git clone https://github.com/lixvbnet/ncm-tools.git
cd ncm-tools
pip3 install -r requirements.txt
python3 ncm_login.py
```

After successful login, get session string from `~/.ncm_cloud.key` , **copy its content**.



### 3. Add secrets

Add a secret:

- Name: `SESSION_STRING` 
- Secret: ***Paste the session string copied from previous step.*** 

> Settings -> Secrets (Actions) -> New repository secret

![image-20221213214914831](_image/image-20221213214914831.png)



### 4. Enable Action

Click **Actions** , then click **I understand my workflows, go ahead and enable them** 

![20200727155444.png](_image/pyQmdMHrOIz4x2f.png)

### 5. Trigger Action

- Automatically trigger every day
- Manually trigger by **Star** your repo

![20200727142847.png](_image/star.png)

### 6. View build logs

Click **Actions** -> **${ActionName}** -> **build** 

![image-20221213222253470](_image/image-20221213222253470.png)