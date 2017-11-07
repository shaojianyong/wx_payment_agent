#!usr/bin/env python
# -*- coding: utf8 -*-
#
# Created on 2016-04-12
# author: shaojianyong
#
################################################################################

import logging
import urllib.request

# 测试退款查询接口
def test_order_query(order_id):
    rsp = urllib.request.urlopen('http://localhost:5000/wx-pay/order-query/1000048701201605151035140723')
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
                        filename='test_order_query.log',
                        filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    
    test_order_query('1000048701201605151035140723')
