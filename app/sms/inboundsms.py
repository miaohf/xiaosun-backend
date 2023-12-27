from flask import jsonify, g, request
import re
from app import db
from app.models import Users, Phones, Countries, Smses, Messages

from twilio.twiml.voice_response import VoiceResponse

from datetime import datetime
from app.sms import bp

from wechatpy import WeChatClient



import os
from twilio.rest import Client



@bp.route("/webhooks/send/<from_number>/<recieve_number>/<msg>", methods=['GET', 'POST'])
def send_sms(from_number, recieve_number, msg):
    # Your Account Sid and Auth Token from twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                         body=msg,
                         from_=from_number,
                         to=recieve_number
                     )

    print(message.sid)
    return('send sms OK')



@bp.route("/webhooks/inbound-voice", methods=['GET', 'POST'])
def inbound_voice():
    """Returns TwiML which prompts the caller to record a message"""

    print('voice call incoming ......')
    # Start our TwiML response
    response = VoiceResponse()

    # Use <Say> to give the caller some instructions
    response.say('Hello. Please leave a message after the beep.')

    # Use <Record> to record the caller's message
    # response.record()
    response.record(transcribe=True)

    # End the call with <Hangup>
    response.hangup()

    print(str(response))
    return str(response)



@bp.route('/webhooks/inbound-sms', methods=['GET', 'POST'])
def inbound_sms():
    if request.is_json:
    	data = request.is_json
    else:
        data = dict(request.form) or dict(request.args)

    # print(type(data['ToCountry']), data['ToCountry'])
    # print(data['To'])
    # print(data['FromCountry'])
    # print(data['From'])
    # print(data['SmsSid'])
    # print(data['Body'])

    # print(data['NumSegments'])
    # print(data['MessageSid'])
    # print(data['AccountSid'])


    sms = Smses()
    sms.body = data['Body'][0]
    sms.smsSid = data['SmsSid'][0]
    sms.country_to = data['ToCountry'][0]
    sms.sms_to = data['To'][0]
    sms.country_to = data['From'][0]
    sms.sms_from = data['FromCountry'][0]
    sms.numnegments = data['NumSegments'][0]
    sms.accountsid = data['AccountSid'][0]

    db.session.add(sms)
    db.session.commit()

    country = Countries.query.filter(Countries.iso == data['ToCountry'][0]).first()
    print(country.country_code)  # +1

    message_demo = "您的账号信息：号码：{}，地区：{}，验证码：{}；售后及合作联系微信: fancybear2018 "
    # verification_code = re.findall(r"\d+\.?\d*", data['Body'])
    verification_code = re.findall(r"\d+", data['Body'][0])[0]

    client = WeChatClient('wx5233798c91b12aa8', '3888aa02c423a8a11e5c41a469eb3ce8')

    phone_number = data['To'][0].replace(country.country_code, '')

    # 判断为uu登录验证码
    if len(verification_code) == 6:  
        
        text = message_demo.format(phone_number, country.country_name, verification_code)

        # send message to wechat user
        phone = Phones.query.filter(Phones.number == sms.sms_to).first()
        if phone.message_deadline > datetime.now():
            print(phone.customer.nickname, phone.customer.openid)
            

            new_message = Messages(text = text, msgtype = 1, customer_id = phone.customer.id)
            print('add new_message')
            db.session.add(new_message)
            db.session.commit()

            res = client.message.send_text(phone.customer.openid, text)
    # 不是uu登录验证码
    else:
        text = sms.body
        admin_openid = 'ocCoyt7GNGFJNydoKX3Rvmxi8-yc'
        res = client.message.send_text(admin_openid, text)

    # ['[Netease]Your pin code is 040497. Netease UU Team']
 
    return ('', 204)
