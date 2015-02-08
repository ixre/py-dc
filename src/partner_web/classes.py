#-*-encoding:utf-8-*-
import web
import org.user,org.member,org.food,org.order,org.conf
from org.encrypt import *
from org.db import newdb
from base import *
from org.utility import *
import json,time,base64

class login1(authbase):
    def GET(self):
        return render.x()
    def POST(self):
        x= web.input()
        raise Exception(self.partnerID)
        
class login:
    def GET(self):
        web.setcookie('token','',expires=0,path='/')
        return render.login(msg='')
        
    def POST(self):
        request=web.input()
        usr=request.username
        pwd=request.password
        _encodepwd=org.user.encryptPwd(usr,pwd)
        
        
        if org.user.isExistsPartner(usr,_encodepwd):
            ptid=org.user.getpartnerid(usr)                         #partner ID
            org.user.saveUStat(ptid,usr,_encodepwd,3600*24, '/')    #保存状态 24小时有效
            
            #userlib.updatelastlogin(request.username)
            #web.setcookie('lastlogintime',user['lastlogintime'],path='/',expires=3600*24*365*2)
            return web.SeeOther('/')
        
        return render.login(msg='用户或密码不正确!')
        
class index(authbase):
    def GET(self):
        if self.haslogin:
            vir={}                                      #服务器环境
            partner=org.user.getpartner(self.username)
            vir['ip']=web.ctx['ip']
            vir['location']=getlocal(vir['ip'])
            
            return render.index(pt=partner,vir=vir)
        else:
            return web.seeother('login')
        
class actionentry(authbase):
    '操作入口'
    def GET(self):
        if self.haslogin==False:
            return '<script>window.parent.userExpires()</script>'
        else:
            m=web.input().m
            act=web.input().act
            return eval('%s(%s).%s()'%(m,self.partnerID,act))
        
    def POST(self):
        if self.haslogin:
            m=web.input().m
            act=web.input().act
            return eval('%s(%s).%s_post()'%(m,self.partnerID,act))
        else:return ''

