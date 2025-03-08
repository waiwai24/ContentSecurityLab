import json
import os

# 定义 JSON 文件路径
json_file_path = './db/test.json'

def append_to_json(data, label):
    # 如果文件存在，读取现有数据
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    # 格式化数据
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
        ]
    }

    # 将新数据添加到外层字典中
    existing_data[label] = formatted_item

    # 写入 JSON 文件
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)

# 示例数据
data = [
    '为何有人说三亚景色不输泰国，中国游客却更爱去泰国？',
    '2025-03-04 14:39',
    '4 个回答',
    '30 个关注',
    '这是提问内容',
    '2 人回答',
    [
        ['Peter Tam', '2025-03-04', '336', '说的太对了。'],
        ['Jimmm', '2025-03-04', '120', '其实这个根本上还是供需问题。']
    ]
]

# 调用函数，指定标签
append_to_json(data, '1')

# 再次调用，添加更多数据
data2 = [
    '另一个问题标题',
    '2025-03-05 10:00',
    '5 个回答',
    '40 个关注',
    '这是另一个提问内容',
    '3 人回答',
    [
        ['Alice', '2025-03-05', '200', '这是一个很好的问题。'],
        ['Bob', '2025-03-05', '150', '我也有同感。']
    ]
]

append_to_json(data2, '2')