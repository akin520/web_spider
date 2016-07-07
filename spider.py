#!/usr/bin/env python
#coding:utf-8

import urllib
import urllib2
import os, uuid, shutil
import time
import tarfile
from bs4 import BeautifulSoup
import random
import string
import model

from celery import Celery

# app = Celery('tasks')
# app.config_from_object('celeryconfig')
# url='http://jandan.net/ooxx'
app = Celery('tasks', broker='redis://127.0.0.1:6379/0')
app.conf.CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
http_header =  [{'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/48.0.2564.82 Safari/537.36'},
                {'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'},
                {'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3', 'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)'}]


def get_html(url):
    try:
        request = urllib2.Request(url, headers=random.choice(http_header))
        obj = urllib2.urlopen(request)
        if obj.getcode() == 200:
            html = obj.read()
            return html
    except Exception as e:
        return False


def tar_file(src=u'./static/',path=u'./temp', filename=u'test.tar.gz'):
    tar = tarfile.open(os.path.join(src, filename), "w:gz")
    for root, dir, files in os.walk(path):
        for file in files:
            fullpath = os.path.join(root, file)
            tar.add(fullpath)
    tar.close()
    # os.rmdir(path)
    shutil.rmtree(path)


def get_url(url, xpath='a', xlink='href', findpath='/'):
    print url,findpath
    urls = []
    html = get_html(url)
    if html:
        soup = BeautifulSoup(html)
        links = soup.find_all(xpath)
        for link in links:
            try:
                url = link[xlink]
            except:
                pass
            # print url
            if url.startswith('http://') and url.find(findpath) != -1:
                urls.append(url)
    return urls


def down_url(urls, path=r'./temp'):
    if not os.path.isdir(path):
        os.mkdir(path)
    print len(urls)
    if isinstance(urls, list) and urls:
        for url in urls:
            print "%s is downloading..." % url
            if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif') or url.endswith('.jpeg') or url.endswith('.bmp'):
                filename = url.rsplit('/', 1)[1]
                urllib.urlretrieve(url, os.path.join(path, filename))
            else:
                time.sleep(5)
                filename = str(uuid.uuid4()) + ".html"
                html = get_html(url)
                if html:
                    with open(os.path.join(path, filename), 'w') as f:
                        f.writelines(html)
                    f.close()


@app.task
def tarall_task(url, id='1', findpath='/',src=r'./static/', path=r'./temp', tarfilename="test.tar.gz", xpath=[], xlink=[]):
    print url, id, findpath, src, path, tarfilename
    #download....
    if xpath and xlink and (len(xpath) == len(xlink)):
        for i in zip(xpath,xlink):
            down_url(get_url(url, xpath=i[0], xlink=i[1], findpath=findpath), path=path)

    #tar file
    tar_file(src=src, path=path, filename=tarfilename)
    model.update_spider(id)
    return "OK!"


#run celery deamon
#celery -A spider worker -c 10 --loglevel=INFO
#run celery montoir flower http://127.0.0.1:5555
#celery -A spider flower --port=5555

# url='http://m.cnkang.com/'
# xpath = ['a', 'img']
# xlink = ['href', 'src']
#path = './' + ''.join([random.choice(string.letters) for i in range(8)])
# tarall(url, path=path, tarfilename="cnkang-m.tar.gz", xpath=xpath, xlink=xlink)

