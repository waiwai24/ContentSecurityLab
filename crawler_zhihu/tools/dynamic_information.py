# coding: utf8
# @File: dynamic_information.py
# @Time: 2025/03/07
# 虽然多线程获取，但还是比较慢

# 动态信息：所有回答和提问（如果回答和提问的总量超过10，则只采集前10条）
# 回答或评论信息包括发帖时间、发帖内容、评论次数、点赞次数、前10条评论（评论人ID、评论人昵称、评论时间、评论内容、点赞次数）
# 当用户更新了回答或提问后，应在1分钟内监控到该变化，并及时更新本地信息
from DrissionPage import ChromiumPage
from DrissionPage import ChromiumOptions
from DrissionPage.common import By
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
import time
import os

db_answer = './db/answer.json'
db_question = './db/question.json'


def auto_login(page):
    with open('./cookie.txt', 'r', encoding='utf-8') as f:
        cookies_list = f.read()
        cookies_list = json.loads(cookies_list)
    for cookie in cookies_list:
        page.set.cookies(cookie)
    page.refresh()
    return page

def get_last_line(s):
    lines = s.splitlines()
    if lines:
        return lines[-1]
    else:
        print('==========获取最后一行失败==========\n')
        return 0

def re_match2question(string):
    # 正则表达式提取数据
    pattern = r'<div class="ContentItem-status">(.*?)</div>'
    match = re.search(pattern, string, re.DOTALL)
    return_spans = []
    if match:
        content = match.group(1)
        # 提取每个 span 中的内容
        spans = re.findall(r'<span class="ContentItem-statusItem">(.*?)</span>', content)
        return spans

