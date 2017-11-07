#!usr/bin/env python
# -*- coding: utf8 -*-
#
# 微信退款查询(Python版本)
#
# 查询一笔微信支付交易的退款记录，通常一笔交易只有一笔退款；但也有一些类型的交易支持多笔退款，
# 每笔退一部分，但总金额不大于原单支付金额。
# 提交退款申请后，通过调用该接口查询退款状态。退款有一定延时，用零钱支付的退款20分钟内到账，
# 银行卡支付的退款3个工作日后重新查询退款状态。
#
# 参见：微信公众号支付接口文档 (V3.3.7)
# 微信订单查询接口：https://api.mch.weixin.qq.com/pay/refundquery
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

class WxRefundQuery(object):
    
    def __init__(self):
        self.wxpay_id = None
        self.order_id = None
        self.req_params = {}
        self.rsp_params = {}
        self.refund_rec = []
        
    def __del__(self):
        pass
    
    # 向微信后台发送查询请求
    def query_req(self):
        self.req_params = {
            'appid': wx_app_info.APP_ID,
            'mch_id': wx_merchant.MCH_SPID,
            'nonce_str': '%s%d' % (datetime.now().strftime('%Y%m%d%H%M%S%f'), random.randint(10000000, 99999999)),
            'out_trade_no': self.order_id,
            'out_refund_no': self.order_id
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
        req = urllib.request.Request("https://api.mch.weixin.qq.com/pay/refundquery", post_data)
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
            raise AssertionError('Weixin refund query failed: %s' % http_status)
        else:
            logging.info('Weixin refund query success')
            
        root = ET.fromstring(xml_rsp)
        self.rsp_params.clear()
        for node in root:
            self.rsp_params[node.tag] = node.text
    
    # 解析微信后台返回的查询结果
    def check_rsp(self):
        assert self.rsp_params['return_code'] == 'SUCCESS', ('Protocol level error： return_code=%s, return_msg=%s'
                    % (self.rsp_params['return_code'], self.rsp_params['return_msg']))
        
        if self.rsp_params['result_code'] != 'SUCCESS':
            if self.rsp_params['err_code'] == 'REFUNDNOTEXIST':
                info = 'No refund record: ' + self.rsp_params['err_code_des']
                logging.info(info)
                return
            else:
                raise AssertionError('Service level error： result_code=%s, err_code=%s, err_code_des=%s'
                                     % (self.rsp_params['result_code'],
                                        self.rsp_params['err_code'],
                                        self.rsp_params['err_code_des']))
        
        # check signature
        assert app_common.wx_mch_sign(self.rsp_params) == self.rsp_params['sign'], 'Signature verification failed'
        
        # check parameters
        assert self.req_params['appid'] == self.rsp_params['appid'], 'appid error'
        assert self.req_params['mch_id'] == self.rsp_params['mch_id'], 'mch_id error'
        
        assert (not self.wxpay_id or self.wxpay_id == self.rsp_params['transaction_id']), 'transaction_id error'
        assert self.req_params['out_trade_no'] == self.rsp_params['out_trade_no'], 'out_trade_no error'
        refund_count = int(self.rsp_params['refund_count'])
        
        for i in range(refund_count):
            refund_rec = {
                'refund_status': self.rsp_params['refund_status_%s' % i],
                'out_refund_no': self.rsp_params['out_refund_no_%s' % i],
                'refund_id': self.rsp_params['refund_id_%s' % i],
                'refund_fee': self.rsp_params['refund_fee_%s' % i]
            }
            self.refund_rec.append(refund_rec)
    
    # 查询订单的所有退款记录
    def query_refund_records(self, order_id, wxpay_id=None):
        self.refund_rec = []
        
        self.wxpay_id = wxpay_id
        self.order_id = order_id
        
        try:
            self.query_req()
            self.check_rsp()
            ret_info = { 'return_code': 'SUCCESS', 'return_msg': 'ok', 'return_data': self.refund_rec }
        except Exception as e:
            ret_info = { 'return_code': 'FAILURE', 'return_msg': str(e) }
            logging.exception('query_refund_records error')
        finally:
            return ret_info
        
# 单元测试
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='wx_refund_query.log',
                        filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    
    try:
        handler = WxRefundQuery()
        result = handler.query_refund_records('4001892001201605155887849274', '1000048701201605151035140723')
        logging.info(result)
    except:
        logging.exception('wx_refund_query exception')
