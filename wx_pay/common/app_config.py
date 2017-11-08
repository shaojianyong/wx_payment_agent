#!usr/bin/env python
# -*- coding: utf8 -*-
#
# Created on 2016-04-12
# author: shaojianyong
#
################################################################################

# 微信应用信息
class wx_app_info(object):
    APP_ID = 'wxfd0b77802960be00'  # 公众号AppID
    APP_NAME = 'GlobalTransfer'  # 应用名称
    APP_SECRET = '6c3bb09ed6b2fb52092e3f7f720fc1d0'  # 微信公众号应用密钥

# 微信商户信息
class wx_merchant(object):
    MCH_SPID = '1000048701'  # 财付通商户号
    SIGN_KEY = 'b48f34296399f9f4b1e5c7a47d7424c5'  # 微信支付商户签名KEY

# 微信退款申请接口
class wx_refund(object):
    HTTPS_KEY_FILE = '1000048701key.pem'  # SSL/TLS双向认证私钥和证书
    HTTPS_CER_FILE = '1000048701cer.pem'
    OPERATOR_UID = wx_merchant.MCH_SPID # 后台操作员号码
