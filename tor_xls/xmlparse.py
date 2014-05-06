import xml.parsers.expat


def parse_xml(stream):
    tag_name = []
    dic = {}
    dest_count = [0]
    # 3 handler functions
    def start_element(name, attrs):
        tag_name.append(name.rsplit(':')[-1].encode())
        # print 'Start element:', tag_name, attrs
    def end_element(name):
        tag_name.pop()
        # print 'End element:', name
    def char_data(data):
        if tag_name[-1] == 'Number':
            if 'SenderAddress' in tag_name:
                dic['SrcAddr'] = data.encode()
            elif 'Recipients' in tag_name:
                count = dest_count[-1]
                dest_count.append(count + 1)
                dic['DestAddr%d' % count ] = data.encode()
                # print "dest count", dest_count
        else:
            dic[tag_name[-1]] = data.encode()
        # print 'Character data:', tag_name, repr(data)

    p = xml.parsers.expat.ParserCreate()

    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data

    p.Parse(stream, 1)
    dic['DestCount'] = dest_count[-1]
    return dic
if __name__ == '__main__':
    submit_str = """<?xml version="1.0" encoding="utf-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Header><mm7:TransactionID xmlns:mm7="http://www.3gpp.org/ftp/Specs/archive/23_series/23.140/schema/REL-6-MM7-1-0" soapenv:mustUnderstand="1">3140318145742777242914</mm7:TransactionID></soapenv:Header><soapenv:Body><SubmitReq xmlns="http://www.3gpp.org/ftp/Specs/archive/23_series/23.140/schema/REL-6-MM7-1-0"><MM7Version>6.3.0</MM7Version><SenderIdentification><VASPID>1065</VASPID><VASID>123456</VASID><SenderAddress><Number>13800230500</Number></SenderAddress></SenderIdentification><Recipients><To><Number>13527537125</Number></To></Recipients><ServiceCode>00001020101130</ServiceCode><ExpiryDate>1970-01-01T06:59:59+08:00</ExpiryDate><DeliveryReport>true</DeliveryReport><Priority>Normal</Priority><Subject>mms subject </Subject></SubmitReq></soapenv:Body></soapenv:Envelope>
"""
    msg = parse_xml(submit_str)
    print msg
