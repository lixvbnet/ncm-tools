#!/usr/bin/env python3

from pyncm.apis import *
from ncm_login import login


# ============================ Main ============================ #
login()

print(f"\nCheckin...")
res = user.SetSignin(user.SIGNIN_TYPE_WEB)
print(res)
