
import os
from twilio.rest import Client


from app import create_app, db
app=create_app()
app.app_context().push()

from app.models import Phones

# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

incoming_phone_numbers = client.incoming_phone_numbers.list(limit=20)

for record in incoming_phone_numbers:

	# incoming_phone_number = client.incoming_phone_numbers(record.sid)
	client\
        .incoming_phone_numbers(record.sid)\
        .update(
             sms_url = 'http://mp.tuozhanad.com/sms/webhooks/inbound-sms'
         )

	phone = Phones.query.filter(Phones.number == record.phone_number).first()
	if not phone:
		phone = Phones()
		phone.channel_id = 1
		phone.country_id = 1
		phone.number_sid = record.sid
		phone.number = record.phone_number
		phone.voice = record.capabilities['voice']
		phone.sms = record.capabilities['sms']
		phone.mms = record.capabilities['mms']
		# phone.fax = record.capabilities['fax']
		phone.address_requirements = record.address_requirements
		phone.account_sid = record.account_sid
		phone.note = record.status

		db.session.add(phone)
	else:
		phone.channel_id = 1
		phone.country_id = 1
		phone.number_sid = record.sid
		phone.number = record.phone_number
		phone.voice = record.capabilities['voice']
		phone.sms = record.capabilities['sms']
		phone.mms = record.capabilities['mms']
		# phone.fax = record.capabilities['fax']
		phone.address_requirements = record.address_requirements
		phone.account_sid = record.account_sid
		phone.note = record.status


	db.session.commit()