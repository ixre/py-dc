# -*-encoding:utf-8 -*-
import web
from master import *

urls=(
      '/','index',
      '/pattern/([^/]+)','pattern'
     )

app=web.application(urls,globals())


if __name__=='__main__':
    app.run()