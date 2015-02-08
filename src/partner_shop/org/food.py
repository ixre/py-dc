#-*-encoding:utf-8-*-
from db import *
import utility
import urllib,urllib2
import conf

host=conf.host

def addcate(partnerid,parentid,name):
    '添加菜谱分类'
    db=newdb()
    db.cursor.execute('SELECT MAX(idx) from fd_categories where ptid=%(ptid)s',{'ptid':partnerid})
    idx=db.cursor.fetchone()[0]+1
    db.cursor.execute('''
                INSERT INTO fd_categories
                    (
                    cpid,
                    ptid,
                    name,
                    idx,
                    createtime)
                    VALUES
                    (
                     %(cpid)s,
                     %(ptid)s,
                     %(name)s,
                     %(idx)s,
                     %(createtime)s
                    )
                ''',{
                     'cpid':parentid,
                     'ptid':partnerid,
                     'name':name,
                     'idx':idx,
                     'createtime':utility.timestr()
                     })
    print utility.timestr()
    db.conn.commit()
    db.cursor.close()
    db.conn.close()

def updatecate(partnerid,id,cpid,name,idx):  
    if name!='':
        return newdb().query('''
                UPDATE fd_categories
                SET
                `cpid` = %(cpid)s,
                `name` = %(name)s,
                `idx` = %(idx)s
                WHERE id=%(id)s AND ptid=%(ptid)s
                ''',{
                     'id':id,
                     'ptid':partnerid,
                     'cpid':cpid,
                     'name':name,
                     'idx':idx
                     } ) == 1
    return False
    
def getcates(partnerID):
    '获取父分类'
    return newdb(True).fetchall('''SELECT id,cpid,'''+
                            #(SELECT name FROM fd_categories f WHERE f.id=c.cpid) as cpname,
                           '''name,idx FROM fd_categories c WHERE ptid=%(ptid)s ORDER BY id''',{'ptid':partnerID})

def delcate(id,partnerID):
    '删除分类'
    return newdb().query('DELETE FROM fd_categories WHERE id=%(id)s AND ptid=%(ptid)s',
                           {
                            'id':id,
                            'ptid':partnerID
                            })==1

'======= FOODS ========='
class food:
    def __init__(self,id):
        self.id=id
        
def addfooditem(name,cid,pic,applySubm,note,desc,price=0,percent=1):
    '''
    新增食物
    '''
    _tstr=utility.timestr()
    _id=None
    
    db=newdb()
    db.cursor.execute('''INSERT INTO fd_items
                        (
                        cid,
                        name,
                        img,
                        price,
                        percent,
                        applysubs,
                        note,
                        state,
                        updatetime)
                        VALUES
                        (
                        %(cid)s,
                        %(name)s,
                        %(img)s,
                        %(price)s,
                        %(percent)s,
                        %(applysubs)s,
                        %(note)s,
                        %(state)s,
                        %(updatetime)s
                        )''',
                        {
                            'cid':cid,
                            'name':name,
                            'img':pic,
                            'price':price,
                            'percent':percent,
                            'applysubs':applySubm,
                            'note':note,
                            'state':1,
                            'updatetime':_tstr
                            
                        })
    
    '获取插入的索引'
    db.cursor.execute('SELECT id FROM fd_items WHERE cid=%(cid)s AND updatetime=%(uptime)s',
                      {
                       'cid':cid,
                       'uptime':_tstr
                       }
                      )
    
    _id=db.cursor.fetchone()[0]
    
    '插入描述'
    db.cursor.execute('''INSERT INTO fd_itemprop
                        (id,description)VALUES
                        (%(id)s,%(description)s)''',
                          {
                         'id':_id,
                         'description':desc
                         })
    
    '提交到数据库'
    db.conn.commit()
    db.cursor.close()
    db.conn.close()

