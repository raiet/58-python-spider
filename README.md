58-python-spider
================

根据用户的关键字，定时定向抓取58同城的页面，分析网页结果，将最新的发布信息通过邮件发给用户，已达到时刻关注网页的效果


###使用方法

1， 需要修改下面的信息

  	from_addr = 'xxx@gmail.com'
	password = 'xxx'
	to_addr = 'xxx@qq.com'
	smtp_server = 'smtp.gmail.com'
	smtp_port = '587'
	
  根据发送邮箱，配置邮件服务器的信息   
  
2，指定查询的关键字  

	key = ‘ipad’
	
3,修改全局的查询间隔时间

	loop_time = 2.0

4,ok,运行  

	python spider.py
