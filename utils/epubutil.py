# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 17:31:17 2017

@author: Eric Tao
"""
import os
import zipfile
from utils import httputil
from utils import fileutil


class EpubTool:
    '''
    Epub电子书制作工具
    '''
    
    def __init__(self, book_title, save_dir):
        self._book_title = ''
        self._save_dir = ''
        self._book_dir = ''
        self._meta_inf_dir = ''
        self._ops_dir = ''
        self._ops_image_dir = ''
        self._ops_html_dir = ''
        self._chapters = []
        self._sub_chapters = {}
        self._chap_order = 0
        self._cover_image = ''
        self._setBookTitle(book_title);
        self._initSaveDir(save_dir);
         
    def _setBookTitle(self, book_title):
        '''
        设置图书名称
        '''
        self._book_title = self.filterSprcialChars(book_title)
        
    def _initSaveDir(self, save_dir):
        '''
        初始化保存目录，支持相对路径
        '''
        self._save_dir = save_dir
        bookDir = ''
        if save_dir[-1:] == '/':
            bookDir = save_dir + self._book_title
        else:
            bookDir = save_dir + '/' + self._book_title
        self._book_dir = fileutil.mkdir(bookDir)
        # create metainf dir
        self._meta_inf_dir = fileutil.mkdir(bookDir + '/' + 'META-INF')
        if not self._meta_inf_dir:
            raise EpubToolError('Create META-INF Dir [{0}] Failed!'.format('OPS'))
        # create OPS dir
        self._ops_dir = fileutil.mkdir(self._book_dir + '/' + 'OPS')
        if not self._ops_dir:
            raise EpubToolError('Create OPS Dir [{0}] Failed!'.format('OPS'))
        self._ops_image_dir = fileutil.mkdir(self._ops_dir + '/' + 'images')
        if not self._ops_image_dir:
            raise EpubToolError('Create OPS/image Dir  Failed!')
        self._ops_html_dir = fileutil.mkdir(self._ops_dir + '/' + 'html')
        if not self._ops_html_dir:
            raise EpubToolError('Create OPS/html Dir Failed!')
    
    def filterSprcialChars(self, text):
        '''
        过滤特殊字符
        '''
        text = text.replace('/','_')
        specialChars = ['\\', '/', "'", '"']
        return ''.join([c for c in text if c not in specialChars])
    
    def addChapterMenu(self, chapter_name, idx = -1):
        if idx >= 0:
            chapId = 'file_' + str(idx)
        else:
            chapId = 'file_' + str(self._chap_order)
        fileName = chapId + '.html'
        play_order = idx if idx >= 0 else self._chap_order
        _chap = {'chapter_name':chapter_name, 'file_name':fileName, 'def_id':chapId, 'play_order':play_order}
        if  idx < 0:
            self._chapters.append(_chap)
        else:
            self._chapters.insert(idx, _chap)
        return _chap
        
    def addChapter(self, chapter_name, chapter_content, idx = -1):
        '''
        添加图书章节
        '''
        # 过滤特殊字符
        chapter_name = self.filterSprcialChars(chapter_name)
        chapInfo = self.addChapterMenu(chapter_name, idx)
        fileName = chapInfo['file_name']
        
        self._chap_order += 1
        if chapter_name not in self._sub_chapters:
            self._sub_chapters[chapter_name] = []
        # 保存文件内容
        filePath = self._ops_html_dir + '/' + fileName
        print('save to {0}\n'.format(filePath))
        fileutil.writeFile(filePath, chapter_content)
    
    def addSubChapter(self, chapter_name, sub_chapter_name, sub_chapter_content):
        '''
        添加子章节
        '''
        # 过滤特殊字符
        chapter_name = self.filterSprcialChars(chapter_name)
        sub_chapter_name = self.filterSprcialChars(sub_chapter_name)
        if chapter_name not in self._sub_chapters:
            self._sub_chapters[chapter_name] = []
        # fileName = chapter_name + '_' + sub_chapter_name + '.html'
        chapId = 'file_' + str(self._chap_order)
        fileName = chapId + '.html'
        self._sub_chapters[chapter_name].append({'chapter_name':sub_chapter_name, 'file_name':fileName, 'def_id':chapId, 'play_order':self._chap_order})
        self._chap_order += 1
        # 保存文件内容
        filePath = self._ops_html_dir + '/' + fileName
        fileutil.writeFile(filePath, sub_chapter_content)
    
    def setCoverImage(self, image_name):
        '''
        设置封面图片
        '''
        self._cover_image = image_name
    
    def copyImage(self, imagePath, image_name):
        '''
        保存图片地址
        '''
        httputil.saveImage(imagePath, self._ops_image_dir+'/'+image_name)
        # 返回值主要用于替换原文件中图片的src
        return '../images/' + image_name
    
    def _createMimeTypeFile(self):
        '''
        创建mimetype文件
        '''
        fileutil.writeFile(self._book_dir+'/mimetype', 'application/epub+zip')
    
    def _createContainerFile(self):
        '''
        创建container.xml文件
        '''
        metaInfContent = '''<?xml version="1.0"?>
    <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
            <rootfile full-path="OPS/content.opf" media-type="application/oebps-package+xml"/>
        </rootfiles>
    </container>
        '''
        fileutil.writeFile(self._meta_inf_dir+'/container.xml', metaInfContent)
    
    def _createTocNcxFile(self):
        '''
        创建toc.ncx文件
        '''
        filePath = self._ops_dir + '/toc.ncx'
        tocContent = '''<?xml version='1.0' encoding='utf-8' ?>
    <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
        <head>
            <meta charset="UTF-8"/>
        </head>
        <docTitle>
            <text>{title}</text>
        </docTitle>
        <docAuthor>
            <text>Eric Tao</text>
        </docAuthor>
        <navMap>
        {navs}
        </navMap>
    </ncx>
        '''
        navs = ''
        for chapter in self._chapters:
            navItem = '''
                <navPoint id="{def_id}" playOrder="{play_order}">
                    <navLabel>
                        <text><![CDATA[{chapter_title}]]></text>
                    </navLabel>
                    <content src="{file_path}" />
                    {sub_navs}
                </navPoint>
            '''
            sub_navs = ''
            if chapter['chapter_name'] in self._sub_chapters:
                # playOrder = idx
                for subChapter in self._sub_chapters[chapter['chapter_name']]:
                    sub_navs += self.__getChapterNav(subChapter)
            navs += navItem.format(def_id=chapter['def_id'], play_order=chapter['play_order'], chapter_title=chapter['chapter_name'], file_path='html/'+chapter['file_name'], sub_navs=sub_navs)
        fileutil.writeFile(filePath, tocContent.format(title=self._book_title, navs=navs))
    
    def __getChapterNav(self, chapter):
        navItem = '''
                <navPoint id="{def_id}" playOrder="{play_order}">
                    <navLabel>
                        <text><![CDATA[{chapter_title}]]></text>
                    </navLabel>
                    <content src="{file_path}" />
                </navPoint>
        '''
        nav = navItem.format(def_id=chapter['def_id'], play_order=chapter['play_order'], chapter_title=chapter['chapter_name'], file_path='html/'+chapter['file_name'])
        return nav
    
    def _createContentOpfFile(self):
        '''
        创建content.opf文件
        '''
        filePath = self._ops_dir + '/content.opf'
        opfContent = '''<?xml version='1.0' encoding='utf-8'?>
        <package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uuid_id">
            <metadata xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:calibre="http://calibre.kovidgoyal.net/2009/metadata" xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>{book_title}</dc:title>
                <dc:language>en</dc:language>
                <dc:publisher xmlns:dc="http://purl.org/dc/elements/1.1/">Eric Tao</dc:publisher>
                <dc:description xmlns:dc="http://purl.org/dc/elements/1.1/">{book_title}</dc:description>
                <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">en</dc:language>
                <dc:creator opf:role="aut" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">Eric Tao</dc:creator>
                <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">{book_title}</dc:title>
                <dc:date xmlns:dc="http://purl.org/dc/elements/1.1/">2016-12-30</dc:date>
                <dc:contributor opf:role="bkp" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">Eric Tao</dc:contributor>
                <meta name="cover" content="cover"/>
            </metadata>
                <manifest>
                    <!-- Content Documents -->
                    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
                    {manifest}
                </manifest>
                <spine toc="ncx">
                {spine}
                </spine>
            <guide>
            </guide>
        </package>
        '''
        manifest = ''
        spine = ''
        # set cover image
        if self._cover_image:
            manifest += '<item id="cover" href="images/{0}" media-type="image/*"/>'.format(self._cover_image)
        for chapter in self._chapters:
            manifest += '<item id="{def_id}" href="html/{file_name}" media-type="application/xhtml+xml"/>\n'.format(def_id=chapter['def_id'], file_name=chapter['file_name'])
            spine += '<itemref idref="{def_id}" linear="yes" />\n'.format(def_id=chapter['def_id'])
            if chapter['chapter_name'] in self._sub_chapters:
                for subChapter in self._sub_chapters[chapter['chapter_name']]:
                    manifest += '<item id="{def_id}" href="html/{file_name}" media-type="application/xhtml+xml"/>\n'.format(def_id=subChapter['def_id'], file_name=subChapter['file_name'])
                    spine += '<itemref idref="{def_id}" linear="yes" />\n'.format(def_id=subChapter['def_id'])
        fileutil.writeFile(filePath, opfContent.format(book_title=self._book_title, manifest=manifest, spine=spine))
    
    def _makeEpub(self):
        '''
        生成epub文件
        '''
        source_dir = self._book_dir + '/'
        output_filename = self._book_title + '.epub'
        zipf = zipfile.ZipFile(output_filename, 'w')
        pre_len = len(os.path.dirname(source_dir))
        for parent, dirnames, filenames in os.walk(source_dir):
            for filename in filenames:
                pathfile = os.path.join(parent, filename)
                arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
                zipf.write(pathfile, arcname)
        zipf.close()
    
    def make(self):
        '''
        生成电子书
        '''
        # 创建mimetype文件
        self._createMimeTypeFile()
        # 创建container.xml文件
        self._createContainerFile()
        # 创建toc.ncx文件
        self._createTocNcxFile()
        # 创建content.opf文件
        self._createContentOpfFile()
        # 生成epub文件
        self._makeEpub()


class EpubToolError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
