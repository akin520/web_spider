#!\urs\bin\env python
#encoding:utf-8

import web
import datetime
#数据库连接
db = web.database(host='localhost', dbn='mysql', db='test', user='root', pw='')

def get_spiders():
    return db.select('spider', order = 'id DESC')

def new_spider(url, tarfilename,):
    return db.insert('spider',
              url=url,
              tarfilename=tarfilename,
              status=0,
              add_time = datetime.datetime.utcnow())

def update_spider(id):
    db.update('spider',
        where = 'id = $id',
        vars = locals(),
        status=1)