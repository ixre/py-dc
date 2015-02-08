#-*-encoding:utf-8-*-
import web
import hashlib,base64,re
from db import *
import conf,utility

def encryptPwd(username,userpwd):
    '根据用户密码生成加密字串'
    m=hashlib.md5(u'%s$@OPSoft$%s'%(username,userpwd))
    return m.hexdigest()
    
def saveUStat(id,username,encryptPwd,seconds=3600,path='/'):
    '加密字串，存放的客户端'
    token=base64.encodestring('id=%s;username=%s;ticket=%s'%(
                        id,                          
                        username,
                        encryptPwd)
                               ).replace('m','mb')
    
    web.setcookie('token',token,expires=seconds,path=path)
    
def getUStat():
    '''
    读取COOKIE (utk)并解码(mb->m)
    '''
    token=base64.decodestring(web.cookies(token='').token.replace('mb','m'))
    reg=re.compile('^id=([^;]+);username=([^;]+);ticket=(.+?)$')
    match=reg.search(token)
    if match:
        return match.groups()[0],match.groups()[1],match.groups()[2]
    return None


#+===================== 合作商 ==========================
def getpartnerid(username):
    '获取合作商ID'
    row=newdb().fetchone('SELECT id FROM partners WHERE user=%(user)s',{'user':username})
    return None if row==None else row[0]

def isExistsPartner(username,userpwd):
    '接否存在合作商'
    return newdb().fetchone('SELECT count(0) FROM partners WHERE user=%(u)s and pwd=%(p)s',{'u':username,'p':userpwd})[0]==1

def getpartner(username):
    '获取合作商信息'
    return newdb(True).fetchone('SELECT * FROM partners WHERE user=%(user)s',{'user':username})

def getpartnerbyid(partnerid):
    return newdb(True).fetchone('SELECT * FROM partners WHERE id=%(id)s',{'id':partnerid})

def getsubs(partnerid):
    '获取所有分点'
    return newdb(True).fetchall('SELECT * FROM pt_subs WHERE ptid=%(ptid)s',{'ptid':partnerid})

def getsub(subid):
    '获取分店信息'
    return newdb(True).fetchone('SELECT * FROM pt_subs WHERE id=%(id)s',{'id':subid})

def addsub(partnerid,name,address,phone,idx,state):
    return newdb().query('''INSERT INTO pt_subs
                            (ptid,name,address,phone,
                            idx,state)
                            VALUES
                            (%(ptid)s,
                            %(name)s,
                            %(address)s,
                            %(phone)s,
                            %(idx)s,
                            %(state)s
                            )
                            ''',{'ptid':partnerid,
                                 'name':name,
                                 'address':address,
                                 'phone':phone,
                                 'idx':idx,
                                 'state':state
                                 })==1

def updatesub(id,partnerid,name,address,phone,idx,state):
     return newdb().query('''UPDATE pt_subs
                            SET 
                            name=%(name)s,
                            address=%(address)s,
                            phone=%(phone)s,
                            idx=%(idx)s,
                            state=%(state)s
                            WHERE id=%(id)s AND ptid=%(ptid)s
                            ''',{'id':id,
                                 'ptid':partnerid,
                                 'name':name,
                                 'address':address,
                                 'phone':phone,
                                 'idx':idx,
                                 'state':state
                                 })==1
    
def gethost(partnerid):
    '获取合作商域名'
    host = newdb().fetchone('SELECT host FROM pt_hosts WHERE ptid=%(ptid)s',{'ptid':partnerid})
    if host!=None:
        return host[0]
    else:
        usr=newdb().fetchone('SELECT user FROM partners WHERE id=%(id)s',{'id':partnerid})[0]
        return '%s.%s'%(usr,conf.host)
    
def getpage(partnerid,type):
    '获取页面内容'
    row = newdb().fetchone('SELECT `content` FROM pt_page WHERE `ptid`=%(ptid)s and `type`=%(type)s',
                            {
                             'ptid':partnerid,
                             'type':type
                            })
    
    return '' if row==None else row[0]

                            
def updatepage(partnerid,type,content):
    '更新页面内容'
    data={
          'ptid':partnerid,
          'type':type,
          'content':content,
          'updatetime':utility.timestr()
          }
    
    row=newdb().query('UPDATE pt_page SET `content`=%(content)s,`updatetime`=%(updatetime)s WHERE `ptid`=%(ptid)s AND `type`=%(type)s',data)
    if row==0:
        newdb().query('INSERT INTO pt_page (`ptid`,`type`,`content`,`updatetime`) VALUES(%(ptid)s,%(type)s,%(content)s,%(updatetime)s)',data)



                            
        
    