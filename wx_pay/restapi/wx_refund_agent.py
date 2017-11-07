#!usr/bin/env python
# -*- coding: utf8 -*-
#
# 微信退款代理
#
# Created on 2016-04-12
# author: shaojianyong
#
################################################################################

import logging
from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from wx_pay.refund.wx_refund_query import WxRefundQuery
from wx_pay.refund.wx_refund_apply import WxRefundApply

app = Flask(__name__)
api = Api(app)

# 申请退款资源
class WxRefundApplyRes(Resource):
    # 发起退款请求
    def post(self):
        params = request.get_json(force=True)
        
        handler = WxRefundApply()
        return jsonify(handler.apply_for_refund(params))
        return params['transaction_id']

# 退款查询资源
class WxRefundQueryRes(Resource):
    # 查询退款记录
    def get(self, order_id):
        handler = WxRefundQuery()
        return jsonify(handler.query_refund_records(order_id))

# RESTful API
api.add_resource(WxRefundApplyRes, '/wx-pay/refund-apply')
api.add_resource(WxRefundQueryRes, '/wx-pay/refund-query/<order_id>')

# 单元测试
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='wx_refund_agent.log',
                        filemode='a')
    logging.getLogger().addHandler(logging.StreamHandler())
    
    app.run(debug=True)
