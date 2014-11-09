#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import os,datetime,string
import chardet
import sys
import re
import time
from bs4 import BeautifulSoup

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib

def _format_addr(s):
	##解析地址，比如 user xxx@gmail.com
    name, addr = parseaddr(s)
	##简单的格式化
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))
##用于发邮件
def send_mail(addr_infos):
	#初始化配置文件
	#init()
	from_addr = 'xxx@gmail.com'
	password = 'xxx'
	to_addr = 'xxx@qq.com'
	smtp_server = 'smtp.gmail.com'
	smtp_port = '587'
	content=''
	for item in addr_infos:
		content  = content +item.to_string()
	content = content +'hello, send by hustraiet'

	msg = MIMEText(content, 'html', 'utf-8')
	msg['From'] = _format_addr(u'58spider <%s>' % from_addr)
	msg['To'] = _format_addr(u'亲 <%s>' % to_addr)
	msg['Subject'] = Header(u'亲，你关注的商品有新发现了', 'utf-8').encode()

	server = smtplib.SMTP(smtp_server, smtp_port)
	server.starttls()
	server.set_debuglevel(1)
	server.login(from_addr, password)
	server.sendmail(from_addr, [to_addr], msg.as_string())
	server.quit()

#将抓取到的有用信息封装成类
class Info(object):
	def __init__(self,title='',href = '',addr = '',description=''):
		self.title = title
		self.href = href
		self.addr = addr
		self.description=description
	def get_addr(self):
		return self.addr
	def to_string(self):
		res =  '<br><a href = \'%s\' >%s</a><br>' %(self.href ,self.title)
		res = res +self.description + '<br><hr>'
		return res


##定义抓取网页的类
class tc58(object):
	def __init__(self,url):
		self.__url = url
		self.addr_infos = []
	##抓取网页到本地
	def load_page(self):
		opener = urllib2.build_opener()
		f = opener.open(self.__url)
		html = f.read()
		self.__html = html
		f.close()
		return html
	##解析网页元素，找到自己要找的信息，这里要根据实际情况分析标签
	def paser_html(self):

		#print html
		soup = BeautifulSoup(self.__html)
		tables =soup.html.body.find('section',id="mainlist").find('div',id = 'infolist').find_all('table',class_='tbimg')
		table = tables[1].find_all("tr")
		addr_infos = []
		for element in table:
			html = element.find_all('td')
			#print "len (td):%d"%len(html)
			t1 = html[1]
			t2 = html[2]
			#print type(html)
			title =  t1.a.get_text()
			#print "title:" + title
			href =  t1.a.get("href")
			#print "href:" + href
			description =  t1.get_text()
			addr_all =  t1.find("span",class_="fl")
			addr_all = addr_all.get_text()
			#print 'addr_all:'+addr_all


			title = title.encode("utf-8")
			href = href.encode("utf-8")
			addr_all = addr_all.encode("utf-8")
			description = description.encode("utf-8")
			i = Info(title,href,addr_all,description)
			addr_infos.append(i)
		self.addr_infos = addr_infos


	def send_mail(self):
		pass
	def get_addr_infos(self):
		return self.addr_infos
	def run(self):
		self.load_page()
		self.paser_html()

##上次抓取的最新事件（min）
last_time = 0
#time.sleep(loop_time)
##60秒钟抓取一次(s)
loop_time = 2.0

##这个函数太蛋疼了，乱码问题一直解决不了，所以，，，，，
def get_time(addr_time):

	res = addr_time.split('/')
	#print res
	if len(res)>1:
		shijian = res[1]
		shijians = shijian.split('-')
		#指处理，小时和分钟，对于11-11这样的日期没必要处理
		if len(shijians)==1:
			#print shijians
			#取得中文，也就是后面的单位
			r = re.sub("[A-Za-z0-9\[\`\~\!\@\#\$\^\&\*\(\)\=\|\{\}\'\:\;\'\,\[\]\.\<\>\/\?\~\！\@\#\\\&\*\%]", "", shijians[0])
			#取得前面的数字
			num = filter(str.isdigit, shijians[0])
			#print num
			r = ''.join(r.strip())
			r = repr(r)
			if len(r) == 26:
				#print "this is xiaoshi"
				#print 'return:%d' %(num*60)
				return num*60
			elif len(r) == 36:
				#print 'this is fenzhong'
				#print 'return:%d' %(num)
				return num
			
			
		#print shijians
	return 3600*3600

def find_head(all):
	##得到实际的上次的时间
	global last_time
	last_time = int(last_time) + int(loop_time)
	min_time = 0.0
	##返回的结果
	res = []
	##第一个的时间一定是最小的
	if len(all)>0:
		min_time = get_time(all[0].get_addr())
	for item in all:
		##单位是s
		shijian = get_time(item.get_addr())
		#print 'recv time %s' % shijian
		if shijian < last_time:
			res.append(item)
	last_time = min_time
	return res
#这是搜索的基地址
__INITURL__ = 'http://wh.58.com/pbdn/?key='

def fun_loop(key):
	##指定第一次，来初始化last
	first = True
	for i in range(100000):
		#print __INITURL__+key
		tc = tc58(__INITURL__+key)
		#开始抓取网页
		tc.run()
		all =  tc.get_addr_infos()
		#对于第一次，则只计算last_time
		if first == True:
			if(len(all)>0):
				last_time = get_time(all[0].get_addr())
			first = False
			#print 'last_time:%d'%int(last_time)
		
		else:
			##找到最新的更新
			new = find_head(all)
			print 'len(new):%d'%len(new)
			print 'last_time:%d' % int(last_time)
			#如果有最新的更细，则发邮件通知
			if len(new)>0:
				send_mail(new)
		##间隔一段时间
		time.sleep(loop_time)
	
	#print len(all)

if __name__ == '__main__':
	key = 'ipad'
	fun_loop(key)


