# 定义一些常用的颜色代码
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
WHITE = "\033[37m"

def print_color(color, message, newline_flag):
    if newline_flag:
        print(f"{color}{message}{RESET}")
    else:
        print(f"{color}{message}{RESET}", end="")
        
def print_warring(message):
    print_color(YELLOW, "[!]", 0)
    print_color(RED, " Waring: ", 0)
    print_color(RED, message, 1)

def print_success(message):
    print_color(GREEN, "[+]", 0)
    print_color(GREEN, " Success ===> ", 0)
    print_color(GREEN, message, 1)
    
def print_update(message):
    print_color(GREEN, "[+]", 0)
    print_color(GREEN, " Update: ", 0)
    print_color(GREEN, message, 1)

def print_pls_send_msg():
    print_color(GREEN, "[*]", 0)
    print_color(BLUE, " Please send message: ", 1)
    data = input()
    return data
    
def clear_last_line():
    print('\033[F', end='') # Move cursor to the beginning of the line
    print('\033[K', end='') # Clear from cursor to end of line
    
    
# print_warring("这是一个警告信息")
# print_pls_send_msg()
# print_success("这是一个成功信息")

