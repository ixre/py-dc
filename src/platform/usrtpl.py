#-*- coding:utf-8 -*-
from string import Template
import web
import org.conf
from org.user import gethost

HOST=org.conf.host

def top(title):
    '页头'
    tpl=Template('''<!doctype>
    <html>
    <head>
        <title>${title}</title>
        <script type="text/javascript" src="http://img.${host}/scripts/global.js"></script>
        <link rel="StyleSheet" type="text/css" href="http://img.${host}/css/usrcent/usrcent.css"/>
    </head>
    <body>
        <div class="topwrap">
        <div id="top"><h1 class="sys">会员中心</h1>
                <div class="nav">
                    <a href="${home}/" target="_blank">首页</a>
                    <a href="javascript:;" class="current">用户</a>
                    <a href="#">商城</a>
                    <a href="${home}/order" target="_blank">订餐</a>
                </div>
                <div class="usr">
                    欢迎您：<span id="usrinfo">..</span>&nbsp;[ <a href="exit">退出</a> ]
                </div>
            </div>
            <script type="text/javascript">$ajaxfunc('getname','',function(x){j.$('usrinfo').innerHTML=x;},function(x){/*document.write(x)*/});</script>
            </div>
            ''')
    home_domain=u'#'
    partnerid=web.cookies(partnerid=None).partnerid
    if partnerid!=None:
        home_domain='http://%s'%(gethost(partnerid).encode('utf-8'))
    
    return tpl.safe_substitute({'title':title,'host':HOST,'home':home_domain})
    

def footer():
    '页脚'
    tpl=Template('''
            <div class="clearfix"></div>
            <div id="footer">2012 &copy;${companyname}&nbsp;版权所有</div>
        </body>
        </html>
        ''')
    
    return tpl.safe_substitute({'companyname':'万绿园网络餐厅'})


def menu(linkname):
    data=[{
          'id':0,'name':'用户中心','childs':[
                              ('会员首页','index'),
                              ('修改资料','modify_profile'),
                              ('退出','exit.html')
                              ]
          },
          {
            'id':1,'name':'订单管理','childs':[
                                ('我的订单','orders'),
                                ('处理中订单','orders?status=0#_proccess'),
                                ('已完成订单','orders?status=3#_proccess'),
                                ('已作废订单','orders?status=-1#_deleted')
                                ]
           },
          
          {
             'id':2,'name':'我的收入','childs':[
                                 ('申请提现','bank_applycash'),
                                 ('订单返现业务信息','order_backcash')
                               ]
           }
         ]
    
    html='<div id="navs">'
    for m in data:
        html+='<div class="title menu%d">%s</div><ul>'%(m['id'],m['name'])
        for (a,b) in m['childs']:
            html+='<li%s><a href="%s">%s</a></li>'%('' if linkname!=a else ' class="selected"',b,a)
        html+='</ul>'
        
    html+='</div>'
    
    html+='<br /><div class="f12" style="padding:0 20px">版本:v&nbsp;0.1</div>'
    
    return html
          