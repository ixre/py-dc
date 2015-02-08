import MySQLdb
# -*-encoding:utf-8-*-
class newdb(object):
    '''数据操作'''
    def __init__(self):
        self.conn=MySQLdb.connect(
                                  host='localhost',
                                  user='root',
                                  passwd='',
                                  db='foodording',
                                  port=3306,
                                  charset='utf8'
                                  )
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
        self.commit()
        self.cursor.close()
        self.close()
        
class apibase(object):
    '''
    接口基类,用于判断是否有权限使用接口
    '''
    def __init__(self):
        pass
'''   
db=newdb()  
print db.fetchone('SELECT count(*) FROM patterns')[0]
print newdb().fetchall('SELECT * FROM pt_submerchants')   
'''