#! -*- encoding:utf-8 -*-
import tornado.web
import tornado.ioloop
from tornado import httpclient
from tornado.log import app_log


from views import MainHandler, XlsHandler, WasHandler
from settings import settings
from threading import Thread
from Queue import Queue

def client_handler(q, i):
    client = httpclient.HTTPClient()
    success = 0
    failed = 0
    print("client%d handler started "%(i))
    while True:
        msg = q.get()
        # print("client{} handler get {} size".format(i))
        try:
            resp = client.fetch(settings.get('uma_mms_url', ''), method='POST', user_agent='MMSC Simulator', body=msg, headers={'soapAction': '""', 'x-mmsc-msg-from': 'mm7', 'Mime-Version': '1.0', 'Content-Type': 'text/xml; charset=utf-8', 'Content-Transfer-Encoding':'8bit', 'Connection': 'Keep-alive'})
            if resp.error:
                failed += 1
            else:
                success += 1
                # print("report resp body: %s" % resp.body)
        except:
            print("Error Resp: ")
            failed += 1
        if success % 10 == 0:
            print("client%d fetch finished! success:%d failed:%d"%(i, success, failed))
    print("client%d handler stopped %d %d"%(i, success, failed))

if __name__ == "__main__":

    application = tornado.web.Application([
        ( r'/xls/', XlsHandler),
    ], **settings)

    application.listen(settings.get('port', 7000), address="0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()
    q.join()
