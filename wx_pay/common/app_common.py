#!usr/bin/env python
# -*- coding: utf8 -*-
#
# Created on 2016-04-12
# author: shaojianyong
#
################################################################################

import logging
import hashlib

from wx_pay.common.app_config import wx_merchant

# 微信商户签名算法
def wx_mch_sign(params):
    kvs = [key + '=' + val for key, val in sorted(params.items()) if key != 'sign' and val]
    kvs.append('key=' + wx_merchant.SIGN_KEY)
    src = '&'.join(kvs)
    logging.debug('sign src: ' + src)
    md5 = hashlib.md5()
    md5.update(src.encode('utf8'))
    dst = md5.hexdigest().upper()
    logging.debug('sign dst: ' + dst)
    return dst

# 单元测试
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='app_common.log',
                        filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    
    try:
        params = {
        'transaction_id': '4001892001201605155887849274',
        'out_trade_no': '1000048701201605151035140723',
        'out_refund_no': '1000048701201605151035140723',
        'total_fee': '10000',
        'refund_fee': '10000',
        }
        
        result = wx_mch_sign(params)
        logging.info(result)
    except:
        logging.exception('app_common exception')
