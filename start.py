#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import socket
from device import Launcher
from tornado import template, gen, iostream
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        loader = template.Loader("./")
        self.write(loader.load("templates/template.html").generate())
        self.finish()


class CtrlHandler(tornado.web.RequestHandler):
    def get(self):
        action = self.get_argument("action", default="stop")
        device.act(action)
        self.write("OK")


class VideoHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(VideoHandler, self).__init__(application, request, **kwargs)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.streaming = True
        self.stream = iostream.IOStream(s)

    @tornado.web.asynchronous
    # @tornado.gen.coroutine
    def get(self):
        self.set_header("Content-Type", "multipart/x-mixed-replace; boundary=--frame")
        self.stream.connect(("localhost", 9999), self.on_stream)

    def on_stream(self, data=None):
        self.stream.read_bytes(2048, self.on_stream)
        if data:
            self.write(data)
            self.flush()

    def on_connection_close(self):
        self.streaming = False



device = Launcher()
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/ctrl", CtrlHandler),
    (r"/video", VideoHandler),
])

if __name__ == "__main__":
    #gst-launch-0.10 v4l2src ! video/x-raw-rgb, framerate=15/1, width=640, height=480 !  jpegenc ! multipartmux boundary=frame ! tcpserversink port=9999
    print("started http://localhost:8888/")
    device.open()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()