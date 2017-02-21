from urllib import request,parse

print('Login to p.nju.edu.cn...')
login_data=parse.urlencode([
    ('password', 'xsb857442867'),
    ('username', '131220144')
])

req = request.Request('http://p.nju.edu.cn/portal_io/login')

with request.urlopen(req, data=login_data.encode('utf-8')) as f:
    print(f.read().decode('utf-8'))

