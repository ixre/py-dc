#-*- encoding:utf-8 -*-
from db import *
import re
import user,member,utility

'订单状态'
order_states=(
              '<span style="color:#d0d0d0">已作废</span>',     #-1
              '未处理',                                        #0
              '<span style="color:#FFCC33">处理中</span>',     #1
              '<span style="color:#FFCC33">配送中</span>',     #2
              '<span style="color:green">已完成</span>'        #3
              )

'订单支付方式(paymethod=[1|2])'
order_paymethods=(
                  '未知',
                  '餐到付款',                                   #1
                  '网银支付'                                    #2
                  )

class cart:
    def __init__(self,data):
        '''init a cart
           data example : 16*1|12*2|80
           (ItemID * ItemNum )| TotalFee 
        '''
        self.data=data
        
    def __getitem__(self,itemid):
        row= newdb(True).fetchone('SELECT name,note,price,percent FROM fd_items WHERE id=%(id)s',
                         {'id':itemid})
        return row
        
    def getprice(self,itemid):
        '获取商品价格'
        row= self.__getitem__(itemid)
        if row==None:return 0
        else:
            return row['price']*row['percent']
        
    def buildInfo(self):
        '生成大纲信息'
        info=''
        reg=re.compile('(\d+)\*([\d\.]+)\*(\d+)\|')
        matchs=reg.findall(self.data)
        
        __item=None
        for m in matchs:
            __item=self.__getitem__(m[0])
            #if __item!=None:
            info+='%s(%s) * %s\r\n'%(__item['name'],__item['note'],m[1])
        return info
        
    def mathfee(self):
        '''
        计算总金额
        '''
        tt_fee=0    
                        
        reg=re.compile('(\d+)\*([\d\.]+)\*(\d+)\|')
        matchs=reg.findall(self.data)
        
        for m in matchs:
            tt_fee+=self.getprice(m[0]) * int(m[2])
        
        return tt_fee
    

        
def getorders(partnerid,status,page,size):
    db=newdb(True)
    
    db.cursor.execute('SELECT count(0) as t FROM pt_orders WHERE ptid=%(ptid)s AND status=%(status)s',
                     {
                      'ptid':partnerid,
                      'status':status
                      })
                      
    count=db.cursor.fetchone()['t']         

    db.cursor.execute('''SELECT id,
                        mid,
                        ptid,
                        ptsid,
                        itemsinfo,
                        pay,
                        paymethod,
                        note,
                        date_format(createtime,%(fmt)s) as createtime,
                        date_format(sendtime,%(fmt)s) as sendtime,
                        status,
                        date_format(updatetime,%(fmt)s) as updatetime
                        FROM pt_orders WHERE ptid=%(ptid)s AND status=%(status)s
                        ORDER BY createtime desc LIMIT %(num)s,%(size)s''',
                     {
                       'fmt':'%Y-%m-%d %T',
                       'ptid':partnerid,
                      'status':status,
                      'num':(page-1)*size,
                      'size':size
                     })
    
    rows=db.cursor.fetchall()

    return count,rows

def getmemberorders(memberid,page,size,where='',orderby='createtime desc'):
    db=newdb(True)
    if where!='':
        where=' AND '+where
    
    db.cursor.execute('SELECT count(0) as t FROM pt_orders o INNER JOIN partners p ON o.ptid=p.id WHERE mid=%(memberid)s'+where,
                     {
                      'memberid':memberid
                      })
                      
    count=db.cursor.fetchone()['t']
    

    db.cursor.execute('''SELECT o.id,
                        p.name,
                        p.tel,
                        p.address,
                        ptid,
                        ptsid,
                        itemsinfo,
                        pay,
                        paymethod,
                        note,
                        date_format(o.createtime,%(fmt)s) as createtime,
                        date_format(o.sendtime,%(fmt)s) as sendtime,
                        o.status,
                        date_format(o.updatetime,%(fmt)s) as updatetime
                        FROM pt_orders o INNER JOIN partners p ON o.ptid=p.id  WHERE mid=%(mid)s '''+where+'''
                        ORDER BY '''+orderby+''' LIMIT %(num)s,%(size)s''',
                     {
                       'fmt':'%Y-%m-%d %T',
                       'mid':memberid,
                      'num':(page-1)*size,
                      'size':size
                     })
    
    rows=db.cursor.fetchall()

    return count,rows

def getorder(id):
    '获取订单'
    return newdb(True).fetchone('''SELECT *,
                                    date_format(createtime,%(fmt)s) as createtime,
                                    date_format(sendtime,%(fmt)s) as sendtime,
                                    date_format(updatetime,%(fmt)s) as updatetime
                                    FROM pt_orders WHERE id=%(id)s''',
                                {
                                 'id':id,
                                 'fmt':'%Y-%m-%d %T'
                                })
    
    
    
