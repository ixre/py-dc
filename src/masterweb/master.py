#-*-encoding:utf-8-*-
from basepage import *

class index(masterPage):
    def GET(self):
        return self.render.index()
    
    

############# 商家 ######################
class pattern(masterPage):
    def GET(self,action):
        return self.render.new_pattern()