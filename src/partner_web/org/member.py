#-*- coding:utf-8 -*-
from db import newdb
import hashlib
import utility
from user import encryptPwd,saveUStat,getUStat

def chkreg(username):
    '检查用户名是否可以注册'
    return newdb().query('SELECT id FROM members WHERE username=%(user)s',{'user':username})!=1

def getid(username):
    '根据用户名获取ID'
    row= newdb().fetchone('SELECT id FROM members WHERE username=%(user)s',{'user':username})
    return None if row==None else row[0]


def chktg(username):
    '根据用户名获取ID'
    row= newdb().fetchone('SELECT id FROM members WHERE username=%(user)s',{'user':username})
    return row!=None


def create_member(member,partnerid,tgid=0):
    db=newdb()
    timestr=utility.timestr()
    try:
        db.cursor.execute('''INSERT INTO members
                            (
                             username,
                             password,
                             sex,
                             realname,
                             avatar,
                             phone,
                             address,
                             qq,
                             email,
                             birthday,
                             regtime,
                             regip,
                             lastlogintime,
                             state)
                            VALUES
                            (
                            %(username)s,
                            %(password)s,
                            %(sex)s,
                            %(realname)s,
                            %(avatar)s,
                            %(phone)s,
                            %(address)s,
                            %(qq)s,
                            %(email)s,
                            %(birthday)s,
                            %(regtime)s,
                            %(regip)s,
                            %(lastlogintime)s,
                            1)
                            ''',
                            {
                             'username':member.username,
                             'password':encryptPwd(member.username,member.password), #hashlib.md5(member.password).hexdigest(),
                             'sex':member.sex,
                             'realname':member.realname,
                             'avatar':member.avatar,
                             'phone':member.phone,
                             'address':member.address,
                             'qq':member.qq,
                             'email':member.email,
                             'birthday':member.birthday,
                             'regtime':timestr,
                             'regip':member.regip,
                             'lastlogintime':''
                             })
        
        db.cursor.execute('select id from members where username=%(user)s',{'user':member.username})
        memberID=db.cursor.fetchone()[0]
        
        #关系表
        db.cursor.execute('''INSERT INTO mm_relations
                            (memberid,
                             cardid,
                             tgid,
                            regmid)
                            VALUES
                            (
                            %(memberid)s,
                            %(cardid)s,
                            %(tgid)s,
                            %(regmid)s
                            )''',
                            {
                             'memberid':memberID,
                             'cardid':'',
                             'tgid':tgid,
                             'regmid':partnerid
                            }
                          )
            
        #帐户表
        db.cursor.execute('''INSERT INTO mm_account
                            (memberid,
                             balance,
                             totalfee,
                             totalcharge,
                             totalpay,
                             updatetime
                            )
                            VALUES
                            (%(memberid)s,
                             %(balance)s,
                             %(totalfee)s,
                             %(totalcharge)s,
                             %(totalpay)s,
                             %(updatetime)s)
                            ''',
                            {
                             'memberid':memberID,
                             'balance':0,
                             'totalfee':0,
                             'totalcharge':0,
                             'totalpay':0,
                             'updatetime':timestr
                             })
        db.conn.commit()
        
    except:
        db.conn.rollback()
        
    db.conn.close()

def login(username,password):
    '登录,如何成功则保存'
    encPwd=encryptPwd(username,password)
    member=newdb().fetchone('SELECT ID FROM members WHERE username=%(user)s AND password=%(pwd)s',
                            {'user':username,'pwd':encPwd})
    if member==None:
        return False
    else:
        id=member[0]
        saveUStat(id,username,encPwd)
        return True
    
def getMember(username):
    '获取用户及关系'
    member=newdb(True).fetchone('SELECT * FROM members WHERE username=%(user)s',{'user':username})
    if member==None:
        return None
    else:
        relations=newdb(True).fetchone('SELECT * FROM mm_relations WHERE memberid=%(id)s',{'id':member['id']})
        return member,relations
    
def getMemberById(id):
    '获取会员'
    return newdb(True).fetchone('SELECT * FROM members WHERE id=%(id)s',{'id':id})

    
def getaccount(memberid):
    '获取账户'
    return newdb(True).fetchone('SELECT *,date_format(updatetime,%(fmt)s) as updatetime FROM mm_account WHERE memberid=%(memberid)s',{'memberid':memberid,'fmt':'%Y-%m-%d %T'})
    
def uppro(memberid,realname,sex,phone,address,birthday,qq,email,password=None,avatar=None):
    '''
    更新会员信息
    '''
    sql='UPDATE members SET '
    data={
          'sex':sex,
          'mid':memberid,
          'realname':realname,
          'phone':phone,
          'address':address,
          'birthday':birthday,
          'email':email,
          'qq':qq
          }
    
    if password!=None and password!='':
        data['password']=password
        sql+=' password=%(password)s,'
        
    if avatar!=None and avatar!='':
        data['avatar']=avatar
        sql+=' avatar=%(avatar)s,'
    
    sql+='''
            sex = %(sex)s,
            realname =%(realname)s,
            phone = %(phone)s,
            address =%(address)s,
            birthday =%(birthday)s,
            qq =%(qq)s,
            email =%(email)s
            WHERE id=%(mid)s
        '''
    return newdb().query(sql,data)==1

def getbank(memberid):
    return newdb(True).fetchone('SELECT * FROM mm_bank WHERE memberid=%(memberid)s',{'memberid':memberid})

def upbank(memberid,bankname,bankaccount,status=1):
    '更新银行帐号信息'
    data={
            'memberid':memberid,
            'bankname':bankname,
            'bankaccount':bankaccount,
            'status':status,
            'updatetime':utility.timestr()
          };
          
    row=newdb().query('UPDATE mm_bank SET bankname=%(bankname)s,bankaccount=%(bankaccount)s,status=%(status)s,updatetime=%(updatetime)s where memberid=%(memberid)s',data)
    
    if row== 0:
        row=newdb().query('INSERT INTO mm_bank (memberid,bankname,bankaccount,status,updatetime) VALUES (%(memberid)s,%(bankname)s,%(bankaccount)s,%(status)s,%(updatetime)s)',data)
    
    return row!=0  

def getincomelog(memberid,page,size,where='',orderby='recordtime desc'):
    db=newdb(True)
    if where!='':
        where=' AND '+where
    
    db.cursor.execute('SELECT count(0) as t FROM mm_account_incomelog l INNER JOIN members m ON m.id=l.memberid WHERE memberid=%(memberid)s'+where,
                     {
                      'memberid':memberid
                      })
                      
    count=db.cursor.fetchone()['t']
    

    db.cursor.execute('''SELECT l.*,
                        date_format(l.recordtime,%(fmt)s) as recordtime
                        FROM mm_account_incomelog l INNER JOIN members m ON m.id=l.memberid
                         WHERE memberid=%(mid)s '''+where+'''
                        ORDER BY '''+orderby+''' LIMIT %(num)s,%(size)s''',
                     {
                       'fmt':'%Y-%m-%d %T',
                       'mid':memberid,
                      'num':(page-1)*size,
                      'size':size
                     })
    
    rows=db.cursor.fetchall()

    return count,rows

    
