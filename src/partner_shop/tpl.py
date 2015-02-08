#-*- coding:utf-8 -*-
import web
import org.conf
from org.user import getUStat
from org.member import getMember

host=org.conf.host

cmrender=web.template.render('templates/comm')

def header():
    notice=org.user.getpage(self.partnerid,'notice').replace('\n','<br />')
    return cmrender.header()

def notice(partnerid):
    return org.user.getpage(partnerid,'notice') #.replace('\n','<br />')
                                
    
def navigator(index):
    return cmrender.navigator()

def footer(partner):
    return cmrender.footer(partner=partner)

def header_user_part(partner):
    usr=getUStat()
    if usr==None:
        return u'您好，欢迎您光临！<a href="/user/register.html">注册</a> | <a href="/login.html">登录</a>'
    else:
        member=getMember(usr[1])
        return u'欢迎您：<span id="state_user" style="color:green">%s</span> <a href="/user/center.html" target="_blank">用户中心</a> | <a href="/user/exit.html">退出登录</a>'%(
                                                                                                                                        member[0]['realname'] if member[0]['realname']!='' else member[0]['username']
                                                                                                                                     )
        