## deploy on windows7
- 安装Apache2.2，mod_wsgi模块放置到modules文件夹下
- 安装python2.7.x（可能要添加环境变量）（python,Apache,mod_wsgi必须都为32位或64位）
- 配置Apache(httpd.conf),添加一行 `LoadModule wsgi_module modules/mod_wsgi.so`，include自定义VirtualHost,添加`Include conf/extra/my.conf`
- 拷贝代码到服务器硬盘上
- 配置自定义VirtualHost,详见my.conf（根据服务器上代码的的路径修改）
- 修改settings.py中的db位置为实际代码部署的路径
- 更改部署代码的文件夹权限为所有权限（这一步可能不是必须的）
- 解决80端口冲突问题（这一步可能不是必须的）
- windows下防火墙问题

### my.conf
		#
		# Virtual Hosts
		#
		# If you want to maintain multiple domains/hostnames on your
		# machine you can setup VirtualHost containers for them. Most configurations
		# use only name-based virtual hosts so the server doesn't need to worry about
		# IP addresses. This is indicated by the asterisks in the directives below.
		#
		# Please see the documentation at 
		# <URL:http://httpd.apache.org/docs/2.2/vhosts/>
		# for further details before you try to setup virtual hosts.
		#
		# You may use the command line option '-S' to verify your virtual host
		# configuration.

		#
		# Use name-based virtual hosting.
		#
		#NameVirtualHost *:80

		#
		# VirtualHost example:
		# Almost any Apache directive may go into a VirtualHost container.
		# The first VirtualHost section is used for all requests that do not
		# match a ServerName or ServerAlias in any <VirtualHost> block.
		#
		WSGIPythonPath F:\schedule\myapp;F:\schedule\env\Lib\site-packages
		Alias /static F:\schedule\myapp\static
		AliasMatch ^/([^/]*\.css) F:\schedule\myapp\static\css\$1


		<VirtualHost *:80>
		    ServerName localhost 
		    <Directory /> 
		        Options FollowSymLinks 
		        AllowOverride None
		        Order allow,deny 
		        Allow from all 
		    </Directory>
		    <Directory F:\schedule\myapp\static>
		        Order deny,allow
		        Allow from all
		    </Directory>

		    WSGIScriptAlias / F:\schedule\myapp\setting.wsgi

		    <Directory F:\schedule\myapp>
		    <Files setting.wsgi>
		        Order allow,deny 
		        Allow from all
		    </Files>
		    </Directory>
		</VirtualHost>

## myapp/setting.wsgi

	import os 
	import sys 
	sys.stdout = sys.stderr 
	from os.path import abspath, dirname, join 
	from django.core.handlers.wsgi import WSGIHandler 
	sys.path.insert(0, abspath(join(dirname(__file__), "./"))) 
	os.environ["DJANGO_SETTINGS_MODULE"] = "myapp.settings" #your settings module 
	application = WSGIHandler()