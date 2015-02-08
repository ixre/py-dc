import web
from passport import *
from food import *
from order import *

urls=(
      '/','index',
      '/user','passportapi',
      '/food','food',
      '/order','order'
      )

app=web.application(urls,globals())

class index(object):
    def GET(self):
        return 'test page'

#if __name__=='__main__':
#    app.run();
application=app.wsgifunc()
