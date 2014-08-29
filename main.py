#!/usr/bin/python
import time
from tornado import template
import tornado.ioloop
import tornado.web
import usb.core


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        loader = template.Loader("./")
        self.write(loader.load("template.html").generate())


class Launcher():
    def __init__(self):
        self.dev = None

    def open(self):
        self.dev = usb.core.find(idVendor=0x2123, idProduct=0x1010)
        if self.dev is None:
            raise ValueError('Launcher not found.')
        if self.dev.is_kernel_driver_active(0) is True:
            self.dev.detach_kernel_driver(0)
        self.dev.set_configuration()

    def up(self):
        self.dev.ctrl_transfer(0x21, 0x09, 0, 0, [0x02, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def down(self):
        self.dev.ctrl_transfer(0x21, 0x09, 0, 0, [0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def left(self):
        self.dev.ctrl_transfer(0x21, 0x09, 0, 0, [0x02, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def right(self):
        self.dev.ctrl_transfer(0x21, 0x09, 0, 0, [0x02, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def stop(self):
        self.dev.ctrl_transfer(0x21, 0x09, 0, 0, [0x02, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def fire(self):
        self.dev.ctrl_transfer(0x21, 0x09, 0, 0, [0x02, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def act(self, action):
        if action == "stop":
            self.stop()
            return
        if action == "up":
            self.up()
            return
        if action == "down":
            self.down()
            return
        if action == "left":
            self.left()
            return
        if action == "right":
            self.right()
            return
        if action == "fire":
            self.fire()
            return


class CtrlHandler(tornado.web.RequestHandler):
    def get(self):
        action = self.get_argument("action", default="stop")
        device.act(action)
        self.write("OK")


device = Launcher()
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/ctrl", CtrlHandler),
])

if __name__ == "__main__":
    device.open()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()