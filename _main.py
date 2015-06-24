#!/usr/bin/python
# -*- coding: utf-8 -*-
#test ospath to import sometemplate
import os.path
#
import textwrap

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
from tornado.options import define, options
define("port", default=8111, help="run on the given port", type=int)
ax=['a','b','c']

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
      #greeting = self.get_argument('greeting', 'Hello')
      #self.write(greeting + ', friendly user!')
      
      #test index.html
      self.render('index.html')

class AllMsgHandler(tornado.web.RequestHandler):

    def get(self):
        #main

        self.render("index.html", items=ax, good_num=[0,1,2])

    def post(self):
        pass

    def head(self):
        pass

class UserAuth(tornado.web.RequestHandler):
    def post(self):
        pass

#class SingleGoodMsgHandler(tornado.web.RequestHandler):
#    def get(self):
#      pass
if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler),
                                            (r"/fridge/",AllMsgHandler)],
                                            template_path=os.path.join(os.path.dirname(__file__), "templates"),
                                            static_path=os.path.join(os.path.dirname(__file__), "static"),
                                            debug=True
                                            )#,(r"/fridge/SngMsg")])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
