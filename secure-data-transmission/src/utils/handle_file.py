import os

def store2file(data, file_path):
    with open(file_path, 'w') as f:
        f.write(data)

def read2msg(file_path):
    with open(file_path, 'r') as f:
        return f.read()
    
def namesrcfile(username, time_hash, channel=None):
    # time_hash = hashlib.md5(str(time.time()).encode()).hexdigest()
    filename = f"tmp/{username}_{time_hash}_{channel}.txt"
    return filename

def namechannel1file(username, time_hash):
    filename = f"tmp/{username}_{time_hash}_channel1.txt"
    return filename

def namechannel2file(username, time_hash):
    filename = f"tmp/{username}_{time_hash}_channel2.txt"
    return filename

def deletefile(file_path):
    os.remove(file_path)

def mkdir(dir_path):
    os.makedirs(dir_path, exist_ok=True)
    
def getinput2file(input, user, time_hash, channel=None):
    filename = namesrcfile(user, time_hash, channel)
    store2file(input, filename)
    return filename
    
# getin = input("请输入要发送的内容：")
# getinput2file(getin, "user1")
    
    
# test
# filename = namefile("user1")
# store2file("hello", filename)
# mkdir("../tmp/1")