# coding: utf8
# @File: dynamic_information.py
# @Time: 2025/03/08

import threading
import json

class FileLock:
    def __init__(self):
        self.lock = threading.Lock()
    
    def write_json(self, file_path, data):
        """线程安全的 JSON 写入"""
        with self.lock:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    
    def read_json(self, file_path):
        """线程安全的 JSON 读取"""
        with self.lock:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except FileNotFoundError:
                return None