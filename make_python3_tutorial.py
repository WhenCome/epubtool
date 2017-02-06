# -*- coding: utf-8 -*-
import sys
from utils import httputil
from utils import epubutil
from bs4 import BeautifulSoup

def getChapters():
    '''
    Get chapter list
    '''
    url = 'http://www.python-course.eu/python3_course.php'
    host = 'http://www.python-course.eu/'
    html = httputil.getHtml(url)
    if not html:
        return None
    try:
        chapters = []
        bsObj = BeautifulSoup(html, 'html.parser')
        menuBox = bsObj.find('div', {'class':'menu'})
        lis = menuBox.findAll('li')
        for li in lis:
            link = li.find('a')
            chapters.append({'title':link.get_text(),'url':host+link.attrs['href']})
        return chapters
    except Exception as e:
        print('getChapters Exception: ' + str(e))
    return None

def getContent(url, host):
    '''
    Get chapter content
    '''
    try:
        html = httputil.getHtml(url)
        if not html:
            return ''
        bsObj = BeautifulSoup(html, 'html.parser')
        contentBox = bsObj.find('div', {'id':'content'})
        # call twice
        ctl = contentBox.find('div', {'id':'contextlinks'})
        if ctl:
            ctl.replace_with('')
        ctl = contentBox.find('div', {'id':'contextlinks'})
        if ctl:
            ctl.replace_with('')
        # save images
        imgs = contentBox.findAll('img')
        if imgs:
            for img in imgs:
                if 'src' not in img.attrs:
                    continue
                imgUrl = img.attrs['src']
                if imgUrl[0:5] != 'http':
                    imgUrl = host + imgUrl
                saveName = imgUrl[imgUrl.rfind('/')+1:]
                newPath = saveNetImage(imgUrl, saveName)
                img['src'] = newPath
        return str(contentBox)
    except Exception as e:
        print('getContent Exception: ' + str(e))
    return ''


def buildChapterContent(title, rawContent):
    html = '''
    <!Doctype html>
    <html>
    <head>
    	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    	<meta name="viewport" content="width=device-width, initial-scale=1.0" />  
    	<title>{0}</title>
     <style type="text/css">
         pre {{
            margin: 15px auto;
            font: 12px/20px 'courier new';
            white-space: pre-wrap;
            word-break: break-all;
            word-wrap: break-word;
            border: 1px solid #ddd;
            border-left-width: 4px;
            padding: 10px 15px;
         }}
     </style>
    </head>
    <body>
    {1}
    </body>
    </html>
    '''
    return html.format(title, rawContent)


def saveNetImage(imgUrl, saveName):
    global epub
    print('save image {0} as {1}\n'.format(imgUrl, saveName))
    return epub.copyImage(imgUrl, saveName)

chapters = getChapters()
bookName = 'Python 3 Tutorial'
if not chapters:
    print('get chapters failed')
    sys.exit()

host = 'http://www.python-course.eu/'
epub = epubutil.EpubTool(bookName, './test')
for chapter in chapters:
    print('{0}, url:{1}\n'.format(chapter['title'], chapter['url']))
    chapContent = getContent(chapter['url'], host)
    chapterContent = buildChapterContent(chapter['title'], chapContent)
    epub.addChapter(chapter['title'], chapterContent)
epub.make()


