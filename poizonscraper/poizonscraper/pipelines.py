# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class PoizonscraperPipeline:
    def process_item(self, item, spider):
        return item

import mysql.connector

class MySQLPipeline:
    def __init__(self, mysql_host, mysql_db, mysql_user, mysql_password, mysql_port):
        self.mysql_host = mysql_host
        self.mysql_db = mysql_db
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_port = mysql_port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_db=crawler.settings.get('MYSQL_DATABASE'),
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_password=crawler.settings.get('MYSQL_PASSWORD'),
            mysql_port=crawler.settings.get('MYSQL_PORT')
        )

    def open_spider(self, spider):
        self.conn = mysql.connector.connect(
            host=self.mysql_host,
            user=self.mysql_user,
            password=self.mysql_password,
            port=self.mysql_port
        )
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255),
                Categories VARCHAR(255),
                Color VARCHAR(255),
                Images TEXT,
                Link VARCHAR(255),
                SpuId VARCHAR(255),
                CategoryId VARCHAR(255),
                Brand VARCHAR(255),
                Vendor VARCHAR(255)
            )
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def process_item(self, item, spider):
        sql = """
            INSERT INTO products (Name, Categories, Color, Images, Link, SpuId, CategoryId, Brand, Vendor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            item['Name'],
            item['Categories'],
            item['Color'],
            ','.join(item['Images']),
            item['Link'],
            item['SpuId'],
            item['CategoryId'],
            item['Brand'],
            item['Vendor']
        )
        self.cursor.execute(sql, values)
        self.conn.commit()
        return item
    
    def close_spider(self, spider):
        self.conn.close()