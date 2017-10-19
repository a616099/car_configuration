# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time
import sqlalchemy as sa
from scrapy.conf import settings


class Auto163Pipeline(object):
    table = {
            'auto163_config' : 'auxiliary_auto163_v3',
            'auto163Dealer' : 'auxiliary_auto163_dealer',
            }

    def __init__(self):
        self.db = sa.create_engine(settings.get('MYSQLDB'),encoding='utf-8')
        self.conn = self.db.raw_connection()
        self.cursor = self.conn.cursor()
        # self.table = self.table[spider.name]
        self.count = 0

    def insert(self, item):

        sql = 'INSERT IGNORE INTO ' + self.table + '('
        cols = item.fields.keys()
        for col in cols:
            sql += col + ','
        sql = sql[:-1] + ') VALUES('
        for _ in cols:
            sql += '%s,'
        sql = sql[:-1] + ')'
        self.cursor.execute(sql, tuple((item.get(i) for i in cols)))
        
    # 根据spider.name格式化要插入的表名
    def open_spider(self, spider):
        self.table = self.table[spider.name]
        print(time.strftime('%Y-%m-%d %H:%M:%S'))

    def close_spider(self, spider):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

        print(time.strftime('%Y-%m -%d %H:%M:%S'))

    def process_item(self, item, spider):
        self.insert(item)
        self.count += 1
        if self.count == 1000:
            self.conn.commit()
            self.count = 0

