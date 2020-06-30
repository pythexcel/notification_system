from app import create_app as app
from app.util import allowed_file,FetchRecipient
from app.modules.phone_util import create_sms


#Test case for create mobile message
def test_create_sms():
    phone = "8445679788"
    mobile_message_str = "testing"
    assert phone and mobile_message_str is not None 
    phone_status,phone_issue,phone_issue_message = create_sms(phone=phone, mobile_message_str=mobile_message_str)
    assert phone_status != False and phone_issue != True



#Test for check file type is valid or not
def test_filename():
    filename = "testing.pdf"
    assert type(filename) == str
    file = allowed_file(filename=filename)
    assert file != None


#test for fetch recipients from user details
def test_FetchRecipient():
    slack_user_detail = {"email_group":["testing1@gmail.com","testing2@gmail.com"]}
    message_detail = {"email_group":["testing3@gmail.com","testing4@gmail.com"]}
    assert 'email_group' in message_detail
    status = FetchRecipient(slack_user_detail=slack_user_detail,message_detail=message_detail)
    assert type(status) == list