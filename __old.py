#!/bin/env python
#-*- encoding:utf-8 -*-
#support on 

import os.path
import Image
import hashlib
import time
import random
import tempfile
import torndb
import tornado
import tornado.httpserver
import tornado.ioloop
from tornado import web
from tornado.options import define, options
from tornado import escape 

#define("port", default=8000, help="run on the given port", type=int)
#$python server.py --port=port-num
define("port",default=8888,help="port",type=int)
define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="Personal", help="database name")
define("mysql_user", default="root", help="database user")
define("mysql_password", default="", help="database password")
define("picrootpath",default="",help="store picture")
define("tempdir",default="",help="create temporary file in it")

#define("storedvair",default={},help="store vair",type=dict)

#transmit parameter to subclass in initialize

'''
  user : already login
  {
{user{id1:True, id2:True...}}
    }
'''
_storedvair = {}

#standard response format
_format = {}

#def handle_request(request):
#    message = "hello,you request %s\n" % request.uri
#    request.connection.write("HTTP1.1 200 OK\r\nContent-Length:%d\r\n\r\n%s" % (
#    len(message),message))
#    request.finish()


class MainRequestHandler(tornado.web.RequestHandler):
    #render to index.html
    #Subclass RequestHandler,use get method
    #SUPPORTED_METHOD { }
    #attribute

    '''use trans parameter,subclass inherit from it'''
    self._storedvair = _storedvair
    self._format = _format
    @property
    def db(self):
        return self.application.db

    def get_current_user(self,user):
        return self.get_secure_cookie(user)
    #def get():
        #pass parameter from self.render("xxx.html",***)
    #self.render("index.html")
        #self.get_argument('','')   variable default-value	
    #def get_current_user(self):
    #    user_id = self.get_secure_cookie("user")
    #    if not user_id: return None
    def set_response_json(self, key, value):
		if key is None or value is None:
			return
		self._format[key] = value

	def	get_response_json(self):
		return escape.json_encode(_format)

	def del_response_json(self, key):
		del _format[key]

	def clear_response_json(self):
		_format.clear()

class MaintoHandler(MainRequestHandler):
    def set_default_headers(self):
        #use Auth-temp as user identify
        add_header("Auth-temp","None")

    def _test_timeout(self,_id):
        #timeout = 600s
        _temp_time = int(time.time()) - _storedvair[_id][1]
        if _temp_time >= 600:
            del _storedvair[_id]


class RegisterHandler(MaintoHandler):
	def post(self):
		#client
		Id = self.get_argument("CId",None)
		Password = self.get_argument("CPassword",None)
		Sex = self.get_argument("CSex",None)
		if Id is not None and Password is not None and Sex is not None:
			query_string_register = "SELECT * FROM user WHERE id=%s" % Id
			result_register = self.db.get(query_string_register)
			if result_register is None:
				create_account_string = "INSERT INTO user(id,password,sex)values(%s,%s,%s)" % (Id,Password,Sex)
				self.db.execute(create_account_string)
				self.write("Successful!")
		else:
			self.write("You can't register!")

	def put(self):
		'''CNN_password is rewrite it,Cpsword is old password,cn & cnn is new password'''
		_auth_list = map(lambda x : self.get_argument(x),['C_Id','C_Password','CN_Password','CNN_Password'])
		query_string_match_passwd = "SELECT * FROM user WHERE id=%s" % _auth_list[0]
		result = self.db.get(query_string_login)
		if _auth_list[1] != result:
			self.write("Old Passwd can't match!")
			return
		else:
			if _auth_list[2] == _auth_list[3]:
				edit_user_passwd = "UPDATE user SET password = %s WHERE id = %s" % (_auth_list[2],_auth_list[0])
				self.db.execute(edit_user_passwd)
				self.write("Successful edit password")
			else:
				self.write("Please use the same passwd!")
				return



class AuthLogoutHandler(MainRequestHandler):
    def get(self):
		#!read HTTP request-header Auth-temp
		_temp_authnum = None
		try:	
			del self._storedvair['login'][_temp_authnum]
		
		#self.clear_cookie("user")
        #self.redirect(self.get_argument("next", "/"))
		
		#???
		#???
		self.db.close()

