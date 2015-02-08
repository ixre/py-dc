#-*-encoding:utf-8-*-
import web
from classes import *

urls=(
      '/(register|login).html','passport',
      '/(valid_[a-z]+)','passport',
      '/autologin','autologin',
      '/user/([\S\s]*)','user',
      '/([\s\S]*)','index'
    )

app=web.application(urls,globals())
#if __name__=='__main__':
#    app.run()

application=app.wsgifunc()