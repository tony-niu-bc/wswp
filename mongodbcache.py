#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bson.binary import Binary
from pymongo  import MongoClient
from datetime import datetime, timedelta
import pickle
import zlib

# 添加 mongo 安装目录中的 bin 目录到环境变量
# export PATH=/home/tools/mongodb/bin:$PATH
# 执行 mongod 命令来启动 mongdb 服务
# ./mongod --dbpath <数据库所在路径>
# 如果想进入 MongoDB 后台管理
# ./mongo
# 使用用户 admin 使用密码 123456 连接到本地的 MongoDB 服务上
# mongodb://admin:123456@localhost/
# 创建数据库（如果数据库不存在，则创建数据库，否则切换到指定数据库）
# use <数据库名>
# 查看所有数据库
# show dbs
# insert 插入一个列表多条数据不用遍历，效率高
# my_col.insert({'name': 'wzh', 'age': 18})
# save 需要遍历列表，一个个插入
# my_col.save({'name': 'nsc', 'age': 21})
# 添加多条数据到集合中
# users=[{'name': 'wzh', 'age': 18},{'name': 'nsc', 'age': 21}]
# my_col.insert(users)
# my_col.save(users)
#
# 删除数据
# remove(
#    <query>,                   #（可选）删除的文档的条件
#    {
#      justOne: <boolean>,      #（可选）如果设为 true 或 1，则只删除一个文档
#      writeConcern: <document> #（可选）抛出异常的级别
#    }
# )
# my_col.remove({'name': 'wuciren'})
#
# id = my_set.find_one({'name': 'wuciren'})['_id']
# my_set.remove(id)
#
# 删除集合里的所有记录
# db.users.remove()
#
# mongodb 的条件操作符
# $gt   - 大于(>)
# $lt   - 小于(<)
# $gte  - 大于等于(>=)
# $lte  - 小于等于(<= )
# $or   - 或
# $in   - 在指定集合之中
# $all  - 包含全部
#
# mongodb 的更新操作符
# $push    - 文档中的指定列表追加一值
# $pushAll - 文档中的指定列表追加多值
# $pop     - 文档中的指定列表移除指定位置的值（1为最后一个，-1为移除第一个）
# $pull    - 文档中的指定列表移除指定值
# $pullAll - 文档中的指定列表移除多个指定值
#
# 文档中的指定列表追加一值
# my_col.update({'name': 'wzhnsc'}, {'$push': {'flag': 6}})
# 文档中的指定列表追加多值
# my_col.update({'name': "wzhnsc"}, {'$pushAll': {'flag': [6, 9]}})
# 文档中的指定列表移除最后一个元素(-1为移除第一个)
# my_col.update({'name': "wzhnsc"}, {'$pop': {'flag': 1}})
# 按值移除单个
# my_col.update({'name': 'wzhnsc'}, {'$pull': {'flag': 3}})
# 按值移除多个
# my_col.update({'name': 'wzhnsc'}, {'$pullAll': {'flag': [3, 6, 9]}})
#
# 查询集合中 age 大于 25 的所有记录
# for i in my_set.find({"age":{"$gt":25}}):
#
# 找出 age 是 20 或 35 的记录
# for i in my_col.find({'$or': [{'age': 20}, {'age': 35}]}):
#
# 找出 age 是 20、30、35 的记录
# for record in my_col.find({'age': {'$in': (20, 30, 35)}}):
#
# 查看是否包含全部条件
# 1 - 条件1, 2 - 条件2, ..., 9 - 条件9
# for i in my_set.find({'flag': {'$all': [3, 5, 6, 8, 9]}}):
#
# Double                  1
# String                  2
# Object                  3
# Array                   4
# Binary data             5
# Undefined               6    已废弃
# Object id               7
# Boolean                 8
# Date                    9
# Null                    10
# Regular Expression      11
#
# JavaScript              13
# Symbol                  14
# JavaScript (with scope) 15
# 32-bit integer          16
# Timestamp               17
# 64-bit integer          18
# Min key    255    Query with -1.
# Max key    127
# 找出name的类型是String的
# for i in my_set.find({'name': {'$type': 2}}):
#
# 在 MongoDB 中使用 sort() 方法对数据进行排序，
# sort() 方法可以通过参数指定排序的字段，
# 并使用 1 和 -1 来指定排序的方式，其中 1 为升序，-1为降序。
# for i in my_col.find().sort([('age', 1)]):
#
# limit()方法用来读取指定数量的数据
#
# skip()方法用来跳过指定数量的数据
#
# 下面表示跳过 2 条数据后读取 6 条
# for record in my_col.find().skip(2).limit(6):
#
# 访问/更新文档中指定字典key-value对
# for record in my_col.find({'contact.iphone': '12345678901'}):
# 访问/更新文档中指定字典数组下标(基于零)的key-value对
# result1 = my_set.find_one({"contact.1.iphone":"12345678901"})
#
class MongodbCache:

    def __init__(self, client=None, expires=timedelta(days=30)):
        # 如果没有传入一个 Mongo 数据库客户端的话，则连接本机默认端口 Mongo 数据库
        if client is None:
            client = MongoClient('localhost', 27017)

        self.client  = client
        self.expires = expires

        # db（数据库）和 collection（表）都是延时创建的，在添加 Document（记录）时才真正创建
        # 连接 db_cache_webpage 数据库，没有则自动创建
        self.db  = client.db_cache_webpage

        # 为过期缓存网页创建索引
        # MongoDB 运行一个后台任务，每分钟检查一次过期记录
        self.db.col_bulk_egg.create_index('timestamp', expireAfterSeconds=expires.total_seconds())

    # 根据 URL 从数据库表中加载数据
    def __getitem__(self, url):
        # for record in my_col.find({"name":"wzhnsc"}):
        record = self.db.col_bulk_egg.find_one({'_id': url})
        if record:
            return pickle.loads(zlib.decompress(record['result']))
        else:
            raise KeyError(url + ' does not exist')

    # 根据 URL 保存数据到数据库表上
    def __setitem__(self, url, result):
        # BSON 是由 10gen 开发的一个数据格式，目前主要用于 MongoDB 中，是 MongoDB 的数据存储格式。
        record = {'result': Binary(zlib.compress(pickle.dumps(result))),
                  'timestamp': datetime.utcnow()}
        # update(
        #    <query>,                   # 查询条件
        #    <update>,                  # update 的对象和一些更新的操作符
        #    {
        #      upsert: <boolean>,       # 如果不存在update的记录，是否插入
        #      multi: <boolean>,        # 可选，mongodb 默认是 false, 只更新找到的第一条记录
        #      writeConcern: <document> # 可选，抛出异常的级别。
        #    }
        # )
        self.db.col_bulk_egg.update({'_id': url},
                                    {'$set': record},
                                    upsert=True) # 如果不存在 update 的记录，是否插入
