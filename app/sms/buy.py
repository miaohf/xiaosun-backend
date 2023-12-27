import os
from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)



from app import create_app, db
app=create_app()
app.app_context().push()

from app.models import Phones


limit = 1
local_numbers = client.available_phone_numbers('US').local.list(
                                            #area_code=510,
                                            sms_enabled=True,
                                            #voice_enabled=False,
                                            #mms_enabled=False,
                                            exclude_all_address_required=True,
                                            limit=limit
                                            )
for record in local_numbers:
    # 购买
    number_new = client.incoming_phone_numbers.create(phone_number=record.phone_number)

    # 配置回调URL
    incoming_phone_number = client\
        .incoming_phone_numbers(number_new.sid)\
        .update(
             sms_url = 'http://mp.tuozhanad.com/sms/webhooks/inbound-sms'
         )

    # 号码入库
    phone = Phones()
    phone.channel_id = 1
    phone.country_id = 1
    phone.number_sid = number_new.sid
    phone.number = number_new.phone_number
    phone.voice = number_new.capabilities['voice']
    phone.sms = number_new.capabilities['sms']
    phone.mms = number_new.capabilities['mms']
    # phone.fax = number_new.capabilities['fax']
    phone.address_requirements = number_new.address_requirements
    phone.account_sid = number_new.account_sid
    phone.note = number_new.status

    db.session.add(phone)
    db.session.commit()