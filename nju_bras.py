from urllib import request,parse

print('Login to p.nju.edu.cn...')
login_data=parse.urlencode([
    ('password', 'your_password'),
    ('username', 'your_id')
])

req = request.Request('http://p.nju.edu.cn/portal_io/login')

with request.urlopen(req, data=login_data.encode('utf-8')) as f:
    print(f.read().decode('utf-8'))