def setstatus(partnerid,orderid,status):
    '设置订单状态'
    db=newdb()
    timestr=utility.timestr()
    
    #更新订单状态
    result=db.cursor.execute('UPDATE pt_orders SET status=%(status)s WHERE id=%(id)s AND ptid=%(ptid)s',
                  {
                   'id':orderid,
                   'ptid':partnerid,
                   'status':status
                   })==1
                   
    if result:
        if status==3:
            #将此次消费记入会员账户
            db.cursor.execute('SELECT mid,pay FROM pt_orders WHERE id=%(id)s and mid<>0',{'id':orderid})
            row=db.cursor.fetchone()
            _memberid=None if row==None else row[0]
            
            #会员订餐
            if _memberid!=None:
                _amount=row[1]
                db.cursor.execute('''UPDATE mm_account SET
                    totalpay=totalpay+%(amount)s
                    WHERE memberid=%(memberid)s''',
                    {
                     'memberid':_memberid,
                     'amount':_amount
                    }
                )
                
                
                #万绿园返现
                _pt=user.getpartnerbyid(partnerid)
                
                if _pt['user']=='wly':
                    bytes=(
                           1,           #100%分成
                           0.02,         #上级
                           0.01,         #上上级
                           0.1          #消费者自己
                           )
                    
                    _backfee=row[1]*bytes[0]
                    
                    
                    _mid=_memberid
                    
                    tpl_str=u'来自订单:%s(商家:%s,会员:%s)收入￥%s元.'
                    
                   

                    '给自己返现'
                    
                    if bytes[3]!=0:
                        db.cursor.execute('''INSERT INTO mm_account_incomelog
                                                    (
                                                    memberid,
                                                    type,
                                                    fee,
                                                    log,
                                                    recordtime)
                                                    VALUES
                                                    (
                                                    %(memberid)s,
                                                    %(type)s,
                                                    %(fee)s,
                                                    %(log)s,
                                                    %(recordtime)s
                                                    )''',
                                                    {
                                                     'memberid':_mid,
                                                     'type':'backcash',
                                                     'fee':_backfee*bytes[3],
                                                     'log':u'订单:%s返现￥%s元'%\
                                                            (
                                                               orderid,
                                                               str(_backfee*bytes[3])
                                                            ),
                                                     'recordtime':timestr
                                                    })
                                
                        db.cursor.execute('UPDATE mm_account SET totalfee=totalfee+%(amount)s,balance=balance+%(amount)s,updatetime=%(uptime)s WHERE memberid=%(memberid)s',
                                          {
                                            'amount':_backfee*bytes[3],
                                            'memberid':_mid,
                                            'uptime':timestr
                                           }
                                          )
                    
                    
                       
                    '给上线返现'
                    i=0;
                    
                    while _mid!=0 and i<2:
                        db.cursor.execute('SELECT tgid FROM mm_relations WHERE memberid=%(memberid)s',{'memberid':_mid})
                        _mid2=db.cursor.fetchone()[0]
                        
                        if _mid2!=0:
                            '获取产生的用户'
                            db.cursor.execute('SELECT username,realname FROM members WHERE id=%(memberid)s',{'memberid':_mid})
                            _username=db.cursor.fetchone()[0]
                            _fee=_backfee*bytes[i+1]            #返现金额
                            _log=tpl_str%\
                                    (
                                      orderid,
                                      _pt['name'],
                                      _username,
                                      str(_fee)
                                     )
                            
                            db.cursor.execute('''INSERT INTO mm_account_incomelog
                                                (
                                                memberid,
                                                type,
                                                fee,
                                                log,
                                                recordtime)
                                                VALUES
                                                (
                                                %(memberid)s,
                                                %(type)s,
                                                %(fee)s,
                                                %(log)s,
                                                %(recordtime)s
                                                )''',
                                                {
                                                 'memberid':_mid2,
                                                 'type':'backcash',
                                                 'fee':_fee,
                                                 'log':_log,
                                                 'recordtime':timestr
                                                })
                            
                            db.cursor.execute('UPDATE mm_account SET totalfee=totalfee+%(amount)s,balance=balance+%(amount)s,updatetime=%(uptime)s WHERE memberid=%(memberid)s',
                                      {
                                        'amount':_fee,
                                        'memberid':_mid2,
                                        'uptime':timestr
                                       }
                                      )
                    
                                    
                        _mid=_mid2
                        i+=1
        
        #会员订餐处理结束
        
                
        #提交更改到数据库
        db.commit()
        db.conn.close()
               
    return result

                   
def delorder(partnerid,orderid):
    '作废订单'
    return setstatus(partnerid,orderid,-1)

def setsub(partnerid,orderid,subid):
    '设置订单配送分店'
    row=newdb().fetchone('SELECT count(0) FROM pt_subs WHERE id=%(id)s AND ptid=%(ptid)s',
                      {
                       'id':subid,
                       'ptid':partnerid
                      })[0]
                                    
    if row!=1:return False              #如果分店不存在，则返回False
    return  newdb().query('UPDATE pt_orders SET ptsid=%(ptsid)s WHERE id=%(id)s AND ptid=%(ptid)s',
                  {
                   'id':orderid,
                   'ptid':partnerid,
                   'ptsid':subid
                   })==1
                   
    