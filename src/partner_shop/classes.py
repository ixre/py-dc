#-*- coding:utf-8 -*-
import web,time
from lib.partner import *
import org.user,org.food
from org.order import *
from org.member import login as member_login,getMember
import tpl
import org.utility
import urllib

render=web.template.render('templates/')        #默认模板

#模板
tpls={
      'wly':web.template.render('groups/wly/')
      }

class base:
    def __init__(self):
        '获取合作商ID'
        ptid=getid(web.ctx['host'])
        self.partnerid=ptid
        
        usr=org.user.getUStat()
        if usr!=None:
            self.memberuser=usr[1]
        else:
            self.memberuser=None
        
    def getpartner(self):
        '获取合作商信息'
        return org.user.getpartnerbyid(self.partnerid)
    
    def getmember(self):
        '获取会员信息'
        if self.memberuser!=None:
            return getMember(self.memberuser)
        else:
            return None
        
class index(base):
    '''
    首页
    '''
    def GET(self,act):
        #return org.user.encryptPwd('tguser1','123000')
        
        '''
         万绿员加首页
        '''
        '''
        import lib.wly
        
        if str(self.partnerid)=='666888':
            if act==None:
                return web.SeeOther('/main')
            elif act=='main':
                lib.wly.recordIP(self.memberuser)
                arr=lib.wly.getCountInfo()
                return wlytpl.super_index(tpl=tpl,count=arr)
        '''    
        ''' 结束 '''
            
        if self.partnerid==None:
            web.header('Status','404 Not Found')
            return web.SeeOther('/error')
        else:
            '显示合作商首页'
            partner=self.getpartner()
            
            subs=org.user.getsubs(self.partnerid)       #获取分店
            cates=org.food.getcates(self.partnerid)     #分类
            
            ele_cate=''                                 #分类HTML
            ele_food=''                                 #食物HTML
            
            if len(cates)!=0:
                '分类'
                for i in cates:
                    ele_cate+='<li><a href="#c%d" title="%s">%s</a></li>'%(
                                                                           i['id'],
                                                                           i['name'],
                                                                           i['name']
                                                                           )
                
                '默认菜单'
                ele_food=self.menulist(cates[0])
            
            __tpl=tpls['wly'] if partner['user'] == 'wly' else render
            return __tpl.index(tpl=tpl,
                                partner=partner,
                                subs=subs,
                                ele_cate=ele_cate,
                                ele_food=ele_food,
                                cuporn_foods=self.cupornlist()
                                )
            
    
    def POST(self,act):
        web.header("Content-Type","text/plain")
        action=web.input().action
        if action=='getitems':
            html=''
            cates=org.food.getcates(self.partnerid)     #分类
            for i in xrange(1,len(cates)):
                html+=self.menulist(cates[i])
            return html
        
        return None
    
    def menulist(self,category):
        '获取菜单'
        if category==None:return ''
        
        html=u'''<div class="clearfix"></div>
                 <div class="fl">
                    <h2 id="c%d">%s</h2>
                    <a href="javascript:totop()">返回顶部</a>
                 </div>'''%(
                           category['id'],
                           category['name']
                         )
                
        foods=org.food.getfoods(self.partnerid,category['id'])
        for i in foods:
            html+=u'''<div class="fd_items">
                        <img src="http://img.%s/m/%s/%s" alt="%s"/>
                        <h3 class="name">%s%s</h3>
                        <span class="price">￥%s</span>
                        <a href="javascript:cart.add({'id':'%s','name':'%s','price':%s});" class="add">&nbsp;</a>
                    </div>'''%(
                              tpl.host,
                              'common' if i['img']=='' else self.partnerid,
                              'food_nopic.gif' if i['img']=='' else i['img'],
                              i['name'],
                              i['name'],
                              '<br /><em>('+i['note']+')</em>' if i['note']!='' else '',
                             #self.partnerid,
                              '%.2f'%(i['price']*i['percent']),
                              i['id'],
                              i['name'],
                              '%.2f'%(i['price']*i['percent'])
                              #'('+str(i['percent']*10)+u'折)' if i['percent']!=1 else '',
                              #'%.2f'%(i['price']*i['percent'])
                              )
            
        return html

    def cupornlist(self):
        html=''
        foods=org.food.getcupornfoods(self.partnerid)
        for i in foods:
            html+=u'''<div class="fd_items">
                        <img src="http://img.%s/m/%s/%s" alt="%s"/>
                        <span class="zhekou">%i折</span>
                        <h3 class="name">%s%s</h3>
                        <span class="price">￥%s</span>
                        <a href="javascript:cart.add({'id':'%s','name':'%s','price':%s});" class="add">&nbsp;</a>
                    </div>'''%(
                              tpl.host,
                              'common' if i['img']=='' else self.partnerid,
                              'food_nopic.gif' if i['img']=='' else i['img'],
                              i['name'],
                              i['percent']*10,
                              i['name'],
                              '<br /><em>('+i['note']+')</em>' if i['note']!='' else '',
                             #self.partnerid,
                              '%.2f'%(i['price']*i['percent']),
                              i['id'],
                              i['name'],
                              '%.2f'%(i['price']*i['percent'])
                              #'('+str(i['percent']*10)+u'折)' if i['percent']!=1 else '',
                              #'%.2f'%(i['price']*i['percent'])
                              )
            
        return html