def write_answer2json(data, label):
    if os.path.exists(db_answer) and os.path.getsize(db_answer) > 0:
        with open(db_answer, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    # 添加update_time
    data.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    formatted_item = {
        '问题标题': data[0],
        '回答时间': data[1],
        '回答IP': data[2],
        '回答内容': data[3],
        '评论次数': data[4],
        '点赞次数': data[5],
        '评论信息': [
            {
                '评论人昵称': comment[0],
                '评论时间': comment[1],
                '评论点赞次数': comment[2],
                '评论内容': comment[3]
            } for comment in data[6]
        ],
        'update_time': data[7]
    }
    existing_data[label] = formatted_item
    with open(db_answer, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
        f.close()

def write_question2json(data, label):
    if os.path.exists(db_question) and os.path.getsize(db_question) > 0:
        with open(db_question, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    # 添加update_time
    data.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    formatted_item = {
        '提问标题': data[0],
        '提问时间': data[1],
        '回答数目': data[2],
        '关注数目': data[3],
        '提问内容': data[4],
        '回答人数': data[5],
        "回答信息": [
            {
                '回答人昵称': answer[0] if len(answer) > 0 else '',
                '回答时间': answer[1] if len(answer) > 1 else '',
                '回答赞次数': answer[2] if len(answer) > 2 else '',
                '回答内容': answer[3] if len(answer) > 3 else ''
            } for answer in data[6]
        ],
        'update_time': data[7]
    }
    existing_data[label] = formatted_item
    with open(db_question, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
        f.close()

def clear_data(clear_file):
    with open(clear_file, 'w', encoding='utf-8') as f:
        f.write('')
        f.close()
    
def analyze_answer(target_href, page_flag, page):
    # 创建一个浏览器对象
    if page_flag == 0:
        option = ChromiumOptions().auto_port()
        page = ChromiumPage(addr_or_opts=option)
        page.get(target_href)
        page = auto_login(page)
        page.set.window.full()
    else:
        page.get(target_href)
        page.set.window.full()
    # 获取发帖时间和IP
    timeandip = page.ele((By.CLASS_NAME, 'ContentItem-time')).text
    return_answer_time = timeandip[4:20]
    return_answer_ip = timeandip[26:]

    # 获取发帖内容
    return_answer_content = page.ele((By.CLASS_NAME, 'RichText ztext CopyrightRichText-richText css-ob6uua')).text

    # 获取评论次数
    comments_num = page.ele((By.CLASS_NAME, 'Button ContentItem-action FEfUrdfMIKpQDJDqkjte Button--plain Button--withIcon Button--withLabel fEPKGkUK5jyc4fUuT0QP B46v1Ak6Gj5sL2JTS4PY RuuQ6TOh2cRzJr6WlyQp')).text
    comments_num = get_last_line(comments_num)
    if comments_num == '添加评论':
        return_comments_num = 0
    else:
        return_comments_num = int(re.findall(r'\d+', comments_num)[0])

    # 获取点赞次数
    like_num = page.ele((By.CLASS_NAME, 'Button VoteButton VoteButton--up FEfUrdfMIKpQDJDqkjte')).text
    if like_num == '赞同':
        return_like_num = 0
    else:
        return_like_num = int(re.findall(r'\d+', like_num)[0])

    # 获取评论信息(评论信息包括评论人ID(暂时没看见)、评论人昵称、评论时间、评论内容、点赞次数)
    return_comment_info = []
    comment_name = []
    comment_time = []
    comment_like = []
    comment_content = []
    
    if return_comments_num == 0:
        print('==========回答无评论信息为0，结束获取该回答评论信息==========\n')
        return_result = [page, return_answer_time, return_answer_ip, return_answer_content, return_comments_num, return_like_num, return_comment_info]
        return return_result
    try:
        loc = (By.XPATH, '//*[@id="root"]/div/main/div/div/div[3]/div[1]/div/div[2]/div/div/div/div[2]/div[2]/div[1]/button[1]')
        page.ele(loc, timeout=1).click()
    except:
        try:
            loc = (By.XPATH, '//*[@id="root"]/div/main/div/div/div[3]/div[1]/div/div[2]/div/div/div/div[2]/div[2]/div[1]/button[1]/text()')
            page.ele(loc, timeout=1).click()
        except:
            loc_except = (By.XPATH, '//*[@id="root"]/div/main/div/div/div[3]/div[1]/div/div[2]/div/div/div/div[2]/div[2]/button[1]')
            page.ele(loc_except, timeout=1).click()

    # 由于评论下又有回复，暂时不考虑回复属于评论的情况
    i = 1
    for temp in page.eles((By.CLASS_NAME, 'css-10u695f')):
        if i <= 10:
            comment_name.append(temp.text)
            i += 1
        else:
            break
    i = 1
    for temp in page.eles((By.CLASS_NAME, 'css-12cl38p')):
        if i <= 10:
            comment_time.append(temp.text)
            i += 1
        else:
            break
    i = 1
    for temp in page.eles((By.CLASS_NAME, 'Button Button--plain Button--grey Button--withIcon Button--withLabel css-1vd72tl')):
        if i <= 10:
            comment_like.append(temp.text[2:])
            i += 1
        else:
            break
    i = 1
    for temp in page.eles((By.CLASS_NAME, 'CommentContent css-1jpzztt')):
        if i <= 10:
            comment_content.append(temp.text)
            i += 1
        else:
            break
    
    # print(comment_name)
    # print(comment_time)
    # print(comment_like)
    # print(comment_content)
    
    # 将评论信息存入return_comment_info
    for i in range(0, i - 1):
        return_comment_info.append([comment_name[i], comment_time[i], comment_like[i], comment_content[i]])
    return_result = [page, return_answer_time, return_answer_ip, return_answer_content, return_comments_num, return_like_num, return_comment_info]
    # print(return_result)
    return return_result
    
def analyze_question(target_href, page_flag, page):
    # 创建一个浏览器对象
    if page_flag == 0:
        option = ChromiumOptions().auto_port()
        page = ChromiumPage(addr_or_opts=option)
        page.get(target_href)
        page = auto_login(page)
        page.set.window.full()
    else:
        page.get(target_href)
        page.set.window.full()

    # 获取提问内容
    click_loc = (By.XPATH, '//*[@id="root"]/div/main/div/div/div[1]/div[2]/div/div[1]/div[1]/div[6]/div/div/div/button')
    try:
        page.ele(click_loc, timeout=1).click()
        return_question_content = page.ele((By.CLASS_NAME, 'RichText ztext css-ob6uua')).text
    except:
        return_question_content = ''

    # 获取回答人数，实测回答人数存在问题 https://www.zhihu.com/question/14028557576(该网站目前显示5个回答，实际只有四个)
    return_question_answer_num = page.ele((By.CLASS_NAME, 'List-headerText')).text[:-4]

    # 获取回答信息[回答人昵称, 回答时间, 回答赞次数, 回答内容]
    return_question_answer_name = []
    return_question_answer_time = []
    return_question_answer_like = []
    return_question_answer_content = []
    return_question_answer_info = []
    count = 0
    for answer_container in page.eles((By.CLASS_NAME, 'UserLink AuthorInfo-name')):
        return_question_answer_name.append(answer_container.text)
        count += 1
        if count == 10:
            break
        # print (return_question_answer_name)
    count = 0
    for answer_container in page.eles((By.CLASS_NAME, 'ContentItem-time')):
        return_question_answer_time.append(answer_container.text[4:20])
        count += 1
        if count == 10:
            break
        # print (return_question_answer_time)
    count = 0
    for answer_container in page.eles((By.CLASS_NAME, 'Button VoteButton VoteButton--up FEfUrdfMIKpQDJDqkjte')):
        if answer_container.text[4:] == '':
            return_question_answer_like.append(str(0))
        else:
            return_question_answer_like.append(answer_container.text[4:])
        count += 1
        if count == 10:
            break
        # print (return_question_answer_like)
    count = 0
    for answer_container in page.eles((By.CLASS_NAME, 'RichText ztext CopyrightRichText-richText css-ob6uua')):
        if answer_container.text == '':
            return_question_answer_content.append('回答内容为视频，请到具体详情页查看')
        else:
            return_question_answer_content.append(answer_container.text)    
        count += 1
        if count == 10:
            break
        # print (return_question_answer_content)
    for i in range(0, count):
        return_question_answer_info.append([return_question_answer_name[i], return_question_answer_time[i], return_question_answer_like[i], return_question_answer_content[i]])
    # print(return_question_answer_info)
    return_result = [page, return_question_content, return_question_answer_num, return_question_answer_info]
    return return_result
    
def get_user_answer(target_href, page):
    # 创建一个浏览器对象
    page_flag = 0 # 用于优化page
    # option = ChromiumOptions().auto_port()
    # page = ChromiumPage(addr_or_opts=option)
    page.get(target_href)
    page.set.window.full()
    page = auto_login(page)


    print('==========准备获取用户回答信息==========\n')

    # 点击回答
    loc = (By.XPATH, '//*[@id="ProfileMain"]/div[1]/ul/li[2]/a')
    page.ele(loc).click()
    time.sleep(1)

    # 获取回答总数
    return_answer_num = page.ele((By.CLASS_NAME, 'Tabs-meta')).text

    # 获取回答信息
    # threads = []
    return_answer_question = []
    return_answer_question_href = []

    if int(return_answer_num) == 0:
        print('==========用户无回答信息为0，结束获取回答信息==========\n')
        return page

    limit = min(int(return_answer_num), 10)
    loc = [f'//*[@id="Profile-answers"]/div[2]/div[{i}]/div/div/h2/div/a' for i in range(1, limit + 1)]
    analyze_page = page
    print('==========开始获取回答信息==========')
    print('==========清空之前保存信息==========')
    clear_data(db_answer)
    for i in range(0, limit):
        info = (By.XPATH, loc[i])
        info_html = page.ele(info).html
        soup = BeautifulSoup(info_html, 'html.parser')
        return_answer_question.append(soup.a.text)
        return_answer_question_href.append('https:' + soup.a['href'])
        # 创建线程
        # t = threading.Thread(target=analyze_answer, args=('https:' + soup.a['href'],))
        # threads.append(t)
        analyze_answer_return = analyze_answer('https:' + soup.a['href'], page_flag, analyze_page)
        analyze_page = analyze_answer_return[0]
        analyze_answer_return[0] = return_answer_question[i]
        print('==========获取第' + str(i + 1) + '条回答信息==========')
        # 返回列表格式：[问题标题, 回答时间, 回答IP, 回答内容, 评论次数, 点赞次数, 评论信息[评论人昵称, 评论时间, 评论点赞次数, 评论内容]]
        print(analyze_answer_return)
        page_flag = 1
        # 按照返回列表格式用键值对的json格式存储
        write_answer2json(analyze_answer_return, 'answer' + str(i+1))
    print('==========获取回答信息结束==========\n')

    # 非常愚蠢的启动多线程，经测试，加载会卡死，多线程比单线程慢
    # for t in threads:
    #     t.start()
    # for t in threads:
    #     t.join()
    analyze_page.quit()
    return page

def get_user_question(target_href, page):
    page_flag = 0
    # 创建一个浏览器对象
    # option = ChromiumOptions().auto_port()
    # page = ChromiumPage(addr_or_opts=option)
    # page.get(target_href)
    # page = login.auto_login(page)
    # 接着使用游览器对象
    page.get(target_href)
    page.set.window.full()

    print('==========准备获取用户提问信息==========\n')

    # 点击提问
    loc = (By.XPATH, '//*[@id="ProfileMain"]/div[1]/ul/li[4]/a')
    page.ele(loc).click()
    time.sleep(1)
    
    # 获取提问总数
    return_question_num = page.eles((By.CLASS_NAME, 'Tabs-meta'))[2].text
    
    # 获取提问信息
    return_question_title = []
    return_question_href = []
    return_question_time = []
    return_question_answer_num = []
    return_question_follow_num = []
    
    if int(return_question_num) == 0:
        page.quit()
        print('==========用户无提问信息为0，结束获取提问信息==========\n')
        return 0
    
    limit = min(int(return_question_num), 10)
    loc_title = [f'//*[@id="Profile-asks"]/div[2]/div[{i}]/div/div/h2/span/div/a' for i in range(1, limit + 1)]
    loc_othershow = [f'//*[@id="Profile-asks"]/div[2]/div[{i}]/div/div/div' for i in range(1, limit + 1)]
    page_turning_flag = 0
    for i in range(0, limit):
        try:
            info = (By.XPATH, loc_title[i])
            info_other = (By.XPATH, loc_othershow[i])
            info_html = page.ele(info, timeout = 1).html
            info_other_html = page.ele(info_other, timeout = 1).html
        except:
            tmp = i + 1
            page_turning_flag += 1
            click_loc = (By.XPATH, f'//*[@id="Profile-asks"]/div[2]/div[{tmp}]/button[2]')
            page.ele(click_loc).click()
            temp_loc_title = f'//*[@id="Profile-asks"]/div[2]/div[{page_turning_flag}]/div/div/h2/span/div/a'
            temp_loc_other = f'//*[@id="Profile-asks"]/div[2]/div[{page_turning_flag}]/div/div/div'
            info = (By.XPATH, temp_loc_title)
            info_other = (By.XPATH, temp_loc_other)
            info_html = page.ele(info).html
            info_other_html = page.ele(info_other).html
        soup = BeautifulSoup(info_html, 'html.parser')
        soup_other = BeautifulSoup(info_other_html, 'html.parser')
        soup_other_analyze = re_match2question(str(soup_other))
        return_question_title.append(soup.a.text)
        return_question_href.append('https://zhihu.com' + soup.a['href'])
        return_question_time.append(soup_other_analyze[0])
        return_question_answer_num.append(soup_other_analyze[1])
        return_question_follow_num.append(soup_other_analyze[2])

    # print(return_question_href)
    # print(return_question_title)
    # print(return_question_time)
    # print(return_question_answer_num)
    # print(return_question_follow_num)

    analyse_page = page
    print('==========开始获取提问信息==========')
    print('==========清空之前保存信息==========')
    clear_data(db_question)
    for i in range(0, limit):
        analyze_question_return = analyze_question(return_question_href[i], page_flag, analyse_page)
        analyse_page = analyze_question_return[0]
        analyze_question_return[0] = return_question_title[i]
        analyze_question_return.insert(1, return_question_time[i])
        analyze_question_return.insert(2, return_question_answer_num[i])
        analyze_question_return.insert(3, return_question_follow_num[i])
        print('==========获取第' + str(i + 1) + '条提问信息==========')
        # [提问标题, 提问时间, 回答数目, 关注数目, 提问内容, 回答人数, 回答信息[回答人昵称, 回答时间, 回答赞次数, 回答内容]]
        print(analyze_question_return)
        page_flag = 1
        # 按照返回列表格式用键值对的json格式存储
        write_question2json(analyze_question_return, 'question' + str(i + 1))
    print('==========获取提问信息结束==========\n')
    analyse_page.quit()
    return page

# answer_return_page = get_user_answer("https://www.zhihu.com/people/gianluca-sorrentino/")
# # analyze_answer('https://www.zhihu.com/question/647766773/answer/68484783999',0,0)
# get_user_question("https://www.zhihu.com/people/gianluca-sorrentino/", answer_return_page)
# # analyze_question('https://www.zhihu.com/question/295109514', 0, 0)
# analyze_answer('https://www.zhihu.com/question/14365568411/answer/119198135782',0 ,0)