#!\urs\bin\env python
#encoding:utf-8

from celery import Celery
from spider import tarall_task
import random
import string
import web
import model

urls = (
    '/','Index',
    '/new','New',
    '/about','About',
)

web.config.debug = False
web_app = web.application(urls, globals())
# session = web.session.Session(web_app, web.session.DiskStore('sessions'))
render = web.template.render('templates/',cache=False)

app = Celery('tasks', broker='redis://127.0.0.1:6379/0')
app.conf.CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'


def manage_spider_task(url, id='1', findpath='/', src=r'./static/', path='./temp', tarfilename="cnkang-m.tar.gz", xpath=[], xlink=[]):
    result = tarall_task.delay(url, id=id, findpath=findpath, src=src, path=path, tarfilename=tarfilename, xpath=xpath, xlink=xlink)
    return result


class Index:
    def GET(self):
        spiders = model.get_spiders()
        return render.index(spiders)

class New:
    def GET(self):
        return render.new()

    def POST(self):
        i = web.input()
        print i
        url = i.get('url')
        findpath = i.get('findpath')
        path = './' + ''.join([random.choice(string.letters) for jj in range(8)])
        tarfilename = i.get('tarfilename')
        xpath = i.get('xpath').split(',')
        xlink = i.get('xlink').split(',')
        rowid = model.new_spider(url, tarfilename)
        if rowid:
            result = manage_spider_task(url, findpath=findpath, path=path, tarfilename=tarfilename, xpath=xpath, xlink=xlink, id=rowid)
            print "celery add id:",result
            if result:
                raise web.seeother('/')
            else:
                return '''<script>alert('celery add error');history.back();</script>'''
        else:
            return '''<script>alert('db add error');history.back();</script>'''


class About:
    def GET(self):
        return render.about()

if __name__ == '__main__':
    web_app.run()
    # url = 'http://m.cnkang.com/'
    # xpath = ['a', 'img']
    # xlink = ['href', 'src']
    # path= './' +  ''.join([random.choice(string.letters) for i in range(8)])
    # print manage_spider_task(url, path=path, tarfilename="cnkang-m.tar.gz", xpath=xpath, xlink=xlink)
    #
    # url = 'http://www.cnkang.com/'
    # xpath = ['img']
    # xlink = ['src']
    # path = './' + ''.join([random.choice(string.letters) for i in range(8)])
    # print manage_spider_task(url, path=path, tarfilename="cnkang-www.tar.gz", xpath=xpath, xlink=xlink)
