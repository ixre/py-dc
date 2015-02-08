#-*-encoding:utf-*-
import web,re
import org.conf as conf
import org.utility
from org.member import *
from org.user import getUStat,gethost
from org.order import getmemberorders,order_states
from org.db import *
from org.utility import getlocal
import usrtpl


TPL_SSO=web.template.render('templates/passport')
TPL_USR=web.template.render('templates/user')

HOST=conf.host

class index:
    def GET(self,param):
        return 'Access prohibited!\r\npath:/%s'%(param)
    
    
class passport:
    def GET(self,action):
        url_pid=web.input(partnerid=None).partnerid
        partnerID=web.cookies(partnerid='').partnerid
        
        '保存COOKIE'
        if url_pid!=None and url_pid!='' and url_pid!=partnerID:
            partnerID=url_pid
            web.setcookie('partnerid',partnerID,httponly=True, path='/')
        
        return eval('self.%s(\'%s\')'%(action,partnerID))
        #return self.register(partnerID)
        
    def POST(self,action):
        return eval('self.%s_post()'%action)
    
    
    def register(self,partnerID):
        if partnerID=='':
            partnerID='10000'
            
        returnURI=web.input(returnURI='').returnURI
        if returnURI=='':
            returnURI='http://www.yyc668.com'
            
        return TPL_SSO.register(host=HOST,returnURI=returnURI)
    
    def register_post(self):
        request=web.input()
        
        member=request
        member.realname=''
        member.avatar=''
        member.birthday=''
        member.qq=''
        member.email=''
        member.regip=web.ctx['ip']
        
        tgid=0                      #推广用户ID
        
        if chkreg(member.username)==False:
            return u'<script>window.parent.uid.onblur();</script>'
        
        if request.tguser!='':
            if chktg(request.tguser)==False:
                return u'<script>window.parent.tguser.onblur();</script>'
            else:
                tgid=getid(request.tguser)
        
        '写入数据库'
        create_member(member,request.partnerid,tgid)
        try:
            import mall
            mall.adduser(member)
            
        except Exception,msg:
            return msg
                
        return u'<script>window.parent.regsucc()</script>'
    
    
    def valid_username(self,partnerid):
        username=web.input(username=None).username
        if username==None or username=='':
            return u'用户名不能为空!'
        elif chkreg(username)==False:
            return u'用户已经被占用'
        else:
            return ''
        
    def valid_tguser(self,partnerid):
        if chktg(web.input().user)==False:
            return u'推广帐号错误或已达上限'
        else:
            return ''
        
        
class autologin:  
    '自动登录'   
    def GET(self):
       token=web.input(token='').token
       key=web.input(key='').key
       partnerid=web.input(partnerid='').partnerid
       
       
       if token=='' or key!='$www.ops.cc' or partnerid=='' or org.user.getpartnerbyid(partnerid)==None:
           return 'login fail!'
       else:
           web.setcookie('token', token,httponly=True,path='/')
           web.setcookie('partnerid',partnerid,expires=3600*24*365,path='/')
           
           return web.SeeOther('/user/')