#============ ENTRY CLASS ===================#
class food:
    def __init__(self,id):        
        self.partnerID=id
    
    '''============== Category ============='''
    def category(self):
        cates=org.food.getcates(self.partnerID)
        '获取父分类并返回JSON'
        categories=[
            {'id':0,'name':'--'}
        ]
        for i in cates:
            if i['cpid']==0:
                categories.append({'id':i['id'],'name':i['name']})
                   
        catejson=json.dumps(categories)
        return render.foodcategory(catejson=catejson)
            
    def category_post(self):
        '''
        获取分类JSON
        $dtype  数据类型 [ 2:新增菜色时返回格式 ]
        '''
        cates=org.food.getcates(self.partnerID)
        web.header('Content-Type','text/plain; charset=utf-8', unique=True) 
        
        dtype=web.input(dtype=None).dtype
        if dtype=='2':
            value=web.input(value=None).value
            if value==None or value=='':
                cates[0]['selected']='true'
            else:
                for i in cates:
                    if i['id']==value:
                        i['selected']='true'
                    
            return json.dumps(cates)
        else:
            return '{"total":%d,"rows":%s}'%(
                         len(cates),
                         json.dumps(cates))
        
    def category2_post(self):
        do=web.input().do
        items=json.loads(web.input(_items='[]')._items)
        for i in items:
            if i['name']!='':
                if do=='add':
                    org.food.addcate(
                                 self.partnerID,
                                 0 if i['cpid']=='' else i['cpid'],
                                 i['name']
                                )
                elif do=='update':
                    org.food.updatecate(
                                        self.partnerID,
                                        i['id'],
                                        0 if i['cpid']=='' else i['cpid'],
                                        i['name'],
                                        i['idx']
                                        )
                    
                
        return 'ok'
    
    def delcategory_post(self):
        id=web.input().id
        return org.food.delcate(id,self.partnerID)
    
    '''============== FOODS ================'''
    def foods(self):
        '''
        菜单列表
        '''
        req=web.input(cid=-1,returnUri='')
        _dataurl='index?m=food&act=foods&ajax=1&cid=%s'%(req.cid)
        
        return render.foods(dataurl=_dataurl)
    
    def foods_post(self):  
        '食物列表' 
        req=web.input(cid=-1,rows=0,page=1)
        web.header('Content-Type','text/plain')
        foods=org.food.getfooditems(
                                    self.partnerID,
                                    int(req.page),
                                    int(req.rows),
                                    int(req.cid)
                                    )
        
        nums=org.food.fooditemsCount(self.partnerID,int(req.cid))
        return '{"total":%d,"rows":%s}'%(nums,json.dumps(foods))
    
    def newfooditem(self):
        '''
        新增菜单
        '''
        req=web.input(returnUri='')
        elemSubm=''
        list=org.user.getsubs(self.partnerID)
        for i in list:
            elemSubm+='<input type="checkbox" value="%s" name="subm%s" checked="checked"/>%s'%(
                                                                    i['id'],
                                                                    i['id'],
                                                                    i['name']
                                                                           )
        return render.newfooditem(elem_subm=elemSubm,return_url=req.returnUri)
    
    def newfooditem_post(self):
        req=web.input(pic={})
        
        '''上传图片'''
        pic=''                                  #食物图片
        
        if req.pic.filename!='':
            pic=time.strftime('%Y%m%d%H%M%S.gif',time.localtime())
            data=base64.encodestring(req.pic.file.read())
            result=org.food.saveitempic(self.partnerID,pic,data)
            '上传失败'
            if result==False:
                pic=''
        
        applySubms=''                           #供应商家
        for i in req:
            if i.startswith('subm'):
                applySubms+=eval('req.%s+","'%(i))
       
        
        
        try:
            org.food.addfooditem(req.name,
                             req.cid,
                             pic,
                             applySubms,
                             req.note,
                             req.desc,
                             float(req.price),
                             float(req.percent)/100
                             )
        except Exception,msg:
           return msg
        
        return u'新增成功!'
    
    def delfood_post(self):
        '删除食物'
        id=int(web.input().id)
        return org.food.delete(self.partnerID,id)
    
    def updateitem(self):
        req=web.input(returnUri='')
        
        _item=org.food.get(self.partnerID,int(req.id))                  #食物
        _img=''                                                         #图片
        if _item['img']!='':
            _img='<img src="http://img.%s/m/%s/%s" style="border:solid 1px #e5e5e5;padding:1px;margin:5px 0;width:120px;height:120px"/><input type="hidden" value="%s" name="img"/>'%(
                      org.conf.host,
                      self.partnerID,
                      _item['img'],
                      _item['img']
                    )
        
        '设置分店'
        elemSubm=''
        list=org.user.getsubs(self.partnerID)
        for i in list:
            elemSubm+='<input type="checkbox" value="%s" name="subm%s" %s/>%s'%(
                                                                    i['id'],
                                                                    i['id'],
                                                                    '' if _item['applysubs'].count('%d,'%(i['id']))==0 else 'checked="checked"',
                                                                    i['name']
                                                                           )
            
        return render.updatefooditem(item=_item,
                                     elem_subm=elemSubm,
                                     img=_img,
                                     return_url=req.returnUri
                                     )
    
    def updateitem_post(self):
        
        req=web.input(pic={},img='')
        
        '''食物图片'''
        pic=req.img         #原图片
        
        
        if req.pic.filename!='':
            pic=time.strftime('%Y%m%d%H%M%S.gif',time.localtime())
            data=base64.encodestring(req.pic.file.read() )
            result=org.food.saveitempic(self.partnerID,pic,data)
            '上传失败'
            if result==False:
                pic=req.img
        
        applySubms=''                           #供应商家
        for i in req:
            if i.startswith('subm'):
                applySubms+=eval('req.%s+","'%(i))
       
        
        try:
            org.food.updatefooditem(
                             int(req.id),
                             req.name,
                             req.cid,
                             pic,
                             applySubms,
                             req.note,
                             req.desc,
                             float(req.price),
                             float(req.percent)/100
                             )
        except Exception,msg:
            return u'错误',msg
        
        return u'修改成功!'
        
