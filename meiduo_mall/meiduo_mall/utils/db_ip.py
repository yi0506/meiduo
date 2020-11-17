# -*- coding: UTF-8 -*-
import socket


def get_db_ip():
    """获取数据库ip"""
    # 获取计算机名称
    hostname = socket.gethostname()
    # 获取本机IP
    host_ip = socket.gethostbyname(hostname)

    db_ip = "192.168.192.133" if host_ip in ["172.24.178.15", "192.168.192.1"] else "192.168.72.129"  # 192.168.72.1
    return db_ip


if __name__ == '__main__':
    pass
