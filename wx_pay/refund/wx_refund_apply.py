#!usr/bin/env python
# -*- coding: utf8 -*-
#
# 跨境汇款--微信退款申请批跑
# 字符集使用UTF8，不要使用其它字符集
# 参见：微信公众号支付接口文档 (V3.3.7)
#
# Created on 2016-04-12
# author: shaojianyong
#
################################################################################

import logging
import os.path
import pathlib
import ssl
import random
import http.client as HTTP
from datetime import datetime
import xml.etree.ElementTree as ET

from wx_pay.common import app_common
from wx_pay.common.app_config import wx_app_info, wx_merchant, wx_refund

# https://www.python.org/dev/peps/pep-0476/
ssl._create_default_https_context = ssl._create_unverified_context

class WxRefundApply(object):
    
    def __init__(self):
        self.req_params = {}
        self.rsp_params = {}
        
    def __del__(self):
        pass
    
    # 退款请求
    def apply_req(self):
        self.req_params.update({
            'appid': wx_app_info.APP_ID,
            'mch_id': wx_merchant.MCH_SPID,
            'nonce_str': '%s%d' % (datetime.now().strftime('%Y%m%d%H%M%S%f'), random.randint(10000000, 99999999)),
            'op_user_id': wx_refund.OPERATOR_UID
            })
        
        self.req_params['sign'] = app_common.wx_mch_sign(self.req_params)
        
        root = ET.Element('xml')
        for key, val in self.req_params.items():
            ET.SubElement(root, key).text = val
        xml_req = ET.tostring(root).decode('utf8')
        
        logging.info('xml_req: ' + xml_req)
        
        res_path = pathlib.Path(os.path.realpath(__file__)).parent.joinpath('res')
        key_path = res_path.joinpath(wx_refund.HTTPS_KEY_FILE)
        cer_path = res_path.joinpath(wx_refund.HTTPS_CER_FILE)
        
        http_hdrs = { 'Content-type': 'text/xml', 'Accept': 'text/xml' }
        conn = HTTP.HTTPSConnection(host='api.mch.weixin.qq.com', port=443,
                key_file=str(key_path), cert_file=str(cer_path))
        conn.request(method='POST', url='/secapi/pay/refund', body=xml_req, headers=http_hdrs)
        res = conn.getresponse()
        
        xml_rsp = ''
        http_status = res.status
        http_reason = res.reason
        logging.info('http_status=%d, http_reason=%s' % (http_status, http_reason))
        if http_status == 200:
            xml_rsp = res.read().decode('utf8')
            logging.info('xml_rsp: ' + xml_rsp)
        conn.close()
        
        if http_status != 200:
            raise AssertionError('Weixin refund request failed: %s' % http_status)
        else:
            logging.info('Weixin refund request success')
        
        root = ET.fromstring(xml_rsp)
        self.rsp_params.clear()
        for node in root:
            self.rsp_params[node.tag] = node.text
    
    # 检查退款响应
    def check_rsp(self):
        if self.reentrant:
            return
        
        assert self.rsp_params['return_code'] == 'SUCCESS', ('Protocol level error： return_code=%s, return_msg=%s'
                    % (self.rsp_params['return_code'], self.rsp_params['return_msg']))
        assert self.rsp_params['result_code'] == 'SUCCESS', ('Service level error： result_code=%s, err_code=%s, err_code_des=%s'
                    % (self.rsp_params['result_code'], self.rsp_params['err_code'], self.rsp_params['err_code_des']))
        
        # check signature
        assert app_common.wx_mch_sign(self.rsp_params) == self.rsp_params['sign'], 'Signature verification failed'
        
        # check parameters
        assert self.req_params['appid'] == self.rsp_params['appid'], 'appid error'
        assert self.req_params['mch_id'] == self.rsp_params['mch_id'], 'mch_id error'
        assert self.req_params['out_trade_no'] == self.rsp_params['out_trade_no'], 'out_trade_no error'
        assert self.req_params['out_refund_no'] == self.rsp_params['out_refund_no'], 'out_refund_no error'
        assert self.req_params['refund_fee'] == self.rsp_params['refund_fee'], 'refund_fee error'
        
        logging.info('Weixin refund request success')
    
    # 申请退款
    def apply_for_refund(self, params):
        self.req_params = {
            'transaction_id': params['transaction_id'],
            'out_trade_no': params['out_trade_no'],
            'out_refund_no': params['out_refund_no'],
            'total_fee': '%s' % params['total_fee'],
            'refund_fee': '%s' % params['refund_fee'],
            }
        
        try:
            self.apply_req()
            self.check_rsp()
            ret_info = self.rsp_params
        except Exception as e:
            ret_info = { 'return_code': 'FAILURE', 'return_msg': str(e) }
            logging.exception('apply_for_refund error')
        finally:
            return ret_info

# 单元测试
if __name__ == '__main__':
    print('Unit Test Begin!')
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='wx_refund_apply.log',
                        filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    
    handler = WxRefundApply()
    handler.apply_for_refund(10000, 10000, '4001892001201605155887849274',
                             '1000048701201605151035140723', '1000048701201605151035140723')

    print('Unit Test End!')
