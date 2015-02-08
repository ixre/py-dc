# -*-encoding:utf-8 -*-
import web
from classes import *

urls=(
      '/','index',
      '/login','login',
      '/index','actionentry',
      '/login1','login1'
     )

app=web.application(urls,globals())

#if __name__=='__main__':
#    app.run()

application=app.wsgifunc()
