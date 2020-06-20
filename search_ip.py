#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import subprocess
import re
import socket
import paramiko

def ip(file, field):
    ip_field = field
    ip_file = open(file, 'w')
    for i in range(1,256):
        ip = '{}.{}\n'.format(ip_field, i)
        ip_file.write(ip)
    ip_file.close()

def test_ip(file, user, passwd):
    file = open(file, 'r')
    ip_list = []
    port = 22
    f = open('login_ip.txt', 'w')
    for line in file.readlines():
        line=line.strip("\n")
        ip_list.append(line)
    for ip in ip_list:
        p = subprocess.Popen(["ping -c 1 {}".format(ip)],
                             stdin = subprocess.PIPE,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE,
                             shell = True)
        out = p.stdout.read().decode('utf-8', 'ignore')
        regex = re.compile("time=\d*", re.IGNORECASE | re.MULTILINE)
        if len(regex.findall(out)) > 0:
            print('{} : Host Up!'.format(ip))
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                s.connect((ip, int(port)))
                s.shutdown(2)
                print('{} is open'.format(port))
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip, 22, user, passwd)
                    # stdin, stdout, stderr = ssh.exec_command('你的命令')
                    # print stdout.readlines()
                    ssh.close()
                    print('Login successful')
                    # f = open('login_ip.txt', 'w')
                    f.write(ip + '\n')
                    # return True
                except:
                    print('The login problem, please check your username and password')
            except:
                print('{} is down'.format(port))
                # return False
        else:
            print('{} : Host Down!'.format(ip))
    file.close()
    f.close()

if __name__ == "__main__":
    user = 'zsw'
    passwd = 'Ase=1234'
    ip('test80', '114.212.80')
    test_ip('test80', user, passwd)
