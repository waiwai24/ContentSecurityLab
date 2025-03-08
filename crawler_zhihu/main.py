# coding: utf8
# @File: main.py
# @Time: 2025/03/06

"""
知乎重点人物数据采集及反爬
（1）	基本属性信息：用户名、性别、一句话介绍、居住地、所在行业、职业经历、个人简介
（2）	社交关系信息：所有关注人和粉丝（如果关注人数量或者粉丝数量超过10，则只采集前10个），每个人的信息包括用户昵称、链接地址、回答问题数、文章数、关注者人数。
（3）	动态信息：所有回答和提问（如果回答和提问的总量超过10，则只采集前10条），每个回答或评论的信息包括发帖时间、发帖内容、评论次数、点赞次数、前10条评论（评论人ID、评论人昵称、评论时间、评论内容、点赞次数）。当用户更新了回答或提问后，应在1分钟内监控到该变化，并及时更新本地信息。
（4）	反爬功能实现：任意编写一个简单网站，复现一种基于行为监测的反爬机制，规定：若用户在规定时间窗口内没有鼠标移动、拖拽、点击等事件，则弹出消息提醒用户

知乎重点人物数据采集评判
（1）	自动登录（10分）
（2）	基本属性信息采集（15分）
（3）	社交关系信息：（15分）
（4）	动态信息及监控（20分）
（5）	可视化：能够以Web、App等形式较美观地展示采集到的数据，建议在Crawlab基础上优化完善（15分）
（6）	反爬功能实现：（15分）
（7）	TA评定：检查代码是否存在抄袭嫌疑、质询方法过程、质询代码逻辑、是否采用创新方法（多线程加速、防检测等），综合给出评判（10分）
"""

from DrissionPage import ChromiumPage
from DrissionPage.common import By
from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import tools.relationship as relationship
import tools.dynamic_information as dynamic_information

import json
import time
import threading

name = "廖雪峰"
ChromeDriverPath = "C:\Program Files\Google\Chrome\Application\chromedriver-win64\chromedriver.exe"
LoginUrl = "https://www.zhihu.com/signin?next=%2F"
TargetUrl = "https://www.zhihu.com"
CookiePath = "cookie.txt"

def monitor_dynamic_info(usr_href, page, interval=60):
    """
    循环监控用户的回答和提问信息
    参数:
        usr_href: 用户主页链接
        interval: 检查间隔（秒），默认60秒
    """
    while True:
        try:
            print(f"\n==========开始更新动态信息 {time.strftime('%Y-%m-%d %H:%M:%S')}==========")
            page = dynamic_information.get_user_answer(usr_href, page)
            if page is not None:
                page = dynamic_information.get_user_question(usr_href, page)
            print(f"==========动态信息更新完成 {time.strftime('%Y-%m-%d %H:%M:%S')}==========\n")
            time.sleep(interval)
        except Exception as e:
            print(f"更新过程中发生错误: {str(e)}")
            if page:
                page.quit()
            time.sleep(interval)
            
def pre_login():
    chrome_driver = ChromeDriverPath
    service = Service(executable_path=chrome_driver)
    driver = webdriver.Chrome(service=service)
    driver.get(LoginUrl)
    input('已经完成登录:')
    cookies = driver.get_cookies()
    with open(CookiePath,'w', encoding='utf-8') as f:
        f.write(json.dumps(cookies))
    return driver

def auto_login():
    chrome_driver = ChromeDriverPath
    service = Service(executable_path=chrome_driver)
    driver = webdriver.Chrome(service=service)
    driver.get(LoginUrl)
    options = Options()
    options.add_argument("--enable-smooth-scrolling")
    with open(CookiePath,'r', encoding='utf-8') as f:
        cookies = f.read()
        cookies = json.loads(cookies)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.get(TargetUrl)
    return driver