class AuthLoginHandler(MaintoHandler):
    @tornado.web.asynchronous
    def post(self):
        #from URL 
        Id = self.get_argument("CId",None)
        Password = self.get_argument("CPassword",None)

        query_string_login = "SELECT * FROM user WHERE id=%s" % Id
        result = self.db.get(query_string_login)
        if result['password'] != Password:
            #unsuccessful
            raise tornado.web.HTTPError(401)
        else:
            #self.set_secure_cookie(Id,Id)
            #use Auth-temp as user identify
            _temp = hashlib.md5(Password)
            self.set_header("Auth-temp",_temp.hexdigest())
            _storedvair[Id] = (_temp.hexdigest(),int(time.time())

    #def post(self):
    #    Id = self.get_argument("CId",None)
    #   Password = self.get_argument("CPassword",None)


class UploadFileHandler(MainRequestHandler):
	def get(self):
		pass
	def post(self):
		'''
		simulate post-table
			<form action='file' enctype="multipart/form-data" method='post'>
			    <input type='file' name='file'/><br/>
				<input type='submit' value='submit'/>
			</form>
		'''
		#user file
		if self.request.files == {} or 'file' not in self.request.files:
			#no-pic to upload
			return
		image_list = ['image/gif','image/jpeg',
						'image/pjpeg','image/png','image/bmp']
		upload__path = self.current_user_root_path
		file_metas = self.request.files['file']
		send_file = file_metas[0]
		if send_file['content_type'] not in image_list:
			#not match format
			#self.write("please use gif or png or bmp or..format")
			return
		if len(send_file['body']) > 4*1024*1024:
			#self.write("please transmit 4MB and below it size file")
			return
		#if test image length*width
		temp_file = tempfile.NamedTemporaryFile(delete=True)
		temp_file.write(send_file['body'])
		temp_file.seek(0)
		try:
			image_used = Image.open(temp_file.name)
		except IOError, error:
			logging.info(error)
			logging.info('+'*30 + '\n')
			logging.info(self.request.headers)
			temp_file.close()
			#self.write("Error illegal image")
			return
		image_format = send_file['filename'].split('.').pop().lower()
		tempname = send_file['filename'].split()[0]
		image_used.save(upload__path + tempname)
		temp_file.close()
		#self.write("Upload Successful")
		return


class PicUploadHandler(UploadFileHandler):
	def get(self):
		pass
	
	def post(self):
		#if get an argument as photograph
		album = self.get_argument("Calbum",None)
		Photonm = self.get_argument("CPhotonm",random.randint(1,1000000000))
	
	def createPhotograph(self, name):
		'''define("picrootpath",default=".../",help="store picture")'''
		options.picrootpath + name
	
	def delete(self):
		pass

class VidUploadHandler(UploadFileHandler):
	def get(self):
		pass
	
	def post(self):
		pass

	def delete(self):
		pass

		

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
				(r"/",MainHandler),
				(r"/register",RegisterHandler),
				(r"/login",AuthLoginHandler),
				(r"/logout",AuthLogoutHandler),
				(r"/picup",PicUploadHandler),
				]
		settings = dict(
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			gzip=True,
			debug=True,
			cookie_secret="bZJc2sWbQLKos6GkHn/VB9oX6GkHn/VB9oXwQt"
		)
		tornado.web.Application.__init__(self,handlers,**settings)
		self.db = torndb.Connection(
				host=options.mysql_host, database=options.mysql_database,
				user=options.mysql_user, password=options.mysql_password
		)

def searchDir(path, filename):
	for file_tup in walk(path):
		for file_ in file_tup[2]:
			if file_ == filename:
				return True
			else:
				return False

if __name__ == '__main__':
	"""
	Command line formats are what you would expect (``--myoption=myvalue``).
Config files are just Python files. Global names become options, e.g.::
	
	config-file format: 
	config.py
		global_name = "value"
		name = "myname"
	"""
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()