# coding: utf8
# @File: zhihu.py
# @Time: 2025/03/07
# 为每一个auto启动的多线程设置cookie

import json

def auto_login(page):
    with open('./cookie.txt', 'r', encoding='utf-8') as f:
        cookies_list = f.read()
        cookies_list = json.loads(cookies_list)
    for cookie in cookies_list:
        page.set.cookies(cookie)
    page.refresh()
    return page