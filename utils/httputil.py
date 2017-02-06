# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 17:46:33 2017

@author: Eric Tao
"""
import os
import urllib
from urllib.request import urlopen
from urllib.error import HTTPError
import gzip

def buildLink(prefix, relUrl):
    if relUrl[:4] == 'http':
        return relUrl
    if prefix[-1:] != '/':
        prefix += '/'
    if relUrl[:1] == '/':
        url = prefix + relUrl[1:]
    else:
        url = prefix + relUrl
    return url


def getHtml(url, coding='utf-8'):
    try:
        urlConn = urlopen(url)
        html = urlConn.read()
        doc = ''
        try:
            if not coding:
                coding = 'utf-8'
            doc = gzip.decompress(html).decode(coding)
        except:
            doc = html
        
        if not doc:
            return ''
            
        return doc
    except HTTPError as he:
        print('HTTPError: ' + he.msg)
    except Exception as other:
        print('httputil::getHtml Exception:' + str(other))
    return ''


def saveImage(imgUrl, targetFile):
    try:
        print('save img {0} to {1} \n'.format(imgUrl, targetFile))
        if os.path.exists(targetFile):
            print('{0} already exists!'.format(targetFile))
            return
        urllib.request.urlretrieve(imgUrl, targetFile)
    except Exception as e:
        print('httputil::saveImage exception: ' + str(e), end='\n')


'''
def saveImage(imgUrl,savePath):
    try:
        print('save img {0} to {1} \n'.format(imgUrl, savePath))
        if os.path.exists(savePath):
            print('{0} already exists!'.format(savePath))
            return
        conn = urlopen(imgUrl)
        try:
            data = gzip.decompress(conn.read())
        except:
            data = conn.read()
        with open(savePath, 'wb+') as imgFile:
            imgFile.write(data)
            imgFile.flush()
        return True
    except Exception as e:
        print(str(e))
    return False
'''
