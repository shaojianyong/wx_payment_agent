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
