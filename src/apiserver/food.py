#-*-encoding:utf-8-*-
import os,web
import base64

class food:
    def POST(self):
        action=web.input().action
        return eval('self.%s()'%(action))
    def GET(self):
        return self.POST()
        
    def saveitempic(self):
        '保存食物图片'
        req=web.input()
        partnerid=req.partnerid
        filename=req.filename
        data=req.data
        
        filedir='%s/imgserver/m/%s/'%(
                            os.path.abspath('../'),
                            partnerid
                            )
        
        filepath=filedir+filename
        if os.path.exists(filedir)==False:
            os.makedirs(filedir)
        
        data=base64.decodestring(data)
        
        f=open(filepath,'wb')
        f.write(data)
        f.flush()
        f.close()
        
        return 'True'