class user:
    def __init__(self):
        '初始化'
        self.memberuser=None
        self.member=None
        self.relation=None
        self.partnerid=web.cookies(partnerid='').partnerid
        
        usr=getUStat()
        if usr!=None:
            self.memberuser=usr[1]
            member=getMember(self.memberuser)
            self.member=member[0]
            self.relation=member[1]
            if self.member['avatar']=='' or self.member['avatar']==None:
                self.member['avatar']='http://img.%s/css/usrcent/noavatar.gif'%(HOST)
            
        else:
            uri='/' if self.partnerid=='' else 'http://'+gethost(self.partnerid)+'/login.html'
            web.seeother(uri)
            
    
    def reload(self):
        '重新加载数据'
        self.member=getMember(self.memberuser)[0]
                 
    def GET(self,action):
        if action=='':
            action='index'
            
        return eval('self.%s()'%(action))
    
    def POST(self,action):
        return eval('self.%s_post()'%(action))
        
        
    '''
    THESE IS GET METHODS
    '''    
    def index(self):
        
        account=getaccount(self.member['id'])           #会员账户
        
        ip=web.ctx['ip']
        local_html=u'<span class="local">%s</span>&nbsp;(&nbsp;IP:<span class="ip">%s</span>&nbsp;)'\
                    %(getlocal(ip),ip)
        
        return TPL_USR.user_index(host=conf.host,usrtpl=usrtpl,member=self.member,account=account,local=local_html)
      
    def exit(self):
        web.setcookie('token','',expires=0,httponly=False)
        return web.seeother('http://%s/user/exit.html'%(gethost(self.partnerid)))
    
        #return u'<span style="color:green">退出成功,5秒后转到首页！</span><script>setTimeout(function(){location.replace("http://%s")},3000);</script>'\
        #        %(gethost(self.partnerid))
                
    
    def modify_profile(self):
        return TPL_USR.modify_profile(host=HOST,usrtpl=usrtpl,member=self.member,msg='')
    
    def orders(self):
        request=web.input(status='',order='',desc='1',page=1)
        _pageSize=10
        _page=int(request.page)
        _status=''
        _order='createtime desc'
        
        if request.status!='':
            _status=' status=%d'%(int(request.status))
        if request.order!='':
            _order='%s %s'%(request.order,'DESC' if request.desc=='1' else 'ASC')
        
        order=getmemberorders(self.member['id'],_page,_pageSize,where=_status,orderby=_order)
        
        #tpl='orders'
        #if request.status=='1'
        pagedHtml='' if order[0]==0 else '页码：'
        _pages=order[0]/_pageSize
        if order[0]%_pageSize!=0:
            _pages+=1
            
        for i in xrange(1,_pages+1):
            if _page==i:
                pagedHtml+='<span class="current">%d</span>'%(i)
            else:
                pagedHtml+='<a href="?page=%d&order=%s&status=%s&desc=%s">%d</a>'%\
                                        (
                                            i,
                                            str(request.order),
                                            str(request.status),
                                            str(request.desc),
                                            i
                                        )
                                         
        
        tpl='orders'
        if request.status=='-1':
            tpl='orders_deleted'
        elif request.status=='3':
            tpl='orders_compelete'
        elif request.status=='0':
            tpl='orders_proccess'
        
        return eval('TPL_USR.'+tpl+'(host=HOST,usrtpl=usrtpl,member=self.member,orders=order[1],states=order_states,pagedHtml=pagedHtml)')
    
    def incomelog(self,type):
        request=web.input(order='',desc='1',page=1)
        _pageSize=10
        _page=int(request.page)
        _type=''
        _order='recordtime desc'
        
        if type!='':
            _type=' type=\'%s\''%(type)
        if request.order!='':
            _order='%s %s'%(request.order,'DESC' if request.desc=='1' else 'ASC')
        
        order=getincomelog(self.member['id'],_page,_pageSize,where=_type,orderby=_order)
        
        #tpl='orders'
        #if request.status=='1'
        pagedHtml='' if order[0]==0 else '页码：'
        _pages=order[0]/_pageSize
        if order[0]%_pageSize!=0:
            _pages+=1
            
        for i in xrange(1,_pages+1):
            if _page==i:
                pagedHtml+='<span class="current">%d</span>'%(i)
            else:
                pagedHtml+='<a href="?page=%d&order=%s&desc=%s">%d</a>'%\
                                        (
                                            i,
                                            str(request.order),
                                            str(request.desc),
                                            i
                                        )
                                         
        
        tpl='orders'
        if type=='backcash':
            tpl='income_backcash'
        
        return eval('TPL_USR.'+tpl+'(host=HOST,usrtpl=usrtpl,member=self.member,orders=order[1],states=order_states,pagedHtml=pagedHtml)')
    
    
    def order_backcash(self):
        return self.incomelog('backcash')
        
    '''
    THESE IS POST METHODS
    '''    
    def getname_post(self):
        '读取显示名称'
        web.header("Content-Type", "text/plain")
        realname= self.member['realname']
        return self.member['username'] if realname=='' or realname==None else realname
    
    def modify_profile_post(self):
        
        tipmsg=''
        
        request=web.input()
        
        _realname=request.realname
        _phone=request.phone
        _address=request.address
        _sex=request.sex
        _birthday=request.birthday
        _qq=request.qq
        _email=request.email
        
        if _realname=='':#re.match('^[\u4e00-\u9fa5]{2,10}$',_realname)==None:
            tipmsg+='请填写中文姓名<br />'
            
        if re.match('^(13[0-9]|15[1|2|3|4|5|6|8|9]|18[0|6|7|8|9])(\d{8})$',_phone)==None:
            tipmsg+='手机号码错误<br />'
            
        if _address=='' or len(_address)<8:
            tipmsg+='请填写完整的送餐地址<br />'
        
        '更新资料'
        if tipmsg=='':
            try:
                result=uppro(self.member['id'],_realname,_sex,_phone,_address,_birthday,_qq,_email)
                #if result:
                self.reload()
                tipmsg='修改成功'
                #else:
                #    tipmsg='修改失败，请重试'
                    
            except Exception,msg:
                tipmsg=msg
            
        return TPL_USR.modify_profile(host=HOST,usrtpl=usrtpl,member=self.member,msg=tipmsg)
    
    def bank_applycash(self):
        '申请提现'
        memberid=self.member['id']
        bankaccount=getbank(memberid)       
        account=getaccount(memberid)           #会员账户
        return TPL_USR.bank_applycash(host=HOST,usrtpl=usrtpl,account=account,bank=bankaccount)
        
    def bank_update_post(self):
        '更新银行帐号'
        request=web.input()
        upbank(self.member['id'],request.bankname,request.bankaccount)
        return '<script>window.parent.location.reload()</script>'
        