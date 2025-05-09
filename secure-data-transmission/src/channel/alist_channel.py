import requests
import time
import json
import re
from urllib.parse import quote
from utils.color import print_success, print_update, print_warring

class Alist:
    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url
        self.token = None
        self.get_token_time = 0
        self.all_file = {}
    
    # 提取JWt token
    def parse_token(self, response_text):
        token_pattern = r'"token":"([^"]+)"'
        match = re.search(token_pattern, response_text)
        if match:
            return match.group(1)
        return None
    
    # 提取所有文件名和对应的sign值
    def parse_file_name(self, response_text):
        file_name_pattern = r'"name":"([^"]+)"'
        match = re.findall(file_name_pattern, response_text)
        sign_pattern = r'"sign":"([^"]+)"'
        sign_match = re.findall(sign_pattern, response_text)
        if match:
            return match, sign_match
        return None
    
    # 解析是否上传成功
    def parse_upload_result(self, response_text):
        result_pattern = r'"message":"([^"]+)"'
        match = re.search(result_pattern, response_text)
        if match:
            return match.group(1)
        return None

    # 获取某个用户的临时JWt token，默认48小时过期
    def get_tmp_token(self):
        url = self.url + "/api/auth/login"
        payload = json.dumps({
            "username": self.username,
            "password": self.password
        })
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': self.url.split('//')[-1],
            'Connection': 'keep-alive'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        try:
            self.token = self.parse_token(response.text)
            self.get_token_time = time.time()
            print_success("Alist信道获取临时token成功（有效期48小时）")
        except Exception as e:      
            print_warring("Alist信道获取临时token失败")
            print(e)
            print(response.text)
            
    # 列出文件目录
    def list_files(self):
        url = self.url + "/api/fs/list"
        payload = json.dumps({
            "path": "/",
            "password": "",
            "page": 1,
            "per_page": 0,
            "refresh": False
        })
        headers = {
            'Authorization': self.token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': self.url.split('//')[-1],
            'Connection': 'keep-alive'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        try:
            all_file_names, all_file_signs = self.parse_file_name(response.text)
            for i in range(len(all_file_names)):
                self.all_file[all_file_names[i]] = all_file_signs[i]
        except Exception as e:
            print(e)
            print(response.text)
            
    # 上传文件
    def upload_file(self, file_path):
        url = self.url + "/api/fs/put"
        payload = open(file_path, 'rb').read()
        headers = {
            'Authorization': self.token,
            'File-Path': quote(file_path[4:],'utf-8'),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'As-Task': 'true',
            'Content-Type': 'application/octet-stream',
            'Accept': '*/*',
            'Host': self.url.split('//')[-1],
            'Connection': 'keep-alive'
        }
        response = requests.request("PUT", url, headers=headers, data=payload)
        try:
            result = self.parse_upload_result(response.text)
            if result == "success":
                print_success("Alist信道上传成功")
            else:
                print_warring("Alist信道上传失败")
        except Exception as e:
            print_warring("Alist信道上传失败")
            print(e)
            print(response.text)
            
    # 下载文件(无api接口，使用sign值)
    def download_file(self, file_path):
        url = self.url + "/d/" + file_path + "?sign=" + self.all_file[file_path]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Host': self.url.split('//')[-1],
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers)
        storage_path = "tmp/" + file_path
        try:
            with open(storage_path, 'wb') as f:
                f.write(response.content)
            print_success("Alist信道下载成功")
        except Exception as e:
            print_warring("Alist信道下载失败")
            print(e)
            print(response.text)
    
    # 更新文件列表，如果发现文件列表有变化，找到新增文件并下载（不考虑文件删除）
    def update_file_list(self, userid):
        # 获取当前文件列表
        url = self.url + "/api/fs/list"
        payload = json.dumps({
            "path": "/",
            "password": "",
            "page": 1,
            "per_page": 0,
            "refresh": True
        })
        headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': self.url.split('//')[-1],
            'Connection': 'keep-alive'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        try:
            result = json.loads(response.text)
            if result["code"] == 200:
                # 获取新的文件列表
                new_file_list = {}
                for file in result["data"]["content"]:
                    new_file_list[file["name"]] = file["sign"]
                
                # 比较新旧文件列表,找出新增文件
                for file_name in new_file_list:
                    if file_name not in self.all_file:
                        if userid in file_name:
                            continue
                        print_update(f"Alist存储发现新文件: {file_name}")
                        self.all_file[file_name] = new_file_list[file_name]
                        # 下载新文件
                        self.download_file(file_name)
                        return True, file_name
                # 如果没有新文件，返回False 
                return False, None
            else:
                print_warring("Alist获取文件列表失败")
                print(response.text)
        except Exception as e:
            print_warring("Alist获取文件列表失败")
            print(e)
            print(response.text)

# alist = Alist(username, password, alist_url)
# alist.get_tmp_token()
# alist.list_files()
# alist.download_file("1.txt")
# while True:
#     alist.update_file_list()
#     time.sleep(2)
# alist.update_file_list()
# print(alist.all_file_names)

# alist.upload_file("1.txt")