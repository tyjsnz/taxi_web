# -*- encoding: utf-8 -*-
#
# Copyright (c) 2025 snz (274043505@qq.com)
#
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: 
# - 

import pymysql
from dbutils.pooled_db import PooledDB
from settings import DatabaseConfig as Config
from datetime import datetime, timedelta
import redis
import hashlib
from src.helper.helper import *
from contextlib import contextmanager
import threading
import pickle
    
'''
数据业务逻辑处理，Redis缓存，数据库连接池
'''
class PublicDbConnectionWithRedis(object):
    __pool = None
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self, _db=None):
        if not hasattr(self, '_initialized'):
            # 初始化 Redis 客户端
            #self._redis = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)
            try:
                self._redis = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=False)
                self._redis.ping()
            except redis.ConnectionError as e:
                print(f"Redis connection error: {e}")
                self._redis = None
            except redis.AuthenticationError as e:
                print(f"Redis authentication error: {e}")
                self._redis = None
            except Exception as e:
                print(f"Unexpected error: {e}")
                self._redis = None
            self.Cache_Expired_Time = 60
            self.port = Config.PORT
            self.charset = Config.CHARSET
            self.user = Config.USER
            self.passwd = Config.PASSWORD
            if _db is None:
                self.db = Config.DB
            else:
                self.db = _db
            self.host = Config.HOST
            self.pool = self.__get_conn_pool()
            self._initialized = True  # 确保 __init__ 只执行一次

    def set_cached_data(self, cache_key, data):
        """设置缓存数据"""
        if self._redis:
            try:
                # 直接使用默认的 JSON 编码
                self._redis.set(cache_key, pickle.dumps(data), ex=self.Cache_Expired_Time)
            except Exception as e:
                print('set Redis connection error:', e)

    def get_cached_data(self, key):
        """获取缓存数据"""
        if not self._redis:
            return None
            
        try:
            cached_data = self._redis.get(key)
            
            return pickle.loads(cached_data) if cached_data else None
        except Exception as e:
            print('get Redis error:', e)
            return None
    
    def __get_conn_pool(self):
        if self.__pool is None:
            try:
                self.__pool = PooledDB(
                    creator=pymysql,
                    host=self.host, 
                    port=self.port, 
                    user=self.user, 
                    passwd=self.passwd, 
                    db=self.db, 
                    charset=self.charset,
                    mincached=5,  # 初始化时创建的连接数
                    maxcached=20,  # 连接池中允许的最大空闲连接数
                    maxconnections=30,  # 允许的最大连接数
                    blocking=True,  # 连接池中如果没有可用连接后是否阻塞等待
                    maxusage=None,  # 单个连接的最大复用次数
                    setsession=['SET AUTOCOMMIT = 1'],  # 设置会话参数
                    ping=1  # 检查连接是否可用
                )
            except Exception as e:
                print('数据库连接池创建失败')
                print(e)

        return self.__pool

    def _get_connection(self):
        conn = self.pool.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        return conn, cursor

    def _close_connection(self, conn, cursor):
        # 只关闭curosr游标，conn让连接池管理
        if cursor:
            cursor.close()
            
        # 不要手动关闭连接，让连接池管理连接的生命周期
        #if conn:
        #    conn.close()

    def __get_cache_key(self, sql, params=None):
        """生成查询语句的 MD5 哈希值作为缓存键"""
        if params:
            query = sql + str(params)
        else:
            query = sql
        return f"db_cache:{hashlib.md5(query.encode()).hexdigest()}"

    def __is_cache_expired(self, cache_data):
        """检查缓存是否过期"""
        if not cache_data:
            return True
        data, expiration_time = cache_data
        return datetime.now() > datetime.now().fromtimestamp(float(expiration_time))

    @contextmanager
    def get_db_connection(self):
        """上下文管理器"""
        conn, cursor = self._get_connection()
        try:
            yield conn, cursor
        finally:
            self._close_connection(conn, cursor)
            
    def _query_sql(self, sql, params=None,use_cache=False):
        cache_key = self.__get_cache_key(sql, params)
        if use_cache == True:
            # 从 Redis 中获取缓存数据
            cached_data = self.get_cached_data(cache_key)
            
            if cached_data:
                return cached_data

        with self.get_db_connection() as (conn, cursor):
            try:
                cursor.execute(sql, params)
                result = cursor.fetchall()
            except Exception as e:
                self.__write_exception(e,sql)
                return None
        
        if result:
            # 将查询结果和过期时间存入 Redis
            self.set_cached_data(cache_key, result)

        return result


    def _query_sql_one(self, sql, params=None,use_cache=True):
        cache_key = self.__get_cache_key(sql + "_one", params)
        if use_cache: 
            # 从 Redis 中获取缓存数据
            cached_data = self.get_cached_data(cache_key)

            if cached_data:
                return cached_data

        with self.get_db_connection() as (conn, cursor):
            try:
                cursor.execute(sql, params)
                result = cursor.fetchone()
            except Exception as e:
                self.__write_exception(e,sql)
                return None
                
        if result:
            # 将查询结果和过期时间存入 Redis
            self.set_cached_data(cache_key, result)

        return result

    def _execute_sql(self, sql, params=None):
        with self.get_db_connection() as (conn, cursor):
            try:
                cursor.execute(sql, params)
                if sql.upper().find("INSERT") != -1:
                    result = cursor.lastrowid
                else:
                    # 删除语句时候返回影响行数            
                    result = cursor.rowcount
                conn.commit()
            except Exception as e:
                print(e)
                conn.rollback()
                self.__write_exception(e,sql)
                return None
    
        return result

    def __write_exception(self, _exception,sql=None):
        msg = f"sql: {sql}，:{str(_exception)}"
        write_logger(msg)
    def get_pool_status(self):
        # 监控连接池状态：
        return {
            'mincached': self.pool.mincached,
            'maxcached': self.pool.maxcached,
            'maxconnections': self.pool.maxconnections,
            'currentconnections': self.pool._connections,
            'cached': self.pool._cached
        }
