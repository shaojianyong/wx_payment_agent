#!usr/bin/env python
# -*- coding: utf8 -*-
#
# Created on 2016-04-12
# author: shaojianyong
#
################################################################################

import logging
import json
import urllib.request

# 测试统一下单接口
def test_unified_order(params):
    post_data = json.dumps(params).encode('utf8')
    req = urllib.request.Request("http://localhost:5000/wx-pay/unified-order", post_data)
    rsp = urllib.request.urlopen(req)
    
    http_status = rsp.status
    http_reason = rsp.reason
    logging.info('http_status=%d, http_reason=%s' % (http_status, http_reason))
    if http_status == 200:
        xml_rsp = rsp.read().decode('utf8')
        logging.info('rsp: ' + xml_rsp)
    rsp.close()

# 单元测试
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='test_unified_order.log',
                        filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    
    params = {
        'out_trade_no': '1000048701201711081035140723',
        'total_fee': 10000,
        'spbill_create_ip': '127.0.0.1',
        'notify_url': 'http://wxremit.tenpay.com/cgi-bin/wxremit_callback.cgi',
        'trade_type': 'JSAPI',
        'openid': 'o6BHkjr-WyC0H7lM7q7LiSKm7JNY',
        }
    test_unified_order(params)
