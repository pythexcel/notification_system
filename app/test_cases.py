from app import create_app as app
from app.util import allowed_file,FetchRecipient,serialize_doc,FetchChannels,template_requirement,MakeMessage,campaign_details,convert_dates_to_format
from app.modules.phone_util import create_sms
from bson import ObjectId
import datetime
from app.model.template import attach_letter_head
from app.modules.template_util import construct_message_str,construct_mobile_message_str,construct_message_subject,fetch_recipients_by_mode

system_variables = [{'_id': '5dfc6108c837f7bc90ab3ccd', 'name': '#joining_date', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd5', 'name': '#director_signature', 'value': '<p><strong>Excellence Technologies,</strong></p>\n<p><strong>Manish Prakash</strong></p>\n<p><strong>(Director)</strong></p>', 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd6', 'name': '#venue', 'value': 'C-86 B Excellence Technosoft Pvt. Ltd Noida Sector 8', 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cd9', 'name': '#numberOfDays', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce5', 'name': '#relieving_date', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce9', 'name': '#office_time', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd3', 'name': '#termination_date', 'value': None, 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cd7', 'name': '#company', 'value': 'Excellence Technosoft Pvt. Ltd', 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3ce3', 'name': '#date_of_sending', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cdf', 'name': '#details', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cda', 'name': '#name', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cdd', 'name': '#reason', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce0', 'name': '#job_title', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd0', 'name': '#map_location', 'value': 'https://www.google.co.in/maps/place/Excellence+Technologies/@28.5959817,77.3260043,17z/data=!3m1!4b1!4m5!3m4!1s0x390ce4fc8c75d9e:0x4ea29a8e67042fb9!8m2!3d28.595977!4d77.328193?hl=en', 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cd1', 'name': '#employee_user_name', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce1', 'name': '#login_id', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd8', 'name': '#hr_signature', 'value': '<p>HR <br/> Juhi Singh <br/> Landline No: 0120-4113772 <br/> https://excellencetechnologies.in/<br/>https://www.facebook.com/ExcellenceTechnologies<br/>https://itunes.apple.com/in/app/career-app-by-etech/id1399557922?mt=8<br/>', 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3ce4', 'name': '#resignation_date', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce7', 'name': '#upper_limit_salary', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cce', 'name': '#logo', 'value': "<p><img src='https://res.cloudinary.com/dp0y84e66/image/upload/v1568791251/logo.e5be347d_yf4q90.png' width='170' height='50'/></p>", 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cdc', 'name': '#toDate', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce8', 'name': '#increament_after_month', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cdb', 'name': '#fromDate', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce2', 'name': '#employee_id', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ccc', 'name': '#date', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ccf', 'name': '#salary', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cde', 'name': '#month', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce6', 'name': '#lower_limit_salary', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd2', 'name': '#training_completion_date', 'value': None, 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cd4', 'name': '#designation', 'value': None, 'variable_type': 'user'}]


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



#test for serilizer
def test_serialize_doc():
    doc = {"_id":ObjectId("507f1f77bcf86cd799439011"),"data":"data"}
    assert doc['_id'] is not None
    serialize = serialize_doc(doc) 
    assert type(serialize['_id']) == str



#test case for fetch channels from user details
def test_FetchChannels():
    slack_user_detail = {"slack_channel":['CVHCL21','CHGT21'],"sended_to":"public"}
    message_detail = {"slack_channel":['CVHCL21','CHGT21'],"sended_to":"public"}
    channels = FetchChannels(slack_user_detail=slack_user_detail,message_detail=message_detail)
    assert type(channels) == list
    assert len(channels)>0



#Test case for 
def test_MakeMessage():
    message = "@user:  @data:"
    message_variables = ['user','data']
    slack_user_detail = {'user': '<@UJCNCV1DJ>', 'data': 'Report: \nworked with tms\n', 'slack_channel': [], 'message_type': 'simple_message', 'message_key': 'check-in'}
    system_require = []
    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}
    assert message and slack_user_detail is not None
    assert "user" in slack_user_detail
    message_string = MakeMessage(message_str=message,message_variables=message_variables,slack_user_detail=slack_user_detail,system_require=system_require,system_variable=system_variable)
    assert message_string != None
    assert type(message_string) == str



def test_convert_dates_to_format():
    dates_converter = ["dateofjoining","dob","date","interview_date","training_completion_date","termination_date","next_increment_date","start_increment_date","fromDate","toDate","reporting_date"]
    request = {"message_key": "user_timesheet_entry","message_type": "simple_message","user": {"email": "aishwary@excellencetechnolgies.in","name":"aish"},
        "data": {
            "hours": "9",
            "date": "Friday, June 5th 2020, 2:15:49 pm"
                }
            }
    assert "data" in request
    assert type(dates_converter)==list
    assert len(dates_converter)>=1
    updated_data = convert_dates_to_format(dates_converter=dates_converter,req=request)
    assert updated_data is not None



def test_attach_letter_head():
    header="This is header of template"
    footer="This is footer of template"
    message="This is message of template"
    template = attach_letter_head(header,footer,message)
    assert template
    assert type(template) == str


def test_construct_message_str():
    message_detail = "you have made a entry on timesheet Date : @date: Hours: @hours:"
    request = {'hours': '9', 'date': '05 Jun 2020'}
    assert message_detail is not None
    assert request is not None
    assert type(system_variables)==list
    assert type(message_detail)==str
    message_str,missing_payload=construct_message_str(message_detail=message_detail,request=request,system_variable=system_variables)
    assert len(missing_payload) == 0
    assert message_str is not None



def test_construct_mobile_message_str():
    message_detail = {'_id': ObjectId('5ee0bd14f1e987a7106610c1'), 'message_key': 'user_timesheet_entry', 'channels': 'public', 'email_group': None, 'for_email': False, 'for_phone': False, 'for_slack': False, 'for_zapier': True,"mobile_message":"you have made a entry on timesheet Date : @date: Hours: @hours:",'message': 'you have made a entry on timesheet \n Date : @date: \n Hours: @hours:', 'message_color': None, 'message_origin': 'HR', 'message_type': 'simple_message', 'sended_to': 'public', 'slack_channel': ['CHVFM6U30'], 'submission_type': 'HR', 'working': True, 'message_subject': 'user_timesheet_entry'}
    request = {'message_key': 'user_timesheet_entry', 'message_type': 'simple_message','smtp_email': ['aayush_saini@excellencetechnologies.in'], 'to': ['aayush_saini@excellencetechnologies.in'], 'subject': 'user_timesheet_entry', 'phone': '8445679788', 'user': {'email': 'aayush_saini@excellencetechnolgies.in', 'name': 'aish'}, 'data': {'hours': '9', 'date': '05 Jun 2020'}}
    assert message_detail is not None
    assert request is not None
    assert type(system_variables)==list
    assert "mobile_message" in message_detail
    mobile_message_str = construct_mobile_message_str(message_detail=message_detail,request=request,system_variable=system_variables)
    assert mobile_message_str is not None



def test_construct_message_subject():
    message_detail = {'_id': ObjectId('5ee0bd14f1e987a7106610c1'),'message_subject':'user_timesheet_entry','message_key': 'user_timesheet_entry', 'channels': 'public', 'email_group': None, 'for_email': False, 'for_phone': False, 'for_slack': False, 'for_zapier': True,"mobile_message":"you have made a entry on timesheet Date : @date: Hours: @hours:",'message': 'you have made a entry on timesheet \n Date : @date: \n Hours: @hours:', 'message_color': None, 'message_origin': 'HR', 'message_type': 'simple_message', 'sended_to': 'public', 'slack_channel': ['CHVFM6U30'], 'submission_type': 'HR', 'working': True}
    request = {'message_key': 'user_timesheet_entry', 'message_type': 'simple_message','smtp_email': ['aayush_saini@excellencetechnologies.in'], 'to': ['aayush_saini@excellencetechnologies.in'], 'subject': 'user_timesheet_entry', 'phone': '8445679788', 'user': {'email': 'aayush_saini@excellencetechnolgies.in', 'name': 'aish'}, 'data': {'hours': '9', 'date': '05 Jun 2020'}}
    assert message_detail is not None
    assert request is not None
    assert type(system_variables)==list
    assert "message_subject" in message_detail
    message_subject,missing_payload=construct_message_subject(message_detail=message_detail,request=request,system_variable=system_variables)
    assert len(missing_payload) == 0
    assert message_subject is not None



def test_fetch_recipients_by_mode():
    request = {"to":["aayush_saini@excellencetechnologies.in"]}
    assert request is not None
    assert "to" in request
    assert type(request['to']) == list
    MAIL_SEND_TO = fetch_recipients_by_mode(request=request)
    assert MAIL_SEND_TO is not None
    assert type(MAIL_SEND_TO)==list
    assert len(MAIL_SEND_TO)>=1