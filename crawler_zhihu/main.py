# coding: utf8
# @File: main.py
# @Time: 2025/03/05

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
from time import sleep

from intake.interface.catalog.search import Search
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
import time

ChromeDriverPath = "C:\Program Files\Google\Chrome\Application\chromedriver-win64\chromedriver.exe"
LoginUrl = "https://www.zhihu.com/signin?next=%2F"
TargetUrl = "https://www.zhihu.com"
CookiePath = "zhihu_cookie.txt"

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

def basic_attribute_information(driver):
    print("==========开始采集数据==========\n")
    name = input("Please input the name of the person you want to collect:")
    try:
        # search box
        driver.find_element(By.XPATH, '//*[@id="Popover1-toggle"]').click()
        time.sleep(1)
        # input the name
        driver.find_element(By.XPATH, '//*[@id="Popover1-toggle"]').send_keys(name)
        time.sleep(1)
        # click the search button
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/header/div[1]/div[1]/div/form/div/div/label/button').click()
        time.sleep(1)
        # click the user
        driver.find_element(By.XPATH, '//*[@id="root"]/div/main/div/div[1]/div/div/ul/span[2]/li/a').click()
        time.sleep(1)
        # click the first person
        driver.find_element(By.XPATH, '//*[@id="SearchMain"]/div/div/div/div[2]/div/div/div/div/div/div[2]/h2/span/div/span/div/a/span/em').click()
        time.sleep(1)
    except Exception as e:
        print(e)
        return 1
    return 0

def social_relationship_information():
    return 0

if __name__ == '__main__':
    print("==========知乎重点人物数据采集及反爬==========\n")
    print("If you haven't been for a long time login ,plz input 1")
    print("If you have been login, plz input 2\n")
    flag2login = input("Please input:")
    if flag2login == '1':
        login_driver = pre_login()
    elif flag2login == '2':
        login_driver = auto_login()
    else:
        print("Input error!")
        exit(0)
    basic_attribute_information(login_driver)
    social_relationship_information()

