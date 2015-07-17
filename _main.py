#!/usr/bin/python
# -*- coding: utf-8 -*-
#test ospath to import sometemplate
import os.path
#

from tornado.options import define, options
import textwrap
import torndb
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

#    {% for good in goods %}
#         {% for num in good_num %}
#            <td>{{good[num]}}</td>
#          {% end %}
#      {% end %}
#define parameter
define("port", default=8111, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="2015pro", help="database name")
define("mysql_user", default="root", help="database user")
define("mysql_password", default="ljn7168396123", help="database password")

ax=[['a','1','2'],['b','2','3'],['c','3','4']]

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
      #greeting = self.get_argument('greeting', 'Hello')
      #self.write(greeting + ', friendly user!')
      
      #test index.html
      self.render('index.html')

class AllMsgHandler(tornado.web.RequestHandler):

    def get(self):
        #main

        self.render("index.html", items=ax)

    def post(self):
        pass

    def head(self):
        pass

class UserAuth(tornado.web.RequestHandler):
    def post(self):
        pass

class UserRegi(tornado.web.RequestHandler):
    def get(self):
        self.render("regi.html")
    def post(self):
        #add regi.html handle POST
        _user = self.get_argument('user',None)
        _passwd = self.get_argument('passwd',None)
        _passwd_again = self.get_argument('passwd_again',None)
        #check mysql exists user?
        if _user is not None and _passwd is not None and _passwd_again is not None:
            _query_string_user = "SELECT * FROM user WHERE user=%s" % _user
            result_register = self.db.get(_query_string_user)
            if result_register is None:
                #register
            else:
                self.write("you can't register")


#class SingleGoodMsgHandler(tornado.web.RequestHandler):
#    def get(self):
#      pass
if __name__ == "__main__":
    tornado.options.parse_command_line()
    db = torndb.Connection(
    host=options.mysql_host, database=options.mysql_database,
    user=options.mysql_user, password=options.mysql_password
    )

    app = tornado.web.Application(handlers=[(r"/", IndexHandler),
                                            (r"/fridge/",AllMsgHandler),
                                            (r"/user/",UserAuth)]
                                            template_path=os.path.join(os.path.dirname(__file__), "templates"),
                                            static_path=os.path.join(os.path.dirname(__file__), "static"),
                                            debug=True
                                            )#,(r"/fridge/SngMsg")])
    #db = torndb.Connection(
    #		host=options.mysql_host, database=options.mysql_database,
    #		user=options.mysql_user, password=options.mysql_password
    #)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
