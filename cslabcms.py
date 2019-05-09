# encoding: utf-8
import sys
import io
import requests
import re
import urllib.parse


url = 'http://cslabcms.nju.edu.cn/mod/assign/view.php?id=6666'

cookies = {
    'MOODLEID1_' : 'f%2519%25A1%2503%2513%25E8%2510r%25C2',
    'MoodleSession': 'kl47lslmrf35upgmk0e47ngcb2'
}

headers = {
    'Host': 'cslabcms.nju.edu.cn',
    'User-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Connection': 'keep-alive'
}

resp = requests.get(url, headers=headers, cookies=cookies)
fupt = re.compile(r'http://cslabcms.nju.edu.cn/pluginfile.php/[^"]*')
file_urls = fupt.findall(resp.content.decode('utf-8'))
for url in file_urls:
    file_name = url[url.rfind('/')+1:url.rfind('?')]
    file_name = urllib.parse.unquote(file_name)
    r = requests.get(url, headers=headers, cookies=cookies, stream=False)
    with open(file_name, 'wb') as f:
        f.write(r.content)
