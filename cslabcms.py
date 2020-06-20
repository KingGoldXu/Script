# encoding: utf-8
import sys
import io
import requests
import re
import urllib.parse
import os


def download_homeworks(url, cookies, dir):
    headers = {
        'Host': 'cslabcms.nju.edu.cn',
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Connection': 'keep-alive'
    }
    resp = requests.get(url, headers=headers, cookies=cookies)
    fupt = re.compile(r'http://cslabcms.nju.edu.cn/pluginfile.php/[^"]*')
    file_urls = fupt.findall(resp.content.decode('utf-8'))
    for url in file_urls:
        file_name = url[url.rfind('/')+1:url.rfind('?')]
        file_name = urllib.parse.unquote(file_name)
        r = requests.get(url, headers=headers, cookies=cookies, stream=False)
        with open(os.path.join(dir, file_name), 'wb') as f:
            f.write(r.content)


def main():
    cookies = {
        'MOODLEID1_': 'f%2519%25A1%2503%2513%25E8%2510r%25C2',
        'MoodleSession': '1avf5tj30vgbnfje8ufjqltel1'
    }
    url_format = 'http://cslabcms.nju.edu.cn/mod/assign/view.php?id={}'
    url_ids = [7338, 7461, 7339, 7462, 7337, 7463]
    dirs = ['./lab3-1', './lab4-1', './lab3-2',
            './lab4-2', './lab3-3', './lab4-3']
    for url_id, dir in zip(url_ids, dirs):
        download_homeworks(url_format.format(url_id), cookies, dir)


if __name__ == '__main__':
    main()