def updatefooditem(id,name,cid,pic,applySubm,note,desc,price=0,percent=1):
    '''
    更新食物
    '''
    _tstr=utility.timestr()
    
    db=newdb()
    db.cursor.execute('''UPDATE fd_items
                        SET cid=%(cid)s,
                        name=%(name)s,
                        img=%(img)s,
                        price=%(price)s,
                        percent=%(percent)s,
                        applysubs=%(applysubs)s,
                        note=%(note)s,
                        updatetime=%(updatetime)s
                        WHERE id=%(id)s''',
                        {
                            'id':id,
                            'cid':cid,
                            'name':name,
                            'img':pic,
                            'price':price,
                            'percent':percent,
                            'applysubs':applySubm,
                            'note':note,
                            'updatetime':_tstr
                            
                        })
    
    '更新描述'
    db.cursor.execute('''UPDATE fd_itemprop
                        SET description=%(description)s
                        WHERE id=%(id)s''',
                          {
                         'id':id,
                         'description':desc
                         })
    
    '提交到数据库'
    db.conn.commit()
    db.cursor.close()
    db.conn.close()

def saveitempic(partnerid,filename,data):
    '向接口提交图片'
    data={
          'key':'xxxxx',
          'action':'saveitempic',
          'partnerid':partnerid,
          'filename':filename,
          'data':data
          }
    request=urllib2.Request('http://api.%s/food'%(host),data=urllib.urlencode(data))
    response=urllib2.urlopen(request)
    if response.code==200:
        return True
    
    return False
     

def getfooditems(partnerid,page,size,cid=-1):
   '''获取食物'''
   return newdb(True).fetchall('''SELECT f.*,c.name as cname FROM fd_items f
    INNER JOIN fd_categories c ON f.cid=c.id where c.ptid=%(ptid)s'''
    +(' AND cid=%(cid)s' if cid!=-1 else '')+
    ''' ORDER BY updatetime desc limit %(s)s,%(e)s''',
                         {
                          'ptid':partnerid,
                          's':(page-1)*size,
                          'e':size,
                          'cid':cid
                          }
                         )

def getfoods(partnerid,cid):
    return newdb(True).fetchall('''SELECT f.*,c.name as cname FROM fd_items f
    INNER JOIN fd_categories c ON f.cid=c.id where c.ptid=%(ptid)s
      AND cid=%(cid)s ORDER BY id''',
                         {
                          'ptid':partnerid,
                          'cid':cid
                          }
                                )

def getcupornfoods(partnerid):
    return newdb(True).fetchall('''SELECT f.*,c.name as cname FROM fd_items f
    INNER JOIN fd_categories c ON f.cid=c.id where c.ptid=%(ptid)s
       AND `percent`<1 ORDER BY id''',
                         {
                          'ptid':partnerid
                          }
                                )
    
def fooditemsCount(partnerid,cid=-1):
    '''
    获取食物数量
    '''
    return newdb().fetchone('''SELECT count(0) FROM fd_items f
    INNER JOIN fd_categories c ON f.cid=c.id where c.ptid=%(ptid)s'''
    +(' AND cid=%(cid)s' if cid!=-1 else ''),
        {
            'ptid':partnerid,
            'cid':cid
         })[0]
         
def delete(partnerid,id):
    rows=newdb().query('''DELETE f,f2 FROM fd_items AS f 
                        INNER JOIN fd_categories AS c ON f.cid=c.id
                        INNER JOIN fd_itemprop as f2 ON f2.id=f.id
                         WHERE f.id=%(id)s AND c.ptid=%(ptid)s''',
                {
                  'ptid':partnerid,
                  'id':id
                 })
    print rows
    return rows==2

def get(partnerid,id):
    '获取食物信息'
    return newdb(True).fetchone('''SELECT * FROM fd_items f
     INNER JOIN fd_categories  c ON f.cid=c.id
     INNER JOIN fd_itemprop f2 ON f2.id=f.id
     WHERE f.id=%(id)s AND c.ptid=%(ptid)s
     ''',{
          'ptid':partnerid,
          'id':id
          })
    
       