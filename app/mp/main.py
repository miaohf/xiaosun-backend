from flask import jsonify, g, request
from app import db
from app.models import Users, Messages
from app.mp import bp
from datetime import datetime, timedelta

from wechatpy import parse_message, create_reply, WeChatClient

from wechatpy.events import ScanCodeWaitMsgEvent

from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)

import os, time

from multiprocessing import Process

from app.mp.click import MenuClick

client = WeChatClient('wx5233798c91b12aa8', '3888aa02c423a8a11e5c41a469eb3ce8')



@bp.route('/wechat', methods=['GET', 'POST'])
def wechat():
    """
    用来验证微信公众号后台链接
    :return:
    """

    # print('check_token')

    TOKEN = 'ColoreDeerWeChatMp'
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    encrypt_type = request.args.get("encrypt_type", "raw")
    msg_signature = request.args.get("msg_signature", "")
    try:
        check_signature(TOKEN, signature, timestamp, nonce)
    except InvalidSignatureException:
        abort(403)
    if request.method == "GET":
        echo_str = request.args.get("echostr", "")
        return echo_str

    # POST request
    if encrypt_type == "raw":
        # plaintext mode
        msg = parse_message(request.data)
        print('msg.type:', msg.type)

        dt_now = datetime.now()
        openid = msg.source
        wechat_user = client.user.get(openid)
        user = Users.query.filter(Users.openid == openid).first()
        if not user:
            user = Users(
                openid = wechat_user['openid'],
                avatarurl = wechat_user['headimgurl'],
                nickname = wechat_user['nickname'],
                # sex = wechat_user['sex'],
                # city = wechat_user['city'],
                # province = wechat_user['province']

                )
            db.session.add(user)
            db.session.commit()


        if msg.type == "text":

            code = msg.content

            # 备份推送的消息
            new_message = Messages(text = msg.content, user_id = user.id, msgtype = 0)
            db.session.add(new_message)

            user.last_reply = datetime.now()

            db.session.commit()


            
            wx_message = "好的，选房现场信息通知已激活，感谢您的参与。"

        elif msg.type == "event":

            if msg.event == 'subscribe':
                wx_message = "欢迎订阅九色鹿网络~！ 回复任意消息激活【魏塘街道庄港社区、三里桥村等城中村改造】选房活动现场情况消息推送功能。 "

            elif msg.event == 'unsubscribe':
                wx_message = "Sorry ...... "

            elif msg.event == 'click':
                # MenuClick是自定义类，处理菜单点击事件
                click = MenuClick(msg)
                return click.menu_click()
            # 其他类型的事件消息不处理
            else:
                reply = TextReply(message=msg)
                reply.content = 'event未知'
                xml = reply.render()
                return xml



        else:
            wx_message = "Sorry ...... "

        # 查询库存并购买
        # check_and_buy(1)  #直接调用，会阻塞，导致信息回复有延迟
        # 多进程方式启动，防止阻塞
        # p = Process(target=check_and_buy, args=('1',))
        # p.start()

        # 响应消息
        reply = create_reply(wx_message, msg)
        return reply.render()

    else:
        # encryption mode
        from wechatpy.crypto import WeChatCrypto

        crypto = WeChatCrypto(TOKEN, AES_KEY, APPID)
        
        try:
            msg = crypto.decrypt_message(request.data, msg_signature, timestamp, nonce)
        
        except (InvalidSignatureException, InvalidAppIdException):
            abort(403)
        
        else:
            msg = parse_message(msg)
            
            if msg.type == "text":
                reply = create_reply(msg.content, msg)
            
            else:
                reply = create_reply("Sorry, can not handle this for now", msg)
            
            return crypto.encrypt_message(reply.render(), nonce, timestamp)