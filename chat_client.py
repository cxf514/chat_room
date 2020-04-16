"""
chat room
客户端
功能: 发送请求, 获取结果
"""

from socket import *
from multiprocessing import Process, Queue
import sys
from time import sleep

# 服务器地址
ADDR = ('127.0.0.1', 8888)
selfip = ('127.0.0.1', 52870)
q = Queue()


# 接收消息
def recv_msg(s, name):
    while True:
        data, addr = s.recvfrom(1024)
        if data.decode() == "0hds9k23d32s32g92":
            q.put("0")
        else:
            print("\n" + data.decode()+"\n", end="")


# 发送消息
def send_msg(s, name):
    while True:
        if q.empty():
            try:
                msg = input(">>")
            except KeyboardInterrupt:
                msg = 'quit'
            if msg == 'quit':
                msg = f"Q {name}"
                s.sendto(msg.encode(), ADDR)
                sys.exit("您已退出群聊")
            msg = f"C {name}:{msg}"
            s.sendto(msg.encode(), ADDR)
            sleep(0.5)
        else:
            sys.exit("您已退出群聊")


# 网络结构
def main():
    s = socket(AF_INET, SOCK_DGRAM)
    # 进入聊天室
    while True:
        name = input("输入用户名")
        msg = "L" + " " + name
        s.sendto(msg.encode(), ADDR)
        data, addr = s.recvfrom(127)  # 接收反馈
        if data.decode() == 'ok':
            print("您已进入聊天室")
            break
        else:
            print(data.decode())
    # 创建一个进程

    p = Process(target=recv_msg, args=(s, name))
    p.daemon = True  # 子进程随父进程结束而结束
    p.start()

    # 发送消息
    send_msg(s, name)  # 发送消息由父进程执行


if __name__ == '__main__':
    main()
