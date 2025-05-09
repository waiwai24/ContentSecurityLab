from PIL import Image
from io import BytesIO
import math
import numpy
import base64
from utils import handle_file
import os
import time
import hashlib

# fragmenter 一次处理一张图片
# 但是生成的是两个通道的数据（xor）

# 对图片进行进行上下左右4分片
# 0 2
# 1 3
def fragment_image(image_path):
    image = Image.open(image_path)
    width, height = image.size
    fragment_width = math.ceil(width / 2)
    fragment_height = math.ceil(height / 2)
    
    fragments = []
    for i in range(2):
        for j in range(2):
            x = i * fragment_width
            y = j * fragment_height
            right = min(x + fragment_width, width)
            bottom = min(y + fragment_height, height)
            fragment = image.crop((x, y, right, bottom))
            fragments.append(fragment)
            
    return fragments

# 0-3，1-2进行xor处理
def xor_fragments_image(fragments):
    xor_fragments = []
    arr0 = numpy.array(fragments[0])
    arr1 = numpy.array(fragments[1]) 
    arr2 = numpy.array(fragments[2])
    arr3 = numpy.array(fragments[3])
    
    xor_result1 = numpy.bitwise_xor(arr0, arr3)
    xor_result2 = numpy.bitwise_xor(arr1, arr2)
    
    xor_fragments.append(Image.fromarray(xor_result1))
    xor_fragments.append(Image.fromarray(xor_result2))
    xor_fragments.append(fragments[2])
    xor_fragments.append(fragments[3])
    return xor_fragments

# 左右拼接两张图片
def concat_images_horizontal(image1, image2):
    width1, height1 = image1.size
    width2, height2 = image2.size
    new_width = width1 + width2
    new_height = max(height1, height2)
    new_image = Image.new('RGB', (new_width, new_height))
    
    # 将第一张图片粘贴到左侧，将第二张图片粘贴到右侧
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (width1, 0))
    
    return new_image

# 将0-3与2拼接，1-2与3拼接
def handle_send_image(fragments):
    xor_fragments = xor_fragments_image(fragments)
    send_fragments = []
    
    # 拼接第1和第3片段
    send1 = concat_images_horizontal(xor_fragments[0], xor_fragments[2])
    # 拼接第2和第4片段
    send2 = concat_images_horizontal(xor_fragments[1], xor_fragments[3])
    
    send_fragments.append(send1)
    send_fragments.append(send2)
    
    return send_fragments

# 将图片转换为base64
def image_to_base64(image):
    image = Image.open(image).convert("RGB")
    image_bytes = BytesIO()
    image.save(image_bytes, format="PNG")
    return base64.b64encode(image_bytes.getvalue()).decode('utf-8')

def handle_fragmentation(send_image_path, username):
    fragments = fragment_image(send_image_path)
    send_fragments = handle_send_image(fragments)
    for i, fragment in enumerate(send_fragments): 
        fragment.save(f"tmp/fragment_{i}.png")
    send_msg_channel1 = image_to_base64('tmp/fragment_0.png')
    send_msg_channel2 = image_to_base64('tmp/fragment_1.png')
    time_hash = hashlib.md5(str(time.time()).encode()).hexdigest()
    name1 = handle_file.getinput2file(send_msg_channel1, username, time_hash, "channel1")
    name2 = handle_file.getinput2file(send_msg_channel2, username, time_hash, "channel2")
    with open(name1 , "wb") as f:
        f.write(send_msg_channel1.encode())
    with open(name2 , "wb") as f:
        f.write(send_msg_channel2.encode())
    os.remove("tmp/fragment_0.png")
    os.remove("tmp/fragment_1.png")
    os.remove("tmp/send_image.png")
    os.remove("tmp/random.png")
    
    return name1, name2
    
