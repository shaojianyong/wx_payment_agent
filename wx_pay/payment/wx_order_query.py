#!usr/bin/env python
# -*- coding: utf8 -*-
#
# 微信订单查询(Python版本)
#
# 参见：微信公众号支付接口文档 (V3.3.7)
# 微信订单查询接口：https://api.mch.weixin.qq.com/pay/orderquery
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

class WxOrderQuery(object):
    
    def __init__(self):
        self.wxpay_id = None
        self.order_id = None
        self.req_params = {}
        self.rsp_params = {}
        self.payment_rec = {}
        
    def __del__(self):
        pass
    
    # 向微信后台发送查询请求
    def query_req(self):
        self.req_params = {
            'appid': wx_app_info.APP_ID,
            'mch_id': wx_merchant.MCH_SPID,
            'nonce_str': '%s%d' % (datetime.now().strftime('%Y%m%d%H%M%S%f'), random.randint(10000000, 99999999)),
            'out_trade_no': self.order_id
            }
        
        if self.wxpay_id:
            self.req_params['transaction_id'] = self.wxpay_id
            
        self.req_params['sign'] = app_common.wx_mch_sign(self.req_params)
        
        root = ET.Element('xml')
        for key, val in self.req_params.items():
            ET.SubElement(root, key).text = val
        xml_req = ET.tostring(root).decode('utf8')
        
        logging.info('xml_req: %s' % xml_req)
        
        post_data = xml_req.encode('utf8')
        req = urllib.request.Request("https://api.mch.weixin.qq.com/pay/orderquery", post_data)
        rsp = urllib.request.urlopen(req)
        
        xml_rsp = ''
        http_status = rsp.status
        http_reason = rsp.reason
        logging.info('http_status=%d, http_reason=%s' % (http_status, http_reason))
        if http_status == 200:
            xml_rsp = rsp.read().decode('utf8')
            logging.info('xml_rsp: ' + xml_rsp)
        rsp.close()
        
        if http_status != 200:
            raise AssertionError('Weixin order query failed: %s' % http_status)
        else:
            logging.info('Weixin order query success')
            
        root = ET.fromstring(xml_rsp)
        self.rsp_params.clear()
        for node in root:
            self.rsp_params[node.tag] = node.text
    
    # 解析微信后台返回的查询结果
    def check_rsp(self):
        assert self.rsp_params['return_code'] == 'SUCCESS', ('Protocol level error： return_code=%s, return_msg=%s'
                    % (self.rsp_params['return_code'], self.rsp_params['return_msg']))
        assert self.rsp_params['result_code'] == 'SUCCESS', ('Service level error： result_code=%s, err_code=%s, err_code_des=%s'
                    % (self.rsp_params['result_code'], self.rsp_params['err_code'], self.rsp_params['err_code_des']))
        
        # check signature
        assert app_common.wx_mch_sign(self.rsp_params) == self.rsp_params['sign'], 'Signature verification failed'
        
        # check parameters
        assert self.req_params['appid'] == self.rsp_params['appid'], 'appid error'
        assert self.req_params['mch_id'] == self.rsp_params['mch_id'], 'mch_id error'
        
        assert (self.rsp_params.get('out_trade_no') == None or
                self.req_params['out_trade_no'] == self.rsp_params['out_trade_no']), 'out_trade_no error'
        
        self.payment_rec['trade_state'] = self.rsp_params['trade_state']
        self.payment_rec['total_fee'] = self.rsp_params['total_fee']
    
    # 查询微信订单
    def query_order_info(self, order_id, wxpay_id=None):
        self.payment_rec = {}
        
        self.wxpay_id = wxpay_id
        self.order_id = order_id
        
        try:
            self.query_req()
            self.check_rsp()
            ret_info = { 'return_code': 'SUCCESS', 'return_msg': 'ok', 'return_data': self.payment_rec }
        except Exception as e:
            ret_info = { 'return_code': 'FAILURE', 'return_msg': str(e) }
            logging.exception('query_order_info error')
        finally:
            return ret_info
        
# 单元测试
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='wx_order_query.log',
                        filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    
    try:
        handler = WxOrderQuery()
        result = handler.query_order_info('1000048701201605151035140723', '4001892001201605155887849274')
        logging.info(result)
    except:
        logging.exception('wx_order_query exception')
