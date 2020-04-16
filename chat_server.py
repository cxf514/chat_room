"""
chat room
env: python3.6
socket udp  and process
【1】 有人进入聊天室需要输入姓名，姓名不能重复

【2】 有人进入聊天室时，其他人会收到通知：xxx 进入了聊天室

【3】 一个人发消息，其他人会收到：xxx ： xxxxxxxxxxx

【4】 有人退出聊天室，则其他人也会收到通知:xxx退出了聊天室

【5】 扩展功能：服务器可以向所有用户发送公告:管理员消息： xxxxxxxxx

【6】 扩展功能2：•	增加敏感词汇 : xx aa bb oo
               •	当有成员聊天内容中包含敏感词汇，则进行屏蔽，并且向群里 发出对xxx的警告信息
               •	如果一个人被警告三次则踢出该群，同时拉黑这个地址
"""
from multiprocessing import Process
from socket import *

# 服务器地址
HOST = "0.0.0.0"
PORT = 8888
ADDR = (HOST, PORT)
# 用户信息存储 {name:[address,警告次数]}
user = {}
sensitive_word = ["xx", "aa", "bb", "oo"]
blacklist = []


# 处理进入聊天室请求
def do_login(s, name, address):
    if name in user:
        s.sendto("该用户已存在".encode(), address)
    elif address[0] in [a for a,b in blacklist]:
        s.sendto("此IP被永久禁止登入".encode(), address)
    else:
        msg = f"欢迎{name}进入聊天室"
        s.sendto(b'ok', address)
        for i in user:
            s.sendto(msg.encode(), user[i][0])
        user[name] = [address, 0]


# 处理聊天请求
def do_chat(s, text):
    name=text.split(":")[0]
    # 敏感字列表为空
    if not [i for i in sensitive_word if i in text.split(":")[1]]:
        for i in list(user.keys()):
            if i != name:
                s.sendto(text.encode(), user[i][0])
    else:
        user[name][1] += 1
        if user[name][1] <= 2:
            for i in list(user.keys()):
                msg = f"用户{name}聊天内容存在敏感字，第{user[name][1]}次警告"
                s.sendto(msg.encode(), user[i][0])
        else:
            for i in list(user.keys()):
                msg = f"用户{text.split(':')[0]}聊天内容存在敏感字，已满三次，从此封号"
                s.sendto(msg.encode(), user[i][0])
            do_shot(s, name)


# 处理踢出请求
def do_shot(s, name):
    blacklist.append(user[name][0])
    msg = "0hds9k23d32s32g92"
    s.sendto(msg.encode(), user[name][0])
    del user[name]  # 删除用户
    msg = f"{name}被踢出聊天室"
    for i in list(user.keys()):
        s.sendto(msg.encode(), user[i][0])


# 处理退出请求
def do_quit(s, name):
    del user[name]  # 删除用户
    msg = f"{name}退出了聊天室"
    for i in list(user.keys()):
        s.sendto(msg.encode(), user[i][0])


# 接收各个客户端请求
def request(s):
    while True:
        data, addr = s.recvfrom(1024)  # 就收请求
        tmp = data.decode().split(' ', 1)  # 对请求解析,2 最多分割两次
        if tmp[0] == "L":
            do_login(s, tmp[1], addr)
        elif tmp[0] == "C":
            do_chat(s, tmp[1])
        elif tmp[0] == "Q":
            do_quit(s, tmp[1])
        elif tmp[0] == "M":
            do_chat(s, tmp[1])


def manager(s):
    while True:
        msg = input(">>")
        msg = f"M 管理员:{msg}"
        s.sendto(msg.encode(), ADDR)


# 搭建基本结构
def main():
    # 创建一个udp套接字
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(ADDR)
    p = Process(target=request, args=(s,))
    p.start()
    manager(s)  # 处理发来的请求
    p.join()


if __name__ == '__main__':
    main()