class order(base):
    def GET(self):
        ck_cart=web.cookies(cart=None).cart
        if ck_cart==None or ck_cart=='0':
            return u'''<div style="margin:50px auto;color:green;font-size:16px;font-weight:bold;text-align:center">
                      %s</div><script>setTimeout(function(){location.replace("/index")},2000);</script>
                        '''%('餐盒还是空的喔！请订餐后继续。'.decode('utf-8'))
        _cart=cart(ck_cart)
        _member=self.getmember()
        
        return render.submitorder(
                                  cartinfo=_cart.buildInfo().replace('\r\n','<br />'),
                                  tt_fee=_cart.mathfee(),        #总金额
                                  tpl=tpl,
                                  partner=self.getpartner(),
                                  member=None if _member==None else _member[0]
                            )
    
    def POST(self):
        req=web.input(phone='',address='')
        cart=web.cookies().cart
        _member=self.getmember()
        memberid=-1 if _member==None else _member[0]['id']
        
        data={
              'cart':cart,
              'memberid':memberid,
              'o_paymethod':1,
              'o_sendtime':org.utility.timestr(),
              'o_phone':req.phone.encode('utf-8'),
              'o_address':req.address.encode('utf-8'),
              'o_note':req.note.encode('utf-8')
              }
        
        submitOrder(self.partnerid,data)
        
        '发送短信'
        #import org.sms
        #org.sms.sendsms(req.phone,'')
        
        '清除菜单'
        web.setcookie('cart', '/',0,path='/')
        
        return render.completeorder()        

class about(base):
    def GET(self):
        return render.about(tpl=tpl,partner=self.getpartner())

class error:
    def GET(self):
        return render.error()
    
class login(base):
    def GET(self):
        returnuri=web.input(returnuri='/').returnuri
        return render.login(tpl=tpl,partner=self.getpartner(),msg=None,returnuri=returnuri)
    
    def POST(self):    
        request=web.input(username='',password='',returnuri='/index')
        
        if member_login(request.username,request.password):
            return u'<script>window.parent.location.href="%s"</script>'%(request.returnuri)
        else:
            return u'<script>window.parent.tiperr(1)</script>'
        
class user(base):
    def GET(self,action):
        return eval('self.%s()'%(action))
    
    def register(self):
        '去往注册'
        return web.seeother('http://%s.%s/register.html?partnerid=%s&returnURI=http://%s%s'%(
                                'user' if self.partnerid=='666888' else 'www',
                                tpl.host,
                                self.partnerid,
                                web.ctx['host'],
                                web.input(returnURI='/').returnURI
                             ))
    
    def regfinish(self):
        return render.login(tpl=tpl,partner=self.getpartner()\
                            ,msg=u'<span style="color:green">恭喜,注册成功！请输入帐号密码登录.</span>',returnuri='/')
    
    def exit(self):
        web.setcookie('token', '', expires=0)
        return web.seeother('/')
    def center(self):
        token=web.cookies(token='').token
        if token=='':
            return web.seeother('/login.html')
        else:
            uri='http://user.%s/autologin?token=%s&partnerid=%s&key=%s'%(
                tpl.host,
                token,
                self.partnerid,
                '$www.ops.cc'
                )
            uri=uri.replace('\n','')
            #return '<script>location.replace(\'%s\')</script>'%(uri)
            return web.seeother(uri)
        