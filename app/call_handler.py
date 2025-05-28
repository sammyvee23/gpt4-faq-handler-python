from twilio.rest import Client
import os

account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_number = os.environ.get("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

def make_outbound_call(to_number: str, script_url: str):
    """
    Initiates a call to `to_number` using Twilio and plays the TwiML script at `script_url`.
    """
    call = client.calls.create(
        to=to_number,
        from_=twilio_number,
        url=script_url  # this should return valid TwiML XML
    )
    return call.sid