class subm:
    '分店'
    def __init__(self,id):       
        self.partnerID=id
    
    def list(self):
        '分店列表'
        return render.subm()
    def list_post(self):
        '分店json数据'
        web.header('Content-Type','text/plain')
        list=org.user.getsubs(self.partnerID)
        return json.dumps(list)
    
    def dropdown_post(self):
        '下拉列表数据'
        web.header('Content-Type','text/plain')
        list=org.user.getsubs(self.partnerID)
        list[0]['selected']='true'
        return json.dumps(list)
        
    def do_post(self):
        do=web.input().do
        items=json.loads(web.input(_items='[]')._items)
        for i in items:
            if i['name']!='':
                if do=='add':
                    org.user.addsub(
                                 self.partnerID,
                                 i['name'],
                                 i['address'],
                                 i['phone'],
                                 i['idx'],
                                 i['state']
                                )
                elif do=='update':
                    org.user.updatesub(
                                     i['id'],
                                     self.partnerID,
                                     i['name'],
                                     i['address'],
                                     i['phone'],
                                     i['idx'],
                                     i['state']
                                    )
                
        return ''

class order:
    '订单'
    def __init__(self,id):       
        self.partnerID=id
        
    def list(self):
        req=web.input(status=0)
        url='index?m=order&act=list&ajax=1&status=%s'%(req.status)
        subs=org.user.getsubs(self.partnerID)
        
        return render.orderlist(dataurl=url,subs_json=json.dumps(subs))
    
    def list_post(self):
        web.header('Content-Type','text/plain')
        req=web.input(status=0)
        data=org.order.getorders(self.partnerID,req.status,int(req.page),int(req.rows))
        _orders=data[1]
        
        return '{"total":%d,"rows":%s}'%(data[0],json.dumps(_orders))
        
    def del_post(self):
        '作废订单'
        id=web.input().id
        return org.order.delorder(self.partnerID,id)
    
    def view(self):
        '查看订单'
        req=web.input()
        order=org.order.getorder(req.id)
        if order==None or order['ptid']!=self.partnerID:
            return '订单不存在!'
        else:
            o_member=org.member.getMemberById(order['mid'])
            o_state=org.order.order_states[order['status']+1]
            o_paymethod=org.order.order_paymethods[order['paymethod']]
            o_sub=''
            
            __sub=org.user.getsub(order['ptsid'])
            if __sub==None:
                o_sub='未设置'
            else:
                o_sub='%s (%s)'%(__sub['name'],__sub['phone'])
            
            '处理按钮'
            handleHtml=''
            __s=order['status']
            if __s==0:
                handleHtml='''选择<input class="easyui-combobox"
                        id="subid"
                                                name="subid"
                                                url="index?m=subm&act=dropdown&ajax=1" 
                                                valueField="id" 
                                                textField="name" 
                                                panelHeight="auto" />
                                <input type="button" value="处理订单" onclick="setState(1)" />
                '''
            elif __s==1:
                handleHtml='<input type="button" value="配送订单" onclick="setState(2)" />'
                
            elif __s==2:
                handleHtml='<input type="button" value="配送完毕-> 完成订单" onclick="setState(3)" />'
            elif __s==3:
                handleHtml='恭喜，此订单已经完成！无需操作！'
            else:
                handleHtml='<span style="color:red">此订单已经作废！</span>'
            
            return render.orderview(
                                    request=req,
                                    order=order,
                                    o_member=o_member,
                                    o_state=o_state,
                                    o_paymethod=o_paymethod,
                                    o_sub=o_sub,
                                    elem_handle=handleHtml
                                    )
            
    def setstate_post(self):
        req=web.input(subid=0,state=1)
        order=org.order.getorder(req.id)
        _status=int(req.state)
        if order['status']>int(req.state):
            return '无法设置订单状态:%s'%org.order.order_states[_status]
        else:
            if _status==1:
                '设置分店'
                result2=org.order.setsub(self.partnerID,req.id,req.subid)
                if result2==False:
                    return '无法由此分店配送，请刷新重试!'
                
            result=org.order.setstatus(self.partnerID,req.id,_status)
            if result:
                return ''
                
        return '设置失败'
  
class page:
    '页面管理'
    def __init__(self,id):       
        self.partnerID=id
        
    def __update_page__(self,msg):  
        '修改页面'        
        type=web.input(type='notice').type
        page_dict={
                   'notice':'商家公告',
                   'about':"商家介绍"
                   }
        #获取内容
        content=org.user.getpage(self.partnerID,type)
        
        return render.page_update(title=page_dict[type],content=content,msg=msg)
        
    def update(self):
        return self.__update_page__('')
        
    def update_post(self):  
        request=web.input(type='notice',content='')
        org.user.updatepage(self.partnerID,request.type,request.content)
        return self.__update_page__(u'修改成功')
        
        