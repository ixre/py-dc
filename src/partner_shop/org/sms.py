#-*- encoding:utf-8 -*-
import urllib,urllib2
import time

def sendsms(phone,content):
    '发送短信息'
    data={
            'uid':'6',
            'pwd':'123456',
            'phone':phone,
            'conent':content,
            'sendtime':time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
          }

    request=urllib2.Request('http://sms.ops.cc:8080/gateway',urllib.urlencode(data))
    response=urllib2.urlopen(request)
    return response.code==200