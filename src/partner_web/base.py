#-*-encoding:utf-8 -*-
import web
import org.user

render=web.template.render('templates/')

class authbase(object):
    def __init__(self):
        usr=org.user.getUStat()
        if usr!=None and org.user.isExistsPartner(usr[1],usr[2]):
            self.partnerID=usr[0]
            self.username=usr[1]
            self.haslogin=True
        else:
            self.haslogin=False
            self.username=None
           