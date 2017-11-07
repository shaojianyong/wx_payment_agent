#!usr/bin/env python
# -*- coding: utf8 -*-
#
# 微信对账单下载(Python版本)
#
# 参见：微信公众号支付接口文档 (V3.3.7)
# 微信对账单下载接口： https://api.mch.weixin.qq.com/pay/downloadbill
#
# Created on 2016-04-12
# author: shaojianyong
#
################################################################################

import logging
import random
import ssl
import urllib.request
from datetime import datetime
import xml.etree.ElementTree as ET

from wx_pay.common import app_common
from wx_pay.common.app_config import wx_app_info, wx_merchant

# https://www.python.org/dev/peps/pep-0476/
ssl._create_default_https_context = ssl._create_unverified_context

class WxBillDownload(object):
    
    def __init__(self):
        self.bill_date = None
        self.bill_type = None
        self.bill_text = None
        self.bill_path = None
        
    def __del__(self):
        pass
    
    # 拉取对账单数据
    def pull_bill_data(self):
        req_params = {
            'appid': wx_app_info.APP_ID,
            'mch_id': wx_merchant.MCH_SPID,
            'nonce_str': '%s%d' % (datetime.now().strftime('%Y%m%d%H%M%S%f'), random.randint(10000000, 99999999)),
            'bill_date' : self.bill_date,
            'bill_type' : self.bill_type,
            }
            
        req_params['sign'] = app_common.wx_mch_sign(req_params)
        
        root = ET.Element('xml')
        for key, val in req_params.items():
            ET.SubElement(root, key).text = val
        xml_req = ET.tostring(root).decode('utf8')
        
        logging.info('xml_req: %s' % xml_req)
        
        post_data = xml_req.encode('utf8')
        req = urllib.request.Request("https://api.mch.weixin.qq.com/pay/downloadbill", post_data)
        rsp = urllib.request.urlopen(req)
        
        xml_rsp = ''
        http_status = rsp.status
        http_reason = rsp.reason
        logging.info('http_status=%d, http_reason=%s' % (http_status, http_reason))
        if http_status == 200:
            self.bill_text = rsp.read().decode('utf8')
            logging.info('xml_rsp: ' + xml_rsp)
        rsp.close()
        
        if http_status != 200:
            raise AssertionError('Weixin statement download failed: %s' % http_status)
        else:
            logging.info('Weixin statement download success')
            logging.debug('xml_rsp:\n%s' % self.bill_text)
            
        # parse result
        if 'return_code' in self.bill_text:
            root = ET.fromstring(self.bill_text)
            rsp_params = {}
            for node in root:
                rsp_params[node.tag] = node.text
            raise AssertionError('Download bill file failed, %s:%s' % (
                    rsp_params['return_code'], rsp_params.get('return_msg')))
    
    # 保存为本地文件
    def save_bill_file(self):
        if self.bill_path:
            with open(self.bill_path, 'w', encoding='utf8') as bill:
                bill.write(self.bill_text)
    
    # 下载对账单
    def download_bill(self, bill_date, bill_type='ALL', bill_path=None):
        self.bill_date = bill_date
        self.bill_type = bill_type
        self.bill_path = bill_path
        
        try:
            self.pull_bill_data()
            self.save_bill_file()
            ret_info = { 'return_code': 'SUCCESS', 'return_msg': 'ok', 'return_data': self.bill_text }
        except Exception as e:
            ret_info = { 'return_code': 'FAILURE', 'return_msg': str(e) }
            logging.exception('download_bill error')
        finally:
            return ret_info
        
# 单元测试
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='wx_bill_download.log',
                        filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    
    try:
        handler = WxBillDownload()
        result = handler.download_bill('20160524')
        logging.info(result)
    except:
        logging.exception('wx_bill_download exception')
