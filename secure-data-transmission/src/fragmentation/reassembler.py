from PIL import Image
import base64
import numpy
import math
import io

#reassembler 从两个通道中接收的msg恢复出各通道的图片并恢复原图

# 将base64转换为图片并保存
def base64_to_image(base64_data_path):
    with open(base64_data_path, "rb") as f:
        base64_data = f.read()
    image_data = base64.b64decode(base64_data)
    image = Image.open(io.BytesIO(image_data))
    image.save(f"{base64_data_path}.png")
    
# 将图片分为左右两部分
def divide_image_around(image_data):
    if isinstance(image_data, str):
        image = Image.open(image_data)
        image_array = numpy.array(image)
    elif isinstance(image_data, Image.Image):
        image_array = numpy.array(image_data)
    else:
        image_array = image_data
    
    height, width = image_array.shape[:2]
    fragment_width = math.ceil(width / 2)
    left_fragment = image_array[:, :fragment_width]
    right_fragment = image_array[:, fragment_width:width]
    
    fragments = []
    fragments.append(left_fragment)
    fragments.append(right_fragment)
    
    return fragments

# 将图片左右两部分合并
def merge_image_around(receive_msg_img1, receive_msg_img2, width, height):
    if isinstance(receive_msg_img1, Image.Image):
        image_left = receive_msg_img1
    else:
        image_left = Image.fromarray(receive_msg_img1)
        
    if isinstance(receive_msg_img2, Image.Image):
        image_right = receive_msg_img2
    else:
        image_right = Image.fromarray(receive_msg_img2)
        
    new_width = width
    new_height = height
    new_image = Image.new('RGB', (new_width, new_height))
    new_image.paste(image_left, (0, 0))
    new_image.paste(image_right, (width//2, 0))
    return new_image
    
# 将上下图片合并并保存
def merge_image_up_down(receive_msg_img1, receive_msg_img2, width, height):
    if isinstance(receive_msg_img1, Image.Image):
        image_up = receive_msg_img1
    else:
        image_up = Image.fromarray(receive_msg_img1)
        
    if isinstance(receive_msg_img2, Image.Image):
        image_down = receive_msg_img2
    else:
        image_down = Image.fromarray(receive_msg_img2)
        
    new_image = Image.new('RGB', (width, height * 2))
    new_image.paste(image_up, (0, 0))
    new_image.paste(image_down, (0, height))
    return new_image

# 计算图片大小
def calculate_image_size(image_path):
    image = Image.open(image_path)
    width, height = image.size
    return width, height

# 再次xor, 恢复原始图片
def handle_receive_image(receive_msg_img1, receive_msg_img2, width, height):
    # 首先将图片路径转换为PIL Image对象
    if isinstance(receive_msg_img1, str):
        img1_path = receive_msg_img1
        img1 = Image.open(img1_path)
    else:
        img1 = receive_msg_img1
        
    if isinstance(receive_msg_img2, str):
        img2_path = receive_msg_img2
        img2 = Image.open(img2_path)
    else:
        img2 = receive_msg_img2
    
    # 将PIL Image对象转换为numpy数组以便进行XOR操作
    img1_array = numpy.array(img1)
    img2_array = numpy.array(img2)
    
    # 分割图片
    img1_fragments = divide_image_around(img1_array)
    img2_fragments = divide_image_around(img2_array)
    
    # XOR操作
    fragment1 = numpy.bitwise_xor(img1_fragments[0], img2_fragments[1])
    fragment2 = numpy.bitwise_xor(img2_fragments[0], img1_fragments[1])
    
    # 合并图片
    fragment1_3 = merge_image_around(fragment1, img1_fragments[1], width, height)
    fragment2_4 = merge_image_around(fragment2, img2_fragments[1], width, height)
    src_img = merge_image_up_down(fragment1_3, fragment2_4, width, height)
    src_img.save("tmp/src_image.png")
    
def handle_reassemble_image(receive_msg_img1, receive_msg_img2):
    receive_msg_img1 = f"tmp/{receive_msg_img1}"
    receive_msg_img2 = f"tmp/{receive_msg_img2}"
    
    base64_to_image(receive_msg_img1)
    base64_to_image(receive_msg_img2)
    width, height = calculate_image_size(receive_msg_img1 + ".png")
    handle_receive_image(receive_msg_img1 + ".png", receive_msg_img2 + ".png", width, height)
    
# 测试
# base64_to_image("send_msg_channel1")
# base64_to_image("send_msg_channel2")
# width, height = calculate_image_size("send_msg_channel1.png")
# handle_receive_image("send_msg_channel1.png", "send_msg_channel2.png", width, height)



