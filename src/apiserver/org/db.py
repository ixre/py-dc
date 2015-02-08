# -*- coding:utf-8 -*-
import MySQLdb
import conf

class newdb(object):
    '''数据操作'''
    def __init__(self,returnDict=False):
        '返回游标为字典的数据访问对象'
        self.conn=MySQLdb.connect(
                                  host=conf.db_host,
                                  user=conf.db_user,
                                  passwd=conf.db_pwd,
                                  db=conf.db_name,
                                  port=conf.db_port,
                                  charset='utf8'
                                  )
        if  returnDict:
            self.cursor=self.conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        else:
            self.cursor=self.conn.cursor()
            
        
    def commit(self):
        self.conn.commit()
    def close(self):
        self.conn.close()
        
    def fetchone(self,sql,args=None):
        self.cursor.execute(sql,args)
        result=self.cursor.fetchone()
        self.cursor.close()
        self.close()
        return result
        
    def fetchall(self,sql,args=None):
        result=None
        self.cursor.execute(sql,args)
        result=self.cursor.fetchall()
        self.cursor.close()
        self.close()
        return result
    
    def query(self,sql,args=None):
        self.cursor.execute(sql,args)
        self.cursor.close()
        _row=self.cursor.rowcount
        self.commit()
        self.cursor.close()
        self.close()
        return _row
       
       
#********* SQLAlchemy *****************#
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class SA:
    'SQLAlchemy'
    engine=create_engine('mysql://%s:%s@%s:%s/%s?charset=utf8'%(
                                conf.db_user,
                                conf.db_pwd,
                                conf.db_host,
                                conf.db_port,
                                conf.db_name
                                  ),echo=True)
    
    Session=sessionmaker(bind=engine)
'''