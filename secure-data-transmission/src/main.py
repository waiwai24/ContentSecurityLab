import threading
import time
import os
from channel.alist_channel import Alist
from channel.onenet_channel import OneNet
from steganography.lsb import *
from fragmentation.fragmenter import handle_fragmentation
from fragmentation.reassembler import handle_reassemble_image
from utils.color import print_color, print_success, print_update, print_warring, print_pls_send_msg, print_success_receive
from utils.generate_img import generate_random_img

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
WHITE = "\033[37m"

# 信道配置
alist_username = ""
alist_password = ""
alist_url = ""
onenet_user_id = ''
onenet_access_key = ''

# 初始化信道
userid = "user1"
# userid = "user2"
alist = Alist(alist_username, alist_password, alist_url)
onenet = OneNet(onenet_user_id, onenet_access_key)
alist.get_tmp_token()
alist.list_files()
onenet.list_files()
print_color(GREEN, "[+] 双方准备就绪，准备进行加密通信", 1)

# 监听线程
def listen_channels(stop_event):
    while not stop_event.is_set():
        flag1, filename1 = alist.update_file_list(userid)
        flag2, filename2 = onenet.update_file_list(userid)
        if flag1 and flag2:
            print_update("[*] 检测到新文件，已更新文件列表")
            handle_reassemble_image(filename1, filename2)
            lsb = LSBSteganography(channel_count=3, lsb_count=2)
            message = lsb.decode("tmp/src_image.png")
            print_success_receive()
            print_color(YELLOW, message, 1)
            os.remove("tmp/src_image.png")
        time.sleep(5)

# 发送消息线程
def send_messages(stop_event):
    while not stop_event.is_set():
        try:
            # 提示用户输入消息
            send_data = print_pls_send_msg()
            generate_random_img(240, 240)
            lsb = LSBSteganography(channel_count=3, lsb_count=2)
            lsb.encode("tmp/random.png", send_data, "tmp/send_image.png")

            upload1, upload2 = handle_fragmentation("tmp/send_image.png", userid)
            alist.upload_file(upload1)
            onenet.upload_file(upload2)
            print_success("[+] 消息发送完成")
        except Exception as e:
            print(e)
        time.sleep(5)

# 创建线程停止事件
stop_event = threading.Event()

# 创建线程
listener_thread = threading.Thread(target=listen_channels, args=(stop_event,))
sender_thread = threading.Thread(target=send_messages, args=(stop_event,))

# 启动线程
listener_thread.start()
sender_thread.start()

try:
    # 主线程保持运行
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[!] 收到退出信号，正在停止线程...")
    stop_event.set()  # 通知线程停止
    listener_thread.join()  # 等待监听线程结束
    sender_thread.join()  # 等待发送线程结束
    print("[+] 程序已安全退出")