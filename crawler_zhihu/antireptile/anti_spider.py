# coding=utf-8

from flask import Flask, request, jsonify, render_template, make_response
from collections import defaultdict
import time
import random
import json
from datetime import datetime
import math

app = Flask(__name__)
app.template_folder = app.root_path

# ====== 配置参数 ======
REQUEST_LIMIT = 3  # 时间窗口内允许的最大请求数
TIME_WINDOW = 10  # 时间窗口长度（秒）
INACTIVITY_THRESHOLD = 5  # 无操作检测阈值（秒）
BAN_MESSAGE_FREQ = "请求过于频繁，疑似爬虫行为，已禁止访问！"
BAN_MESSAGE_USERAGENT = "UserAgent不存在!"
MOUSE_MOVE_THRESHOLD = 10  # 最小鼠标移动距离阈值
HUMAN_MOVE_VARIANCE = 100  # 人类移动方差阈值

# 用户行为记录
user_activities = defaultdict(lambda: {
    'last_activity': time.time(),
    'mouse_positions': [],
    'suspicious_count': 0
})

class MouseBehaviorAnalyzer:
    def __init__(self):
        self.movements = []
        self.last_position = None
        self.last_time = None
        self.suspicious_patterns = {
            'straight_line': 0,
            'uniform_speed': 0,
            'inactivity': 0
        }

    def analyze_movement(self, x, y, timestamp, client_ip):
        current_time = time.time()
        user_activities[client_ip]['last_activity'] = current_time

        if self.last_position and self.last_time:
            dx = x - self.last_position[0]
            dy = y - self.last_position[1]
            dt = timestamp - self.last_time
            
            distance = math.sqrt(dx*dx + dy*dy)
            speed = distance / dt if dt > 0 else 0
            
            movement_data = {
                'x': x, 'y': y,
                'time': timestamp,
                'speed': speed,
                'distance': distance
            }
            
            user_activities[client_ip]['mouse_positions'].append(movement_data)
            
            # 检测可疑行为
            if self._is_straight_line(x, y):
                self.suspicious_patterns['straight_line'] += 1
            if self._is_uniform_speed(speed):
                self.suspicious_patterns['uniform_speed'] += 1
            
            # 清理旧数据
            if len(user_activities[client_ip]['mouse_positions']) > 100:
                user_activities[client_ip]['mouse_positions'] = user_activities[client_ip]['mouse_positions'][-100:]
        
        self.last_position = (x, y)
        self.last_time = timestamp
        
        return self._check_suspicious(client_ip)

    def _is_straight_line(self, x, y):
        if len(self.movements) < 3:
            return False
        
        last_three = self.movements[-3:]
        x1, y1 = last_three[0]['x'], last_three[0]['y']
        x2, y2 = last_three[1]['x'], last_three[1]['y']
        x3, y3 = x, y
        
        area = abs((x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2))/2.0)
        return area < 1.0

    def _is_uniform_speed(self, current_speed):
        if len(self.movements) < 2:
            return False
        
        last_speed = self.movements[-1]['speed']
        return abs(current_speed - last_speed) < 0.1

    def _check_suspicious(self, client_ip):
        suspicious_score = (
            self.suspicious_patterns['straight_line'] * 2 +
            self.suspicious_patterns['uniform_speed'] * 1.5 +
            self.suspicious_patterns['inactivity']
        )
        
        if suspicious_score > 10:
            user_activities[client_ip]['suspicious_count'] += 1
            return True
        return False

    def check_inactivity(self, client_ip):
        last_activity = user_activities[client_ip]['last_activity']
        if time.time() - last_activity > INACTIVITY_THRESHOLD:
            self.suspicious_patterns['inactivity'] += 1
            return True
        return False

# 在 MouseBehaviorAnalyzer 类和全局实例创建之间添加以下函数
def check_request_UserAgent(user_agent):
    """
    检查请求的User-Agent
    :param user_agent: 请求头中的User-Agent字符串
    :return: True 如果是可疑的User-Agent，False 如果是正常的User-Agent
    """
    if not user_agent:
        return True
        
    suspicious_keywords = [
        'python',
        'curl',
        'wget',
        'scrapy',
        'requests',
        'bot',
        'spider',
        'crawler'
    ]
    
    user_agent = user_agent.lower()
    return any(keyword in user_agent for keyword in suspicious_keywords)

def check_request_frequency(client_ip):
    """
    检查请求频率
    :param client_ip: 客户端IP地址
    :return: True 如果请求频率过高，False 如果请求频率正常
    """
    current_time = time.time()
    client_history = user_activities[client_ip]
    
    # 清理超出时间窗口的记录
    client_history['mouse_positions'] = [
        pos for pos in client_history['mouse_positions']
        if current_time - pos['time'] <= TIME_WINDOW
    ]
    
    # 检查时间窗口内的请求数
    return len(client_history['mouse_positions']) > REQUEST_LIMIT

# 创建全局分析器实例
mouse_analyzer = MouseBehaviorAnalyzer()

# 修改现有的 anti_scraping_check 函数
@app.before_request
def anti_scraping_check():
    client_ip = request.remote_addr
    
    # 检查User-Agent
    if check_request_UserAgent(request.headers.get('User-Agent')):
        return json.dumps({
            "status": "error",
            "code": 430,
            "message": BAN_MESSAGE_USERAGENT
        }, ensure_ascii=False)
    
    # 检查请求频率
    if check_request_frequency(client_ip):
        return json.dumps({
            "status": "error",
            "code": 429,
            "message": BAN_MESSAGE_FREQ
        }, ensure_ascii=False)
    
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mousemove', methods=['POST'])
def handle_mousemove():
    data = request.get_json()
    client_ip = request.remote_addr
    
    is_suspicious = mouse_analyzer.analyze_movement(
        data['x'], data['y'], data['t'], client_ip
    )
    
    if is_suspicious:
        return jsonify({
            'status': 'warning',
            'message': '检测到可疑的鼠标行为模式',
            'suspicious_count': user_activities[client_ip]['suspicious_count']
        })
    
    # 检查无操作状态
    if mouse_analyzer.check_inactivity(client_ip):
        return jsonify({
            'status': 'warning',
            'message': '检测到长时间无操作'
        })
        
    return jsonify({'status': 'received'})

# ====== 启动服务 ======
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
