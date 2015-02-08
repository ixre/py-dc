#-*- encoding:utf-8 -*-
import web
from classes import *
import tpl

urls=(
     '/(index|main)*','index',
     '/error','error',
     '/order','order',
     '/about','about',
     '/login.html','login',
     '/user/([\S\s]+).html','user'
     )

app=web.application(urls,globals())

  
#if __name__=='__main__':
#    app.run()

application=app.wsgifunc()