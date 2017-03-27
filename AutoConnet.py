from urllib import request,parse
from urllib.error import *
import http.cookiejar
import time

login_data=parse.urlencode([
    ('password', '******'),
    ('username', '******')
])

online_data=parse.urlencode([
    ('page',1),
	('rows',20)
])

def getCurrentUserInfo():
    req=request.Request('http://p.nju.edu.cn/portal_io/getinfo')
    with request.urlopen(req) as f:
        return f.read().decode('utf-8')

def isOnline(msg):
    return msg.find('"reply_code":0')!=-1
	
def login(login_data):   
    print('Login to p.nju.edu.cn...')
    req = request.Request('http://p.nju.edu.cn/portal_io/login')
    with request.urlopen(req, data=login_data.encode('utf-8')) as f:
        return f.read().decode('utf-8')
		
def isLoginSuccess(msg):
    return msg.find('"reply_code":1')!=-1 or msg.find('"reply_code":6')!=-1

def printUserInfo(msg):
    dict=eval(msg)
    userinfo=dict['userinfo']
    print('\t全名:\t%-20s\t\t学号:\t%s'%(userinfo['fullname'],userinfo['username']))
    print('\t区域:\t%-20s\t\t余额:\t%.2f'%(userinfo['area_name'],userinfo['balance']/100.0))
	
def loginBrasAndCheckOnline():
    login=request.Request('http://bras.nju.edu.cn:8080/manage/self/auth/login')
    online=request.Request('http://bras.nju.edu.cn:8080/manage/self/online/getlist')
    cj=http.cookiejar.CookieJar()
    opener=request.build_opener(request.HTTPCookieProcessor(cj))
    loginmsg=opener.open(login,data=login_data.encode('utf-8')).read().decode('utf-8')
    onlinemsg=opener.open(online,data=online_data.encode('utf-8')).read().decode('utf-8')
    opener.close()
    return loginmsg,onlinemsg
	
def isBrasLoginSuccess(msg):
    return msg.find('"reply_code":0')!=-1
	
def onlineDeviceNum(msg):
    msg=msg.replace('null','None')
    dic=eval(msg)
    if dic['reply_code']!=0:
        return None
    else:
        return dic['total']
	
def main():
    while True:
        try:
            if not isOnline(getCurrentUserInfo()):
                lmsg,omsg = loginBrasAndCheckOnline()
                if onlineDeviceNum(omsg)==1:
                    print('Other device is online!')
                if not isBrasLoginSuccess(lmsg):
                    print("Can't login bras.nju!")
                if onlineDeviceNum(omsg)==0:
                    print('No device online! Try to login...')
                    msg=login(login_data)
                    if isLoginSuccess(msg):
                        print('Login success!!!')
                        printUserInfo(msg)
                    else:
                        print('Login failed!!!')
        except URLError:
            print('URLError')
        time.sleep(20)
    
if __name__ == "__main__":
    main()
