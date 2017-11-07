#!usr/bin/env python
# -*- coding: utf8 -*-
#
# Created on 2016-04-12
# author: shaojianyong
#
################################################################################

# 微信应用信息
class wx_app_info(object):
    APP_ID = ''  # 跨境汇款公众号AppID
    APP_SECRET = ''  # 微信公众号应用密钥

# 微信跨境汇款商户
class wx_merchant(object):
    MCH_SPID = ''  # 跨境汇款财付通商户号
    MCH_B_ID = ''  # 用户ID，商户C账户内部ID
    MCH_C_ID = ''  # 商户B帐户内部ID
    SIGN_KEY = ''  # 微信支付商户签名KEY

# 微信退款申请接口
class wx_refund(object):
    WX_MCH_DOMAIN  = 'api.mch.weixin.qq.com'
    WX_REFUND_URL  = '/secapi/pay/refund'
    HTTPS_KEY_FILE = '1000000000key.pem'  # SSL/TLS双向认证私钥和证书
    HTTPS_CER_FILE = '1000000000cer.pem'
    OPERATOR_UID   = wx_merchant.MCH_SPID # 跨境汇款后台操作员号码
