# coding: utf8
# @File: zhihu.py
# @Time: 2025/03/06

from DrissionPage import ChromiumPage
from DrissionPage.common import By
from bs4 import BeautifulSoup
import tools.relationship as relationship
import tools.dynamic_information as dynamic_information
import json

name = "小约翰"

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
            f.write(detail.text + '\n')
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


usr_href = search_username_get_href()
get_user_information(usr_href)
relationship.get_followers_information(target_href=usr_href)
relationship.get_fans_information(target_href=usr_href)
page = dynamic_information.get_user_answer(usr_href)
dynamic_information.get_user_question(usr_href, page)





















