# -*-encoding:utf-8 -*-
import web

render=web.template.render('templates/master/')

class masterPage(object):
	'管理页面基类型，判断有无权限执行操作'
	def __init__(self):
		self.render=render