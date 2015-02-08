#-*- encoding:utf-8 -*-
import web
import base64

def encodetick(username,userpwd):
    '加密用户密码，存放的客户端'
    return base64.encodestring('username=%s;tick=%s'%(
                        username,
                        userpwd)
                               ).replace('m','mb')
                               
    