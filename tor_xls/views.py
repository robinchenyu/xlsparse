#! -*- encoding: utf-8 -*-
import uuid
import os
from Queue import Queue

import tornado.web
from tornado import httpclient

from settings import settings
from xmlparse import parse_xml
from readxls import resolv

from tornado.log import app_log


def reportMsg(msg):
    dic = msg
    dic["RStatusCode"] = 129
    dic["RStatusText"] = "Retrieved"
    dic["RTransactionID"] = uuid.uuid4().get_hex()
    msgTmpl = '<?xml version="1.0" encoding="GB2312"?><env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"><env:Header><mm7:TransactionID xmlns:mm7="http://www.3gpp.org/ftp/Specs/archive/23_series/23.140/schema/REL-6-MM7-1-0" env:mustUnderstand="1">{RTransactionID}</mm7:TransactionID></env:Header><env:Body><DeliveryReportReq xmlns="http://www.3gpp.org/ftp/Specs/archive/23_series/23.140/schema/REL-6-MM7-1-0"><MM7Version>{MM7Version}</MM7Version><MMSRelayServerID>902500</MMSRelayServerID><MessageID>{MessageID}</MessageID><Recipient><Number>{DestAddr0}</Number></Recipient><Sender>{SrcAddr}</Sender><TimeStamp>2014-3-24T10:34:50+08:00</TimeStamp><MMStatus>{RStatusText}</MMStatus><MMSStatusErrorCode>{RStatusCode}</MMSStatusErrorCode><StatusText>OK</StatusText></DeliveryReportReq></env:Body></env:Envelope>'.format(**dic)
    # print "report: ", msgTmpl
    return msgTmpl


def getContents(contents):
    data = {}
    ret  = False
    for line in contents.split("\r\n"):
        if len(line) <=5:
            continue
        if 'Content-Type' in line:
            if 'Content-Type:text/xml;' in line:
                data['Content-Type'] = line[len('Content-Type')+1:]
                ret = True
            else:
                break
        elif 'Content-Transfer-Encoding' in line:
            data['Content-Transfer-Encoding'] = line[len('Content-Transfer-Encoding')+1:]
        elif '<?xml' in line:
            data['Contents'] = parse_xml(line)
    return ret, data

def respMsg(msg):
    dic = msg
    dic["StatusCode"] = 1000
    dic["StatusText"] = "Success"
    dic["MessageID"] = uuid.uuid4().get_hex()
    report = reportMsg(dic)
    return dic, report




class MainHandler(tornado.web.RequestHandler):

    def initialize(self, queue):
        # print "get a client", dir(client)
        self.queue = queue
        if not self.queue:
            print "no queue"
            raise

    def get(self):
        self.write("Hello, world")
    def post(self):
        msg = []
        for contents in self.request.body.split("--=MMS_delimiter="):
            ret,data = getContents(contents)
            if ret:
                msg.append(data)
            else:
                msg.append(contents)
        resp, report = respMsg(msg[1].get('Contents'))
        # print "resp: ", resp, len(resp)
        self.set_header('Content-Type', 'text/xml; charset=UTF-8')
        self.render("resp.xml", **resp)

        # print("put report")
        self.queue.put(report)
        # self.__sendReport(report)

    def __sendReport(self,msg):
        def handle_report(response):
            if response.error:
                print "Error report Ack:", response.error

            # print "Report Ack Body", response.body

        if not hasattr(self, "client1") or not self.client1:
            try:
                print "hasattr:", hasattr(self, "client1")
                print "client1:", self.client1
            except:
                pass
            print "get new client"
            self.client1 = httpclient.AsyncHTTPClient()

        self.client1.fetch(settings.get('uma_mms_url'), handle_report, method='POST', user_agent='MMSC Simulator', body=msg, headers={'soapAction': '""', 'x-mmsc-msg-from': 'mm7', 'Mime-Version': '1.0', 'Content-Type': 'text/xml; charset=utf-8', 'Content-Transfer-Encoding':'8bit', 'Connection': 'Keep-alive'})


class XlsHandler(tornado.web.RequestHandler):
    def get_argument(self, name, default=[], strip=True):
        v = super(XlsHandler, self).get_argument(name, default, strip)
        if not v:
            return default
        return v

    def get(self):
        self.render("templates/xls/upload.html")

    def post(self):
        start_time = self.get_argument("start_time", "08:00")
        end_time = self.get_argument("end_time", "19:00")
        start_launch_time = self.get_argument("start_launch_time", "11:45")
        end_launch_time = self.get_argument("end_launch_time", "12:30")
        work_minutes = self.get_argument("work_minutes", "190")
        print "start_time:%s, end_time: %s  %s %s %s" % (start_time, end_time, start_launch_time, end_launch_time, work_minutes)
        try:
            fbody = self.request.files.get('file')[0]
            if fbody and fbody.get('content_type') == 'application/vnd.ms-excel':
                filename = os.path.join(settings.get('static_path'), fbody.get('filename', 'data.xls'))
                print "save file: ", filename
                with open(filename, "w") as fw:
                    fw.write(fbody.get('body'))
                file_name, form, origin_form = resolv(filename, "08:00", "19:00")
            args = locals()
            args.pop('self')
            args['file_url'] = '/static/out.csv'
            self.render("templates/xls/download.html", **args)
                        # form=form, origin_form=origin_form,
                        # start_time = start_time, end_time = end_time, file_url = "/static/out.csv", file_name=file_name)
        except Exception as e:
            print "Error file:", e
            self.write("failed")

class WasHandler(tornado.web.RequestHandler):

    def get(self):
        print "get was"
        self.render("templates/was/params.xml")
    def post(self):
        print "post was"
        self.render("templates/was/params.xml")
