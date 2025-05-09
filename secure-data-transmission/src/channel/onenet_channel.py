import requests
import base64
import json
import hmac
import time
import re
from urllib.parse import quote
from utils.color import print_success, print_update, print_warring

product_id = ''
device_name = ''

class OneNet:
    def __init__(self, user_id, access_key):
        self.user_id = user_id
        self.access_key = access_key
        self.token = self.get_token()
        self.all_file = {}
        
    # 解析上传结果
    def parse_upload_result(self, response_text):
        upload_result_pattern = r'"msg":"([^"]+)"'
        match = re.search(upload_result_pattern, response_text)
        if match.group(1) == 'succ':
            return True
        else:
            return False
    
    # 解析文件列表即其对应的id值
    def parse_file_list(self, response_text):
        file_id_pattern = r'"fid":"([^"]+)"'
        match = re.findall(file_id_pattern, response_text)
        file_name_pattern = r'"name":"([^"]+)"'
        file_name_match = re.findall(file_name_pattern, response_text)
        if match:
            return match, file_name_match
        return None
    
    # 获取平台设备token
    def get_token(self):
        version = '2022-05-01'
        res = 'userid/%s' % self.user_id
        et = str(int(time.time()) + 3600)
        method = 'sha1'
        key = base64.b64decode(self.access_key)
        org = et + '\n' + method + '\n' + res + '\n' + version
        sign_b = hmac.new(key=key, msg=org.encode(), digestmod=method)
        sign = base64.b64encode(sign_b.digest()).decode()
        sign = quote(sign, safe='')
        res = quote(res, safe='')
        token = 'version=%s&res=%s&et=%s&method=%s&sign=%s' % (version, res, et, method, sign)
        print_success("OneNet信道获取认证数据成功")
        return token
    
    # 列出文件目录
    def list_files(self):
        url = "https://iot-api.heclouds.com/device/file-list?limit=1000&offset=0"
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'authorization': self.token,
        }
        response = requests.get(url, headers=headers)
        try:
            file_id_list, file_name_list = self.parse_file_list(response.text)
            for i in range(len(file_id_list)):
                self.all_file[file_name_list[i]] = file_id_list[i]
        except Exception as e:
            print(e)
            print(response.text)
        
    # 上传文件
    def upload_file(self, file_path):
        url = "https://iot-api.heclouds.com/device/file-upload"
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'authorization': self.token,
        }
        files = [
            ('file', (file_path[4:], open(file_path, 'rb'), 'text/plain'))
        ]
        payload = {
            'product_id': product_id,
            'device_name': device_name,
            'imei': 'undefined'
        }
        response = requests.post(url, headers=headers, data=payload, files=files)
        try:
            result = self.parse_upload_result(response.text)
            if result == True:
                print_success("OneNet信道上传成功")
            else:
                print_warring("OneNet信道上传失败")
        except Exception as e:
            print(response.text)
    
    # 下载文件
    def download_file(self, fileID, file_name):
        url = f"https://iot-api.heclouds.com/device/file-download?fid={fileID}"
        # print(url)
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'authorization': self.token,
        }
        res = requests.get(url, headers=headers)
        storage_path = "tmp/" + file_name
        try:    
            with open(storage_path, 'wb') as f:
                f.write(res.content)
            print_success("OneNet信道下载成功")
        except Exception as e:
            print_warring("OneNet信道下载失败")
            print(e)
            print(res.text)
            
    # 更新文件列表，如果发现文件列表有变化，找到新增文件并下载（不考虑文件删除）
    def update_file_list(self, userid):
        # 获取当前文件列表
        url = "https://iot-api.heclouds.com/device/file-list?limit=1000&offset=0"
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'authorization': self.token,
        }
        response = requests.get(url, headers=headers)
        try:
            result = json.loads(response.text)
            print
            if result["code"] == 0:
                # 获取新的文件列表
                new_file_list = {}
                # print(result)
                for file in result["data"]["list"]:
                    new_file_list[file["name"]] = file["fid"]
                # print(new_file_list)
                # 比较新旧文件列表,找出新增文件
                for file_name in new_file_list:
                    if file_name not in self.all_file:
                        if userid in file_name:
                            continue
                        print_update(f"OneNet存储发现新文件: {file_name}")
                        self.all_file[file_name] = new_file_list[file_name]
                        # 下载新文件
                        self.download_file(new_file_list[file_name], file_name)
                        # print(file_name)
                        return True, file_name
                    return False, None
            else:
                print_warring("OneNet获取文件列表失败")
                print(response.text)
        except Exception as e:
            print_warring("OneNet获取文件列表失败")
            print(e)
            
        
        
