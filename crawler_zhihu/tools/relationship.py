# coding: utf8
# @File: zhihu.py
# @Time: 2025/03/06
# 别问我为什么要先写入临时文件再写入json，忘了当时的报错了，但是这样写就没问题

from DrissionPage import ChromiumPage
from DrissionPage.common import By
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re

def extract_data(line):
    pattern = r'(?:(\d{1,3}(?:,\d{3})*) 回答)?\s*' \
              r'(?:(\d{1,3}(?:,\d{3})*) 文章)?\s*' \
              r'(?:(\d{1,3}(?:,\d{3})*) 关注者)?'

    regex = re.compile(pattern)

    match = regex.match(line.strip())
    if match:
        answers, articles, followers = match.groups()
        answers = int(answers.replace(',', '')) if answers else 0
        articles = int(articles.replace(',', '')) if articles else 0
        followers = int(followers.replace(',', '')) if followers else 0
        return answers, articles, followers
    else:
        return 0, 0, 0

def buff_count(file_name):
    with open(file_name, 'rb') as f:
        count = 0
        buf_size = 1024 * 1024
        buf = f.read(buf_size)
        while buf:
            count += buf.count(b'\n')
            buf = f.read(buf_size)
        return count

def send_information2tempfile(href, username, answer_num, article_num, follower_num):
    with open('./db/tempsave.txt', 'a', encoding='utf-8') as f:
        f.write(href + '\n')
        f.write(username + '\n')
        f.write(str(answer_num) + '\n')
        f.write(str(article_num) + '\n')
        f.write(str(follower_num) + '\n')

def send_tempfile2json(key, current_time):
    with open('./db/user_details.json', 'r', encoding='utf-8') as fi:
        data = json.load(fi)
    with open('./db/tempsave.txt', 'r', encoding='utf-8') as f:
        lines = buff_count('./db/tempsave.txt')
        iter = lines // 5
        temp_data = {}
        for i in range(1, iter + 1):
            href = f.readline().strip('\n')
            username = f.readline().strip('\n')
            answer_num = int(f.readline().strip('\n'))
            article_num = int(f.readline().strip('\n'))
            follower_num = int(f.readline().strip('\n'))
            temp_data[f'{key}{i}'] = {
                f"{key}_href": href,
                f"{key}_username": username,
                "answer_num": answer_num,
                "article_num": article_num,
                "follower_num": follower_num
            }
    for user in data:
        user[key] = temp_data
        if key == 'fans':
            user['update_time'] = current_time
    try:
        with open('./db/user_details.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            print('=========={key}写入./db/user_details.json成功=========='.format(key=key))
            file.close()
    except:
        print('=========={key}写入./db/user_details.json失败=========='.format(key=key))

# 信息获取
def get_information(target_href, key, xpath_index):
    with open('./db/tempsave.txt', 'w', encoding='utf-8') as f:
        f.write('')  # 清空文件

    num_key = '关注了' if key == 'follower' else '关注者'
    with open('./db/user_details.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        # target_href = 'https://www.zhihu.com/people/liaoxuefeng'
        for item in data:
            if item["href"] == target_href:
                num = item[num_key]

    page = ChromiumPage()
    page.set.window.full()
    page.get(target_href)
    if key == 'follower':
        print('==========获取followers信息============')
    elif key == 'fans':
        print('==========获取fans信息==========')
        
    # 点击关注者或粉丝
    loc = (By.XPATH, f'//*[@id="root"]/div/main/div/div[2]/div[2]/div[2]/div[2]/div[1]/a[{xpath_index}]/div')
    page.ele(loc).click()

    if int(num) == 0:
        page.quit()
        return 0

    limit = min(int(num), 10)
    for i in range(1, limit + 1):
        # name
        xpath1 = f'//*[@id="Profile-following"]/div[2]/div[{i}]/div/div/div/div[2]/h2/span/div/span/div/a'
        info = (By.XPATH, xpath1)
        info_html = page.ele(info).html
        soup = BeautifulSoup(info_html, 'html.parser')
        href = 'https://' + soup.a['href'][2:]
        username = soup.a.text

        # answer_num, article_num, follower_num
        xpath2 = f'//*[@id="Profile-following"]/div[2]/div[{i}]/div/div/div/div[2]/div/div/div[2]'
        info = (By.XPATH, xpath2)
        try:
            try:
                info_html = page.ele(info, timeout=1).html
                soup = BeautifulSoup(info_html, 'html.parser')
                line = soup.text
            # 没有签名的情况
            except:
                xpath3 = f'//*[@id="Profile-following"]/div[2]/div[{i}]/div/div/div/div[2]/div/div/div[1]'
                info = (By.XPATH, xpath3)
                info_html = page.ele(info, timeout=1).html
                soup = BeautifulSoup(info_html, 'html.parser')
                line = soup.text
            answer_num, article_num, follower_num = extract_data(line)
        # 毛都没有的情况
        except:
            answer_num, article_num, follower_num = 0, 0, 0
        
        # debug
        print(href, username, answer_num, article_num, follower_num)
        
        send_information2tempfile(href, username, answer_num, article_num, follower_num)
        
    # 时间戳
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(current_time)
    
    send_tempfile2json(key, current_time)
    page.quit()
    return 0

# 获取关注者信息
def get_followers_information(target_href):
    return get_information(target_href, 'follower', 1)

# 获取粉丝信息
def get_fans_information(target_href):
    return get_information(target_href, 'fans', 2)


