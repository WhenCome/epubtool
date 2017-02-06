# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 17:36:33 2017

@author: Eric Tao
"""

import os

def mkdir(dir):
    try:
        if os.path.exists(dir):
            return dir
        os.mkdir(dir)
        if os.path.exists(dir):
            return dir
    except Exception as e:
        print('Create Dir {0} Failed. {1}'.format(dir, str(e)))
    return ''

def writeFile(filePath, content):
    '''
    创建文件并写入内容
    '''
    with open(filePath, 'w') as file:
        file.write(content)
        file.flush()
        file.close()
