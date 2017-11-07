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

# 测试退款申请接口
def test_refund_apply(params):
    post_data = json.dumps(params).encode('utf8')
    req = urllib.request.Request("http://localhost:5000/wx-pay/refund-apply", post_data)
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
                        filename='test_refund_apply.log',
                        filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    
    params = {
        'transaction_id': '4001892001201605155887849274',
        'out_trade_no': '1000048701201605151035140723',
        'out_refund_no': '1000048701201605151035140723',
        'total_fee': 10000,
        'refund_fee': 10000,
        }
    test_refund_apply(params)
