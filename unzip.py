import zipfile
import os
import shutil
import re

file_list = os.listdir(r'.')
student_id = re.compile(r'[0-9]{9}')
dir = 'unziped/'

if not os.path.exists(dir):
    os.mkdir(dir)
    
for file_name in file_list:
    if os.path.splitext(file_name)[1] == '.zip':
        id = student_id.findall(file_name)
        if len(id) != 1:
            continue
        id = id[0]
        print(file_name)
        unzip_path = dir + id + '/'
        print(unzip_path)
        if os.path.exists(unzip_path):
            continue
        os.mkdir(unzip_path)
        
        file_zip = zipfile.ZipFile(file_name, 'r')
        for file in file_zip.namelist():
            if 'lab/' in file:
                origin = file[:file.rindex('lab/')]
                file_zip.extract(file, unzip_path)
        if os.path.exists(unzip_path + origin + 'lab/'):
            shutil.move(unzip_path + origin + 'lab/', unzip_path + 'lab/')
        else:
            print(unzip_path + " unzip failed!!!")
            continue
