#-*-encoding:utf-8-*-
import urllib,urllib2
import re,time

def getlocal(ip):
    '获取地理位置'
    try:
        request=urllib2.Request('http://www.ip138.com/ips1388.asp?ip=%s&action=2'%(ip))
        request.add_header('HTTP_REFERER','http://www.ip138.com')
        data=urllib2.urlopen(request).read()
        match=re.search(u'<li>本站主数据：([^<]+)</li>',data.decode('gb2312'))
        return match.groups()[0]
    except Exception,msg:
        return u'未知地区'

def timestr(_time=None):
    '获取时间字符串'
    if _time==None:
        _time=time.localtime()
        
    return time.strftime('%Y-%m-%d %H:%M:%S',_time)   
    