def search_username_get_href():
    # 创建一个浏览器对象
    page = ChromiumPage()

    # 打开知乎并搜索
    page.get('https://www.zhihu.com')
    page.set.scroll.smooth(on_off=True)  # 启用平滑滚动
    page.set.window.full()
    page.ele("#Popover1-toggle").clear().input(name)
    page.ele(".Button SearchBar-searchButton FEfUrdfMIKpQDJDqkjte Button--primary Button--blue epMJl0lFQuYbC7jrwr_o JmYzaky7MEPMFcJDLNMG").click()
    page.ele(".SearchTabs-customFilterEntry").click()

    # 点击用户
    loc1 = (By.XPATH, '//*[@id="root"]/div/main/div/div[1]/div[1]/div/ul/span[2]/li/a')
    page.ele(loc1).click()

    # 获取用户链接
    href = (By.XPATH, '//*[@id="SearchMain"]/div/div/div/div[2]/div/div/div/div/div/div[2]/h2/span/div/span/div/a')
    href_html = page.ele(href).html
    soup = BeautifulSoup(href_html, 'html.parser')
    # debug
    # print(soup)
    href = soup.a['href'][2:]
    href = 'https://' + href
    # debug
    # print(href)
    page.quit()
    return href

def get_user_information(href):
    # 创建一个新的浏览器对象
    page = ChromiumPage()
    page.set.window.full()
    # 打开用户链接并获取信息
    all_user_details = []
    user_details = {}
    with open('db/tempsave.txt', 'w', encoding='utf-8') as f:
        page.get(href)
        f.write("href" + '\n')
        f.write(href + '\n')

        loc1 = (By.XPATH, '//*[@id="ProfileHeader"]/div/div[2]/div/div[2]/div[3]/button')
        page.ele(loc1).click()
        name = page.ele(".ProfileHeader-name").text
        # debug
        # print("用户名：", name)
        f.write("用户名" + '\n')
        f.write(name + '\n')
        num = 0
        for detail in page.eles(".ProfileHeader-detailItem"):
            num += 1
        for detail in page.eles(".ProfileHeader-detailItem"):
            # 空格会影响后面的渲染，所以需要去除
            f.write(detail.text.replace(" ", "") + '\n')
            if (detail.text == "所在行业") and (num % 2 != 0):
                f.write('未知' + '\n')
        for detail in page.eles(".NumberBoard-itemInner"):
            f.write(detail.text + '\n')
        f.close()

    with open('db/tempsave.txt', 'r', encoding='utf-8') as f:
        while True:
            label = f.readline().strip('\n')
            value = f.readline().strip('\n')
            if '万' in value:
                numeric_part, unit = value.split("万")
                numeric_value = float(numeric_part)
                value = str(int(numeric_value * 10000))
            if not label or not value:
                break
            user_details[label] = value
        all_user_details.append(user_details)
        f.close()

    with open('db/user_details.json', 'w', encoding='utf-8') as f:
        json.dump(all_user_details, f, ensure_ascii=False, indent=4)
        f.close()

    print("==========用户详细信息已保存至 db/user_details.json==========")
    page.quit()

if __name__ == '__main__':
    print("==========知乎重点人物数据采集及反爬==========\n")
    print("plz input 1 to pre-login\n")
    print("plz input 2 to verify auto-login\n")
    flag2login = input("Please input:")
    if flag2login == '1':
        login_driver = pre_login()
    elif flag2login == '2':
        login_driver = auto_login()
    else:
        print("Input error!\nExit!")
        exit(0)
    usr_href = search_username_get_href()
    
    # 初始获取信息
    pageflag = 0
    get_user_information(usr_href)
    page1 = relationship.get_followers_information(usr_href ,0 ,pageflag)
    page2 = relationship.get_fans_information(usr_href, page1, pageflag)
    page3 = dynamic_information.get_user_answer(usr_href, page2)
    page4 = dynamic_information.get_user_question(usr_href, page3)
    
    # 创建并启动监控线程
    monitor_thread = threading.Thread(
        target=monitor_dynamic_info,
        args=(usr_href, page4),
        daemon=True  # 设置为守护线程，主程序退出时自动结束
    )
    monitor_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n程序已终止")
    
    





















