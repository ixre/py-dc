#-*- encoding:utf-8 -*-
import web,time,random
import org.user
from org.db import *
from org.order import *

class order:
    def POST(self):
        action=web.input().action
        return eval('self.%s()'%(action))
    def GET(self):
        return self.POST()
    
    def createorder(self):
        '''
        创建订单
        @partnerid      商家ID
        @memberid       会员ID
        @cart           购物车信息
        @o_address      配送地址
        @o_phone        联系电话
        @o_sendtime     配送时间
        @o_paymethod    支付方式
        @o_note         备注信息
        '''
        req=web.input()
        o_phone=req.o_phone                 #配送联系电话
        o_address=req.o_address             #配送地址
        c_note=req.o_note                   #配送备注
        c_paymethod=req.o_paymethod         #支付方式, 1:货到付款
        
        c_orderid=None                      #订单号
        c_createtime=time.localtime()       #创建时间
        c_sendtime=req.o_sendtime           #配送时间
        c_memberid=req.memberid             #会员
        c_partnerid=req.partnerid           #合作商
        c_items=req.cart                    #订单商品
        c_itemsinfo=''                      #商品信息
        c_pay=0                             #支付金额
        
        '格式化创建时间'
        c_timestr=time.strftime('%Y-%m-%d %H:%M:%S',c_createtime)
        
        '创建订单号码'
        c_orderid='%s-%d' %(
                         time.strftime('%Y%m%d',c_createtime),
                         random.randint(1000,9999)
                      )
        
        '计算金额'
        c=cart(c_items)
        c_pay=c.mathfee()
        c_itemsinfo=c.buildInfo()
        
        '将信息添加到备注'
        if c_memberid=='':
            c_note=u'配送地址：%s<br />联系电话：%s<br />其他：%s'%(
                        o_address,
                        o_phone,
                        c_note
                     )
        
        newdb().query('''INSERT INTO pt_orders(
                            id,
                            mid,
                            ptid,
                            ptsid,
                            items,
                            itemsinfo,
                            pay,
                            paymethod,
                            note,
                            createtime,
                            sendtime,
                            status,
                            updatetime)
                            VALUES
                            (
                            %(id)s,
                            %(mid)s,
                            %(ptid)s,
                            %(ptsid)s,
                            %(items)s,
                            %(itemsinfo)s,
                            %(pay)s,
                            %(paymethod)s,
                            %(note)s,
                            %(createtime)s,
                            %(sendtime)s,
                            %(status)s,
                            %(updatetime)s
                            )
                            ''',
                            {
                              'id':c_orderid,
                              #'mid':'0' if c_memberid=='' else c_memberid,
                              'mid':c_memberid,
                              'ptid':c_partnerid,
                              'ptsid':0,
                              'items':c_items,
                              'itemsinfo':c_itemsinfo,
                              'pay':c_pay,
                              'paymethod':c_paymethod,
                              'note':c_note,
                              'createtime':c_timestr,
                              'sendtime':c_sendtime,
                              'status':0,
                              'updatetime':c_timestr
                             })
        
        return 'true'
        
        