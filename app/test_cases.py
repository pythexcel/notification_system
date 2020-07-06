from app import create_app as app
from app.util import allowed_file,FetchRecipient,serialize_doc,FetchChannels,template_requirement,MakeMessage,campaign_details,convert_dates_to_format
from app.modules.phone_util import create_sms
from bson import ObjectId
import datetime
from app.model.template import attach_letter_head
from app.modules.template_util import construct_message_str,construct_mobile_message_str,construct_message_subject,fetch_recipients_by_mode

system_variables = [{'_id': '5dfc6108c837f7bc90ab3ccd', 'name': '#joining_date', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd5', 'name': '#director_signature', 'value': '<p><strong>Excellence Technologies,</strong></p>\n<p><strong>Manish Prakash</strong></p>\n<p><strong>(Director)</strong></p>', 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd6', 'name': '#venue', 'value': 'C-86 B Excellence Technosoft Pvt. Ltd Noida Sector 8', 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cd9', 'name': '#numberOfDays', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce5', 'name': '#relieving_date', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce9', 'name': '#office_time', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd3', 'name': '#termination_date', 'value': None, 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cd7', 'name': '#company', 'value': 'Excellence Technosoft Pvt. Ltd', 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3ce3', 'name': '#date_of_sending', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cdf', 'name': '#details', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cda', 'name': '#name', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cdd', 'name': '#reason', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce0', 'name': '#job_title', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd0', 'name': '#map_location', 'value': 'https://www.google.co.in/maps/place/Excellence+Technologies/@28.5959817,77.3260043,17z/data=!3m1!4b1!4m5!3m4!1s0x390ce4fc8c75d9e:0x4ea29a8e67042fb9!8m2!3d28.595977!4d77.328193?hl=en', 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cd1', 'name': '#employee_user_name', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce1', 'name': '#login_id', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd8', 'name': '#hr_signature', 'value': '<p>HR <br/> Juhi Singh <br/> Landline No: 0120-4113772 <br/> https://excellencetechnologies.in/<br/>https://www.facebook.com/ExcellenceTechnologies<br/>https://itunes.apple.com/in/app/career-app-by-etech/id1399557922?mt=8<br/>', 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3ce4', 'name': '#resignation_date', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce7', 'name': '#upper_limit_salary', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cce', 'name': '#logo', 'value': "<p><img src='https://res.cloudinary.com/dp0y84e66/image/upload/v1568791251/logo.e5be347d_yf4q90.png' width='170' height='50'/></p>", 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cdc', 'name': '#toDate', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce8', 'name': '#increament_after_month', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cdb', 'name': '#fromDate', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce2', 'name': '#employee_id', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ccc', 'name': '#date', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ccf', 'name': '#salary', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cde', 'name': '#month', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce6', 'name': '#lower_limit_salary', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd2', 'name': '#training_completion_date', 'value': None, 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cd4', 'name': '#designation', 'value': None, 'variable_type': 'user'}]



#Test case for create mobile message
class TestClassCreateSms:

    phone = "8445679788"
    mobile_message_str = "testing"

    def test_create_sms(self):
        phone_status,phone_issue,phone_issue_message = create_sms(phone=self.phone, mobile_message_str=self.mobile_message_str)
        assert phone_status != False and phone_issue != True


#Test for check file type is valid or not
class TestClassFilename:

    filename = "testing.pdf"
    filename1 = "testing.txt.pdf"

    def test_filename1(self):
        file = allowed_file(filename=self.filename)
        assert file != None
        assert file == True

    def test_filename2(self):
        file = allowed_file(filename=self.filename1)
        assert file != None
        assert file == True


class TestFetchRecipient:

    slack_user_detail = {"email_group":["testing1@gmail.com","testing2@gmail.com"]}
    message_detail = {"email_group":["testing3@gmail.com","testing4@gmail.com"]}

    def test_FetchRecipient(self):
        status = FetchRecipient(slack_user_detail=self.slack_user_detail,message_detail=self.message_detail)
        assert type(status) == list
        assert status


#test for serilizer
class TestSerializeDoc:
    doc = {"_id":ObjectId("507f1f77bcf86cd799439011"),"data":"data"}
    doc1 = {"_id":str("507f1f77bcf86cd799439011"),"data":"data"}

    def test_serialize_doc(self):
        serialize = serialize_doc(self.doc) 
        assert type(serialize['_id']) == str

    def test_serialize_doc2(self):
        serialize = serialize_doc(self.doc1) 
        assert type(serialize['_id']) == str



#test case for fetch channels from user details
class TestFetchChannels:

    slack_user_detail = {"slack_channel":['CVHCL21','CHGT21'],"sended_to":"public"}
    message_detail = {"slack_channel":['CVHCL21','CHGT21'],"sended_to":"public"}

    def test_FetchChannels(self):
        channels = FetchChannels(slack_user_detail=self.slack_user_detail,message_detail=self.message_detail)
        assert type(channels) == list
        assert len(channels)>0


class TestMakeMessage:

    message = "@user:  @data:"
    message_variables = ['user','data']
    slack_user_detail = {'user': '<@UJCNCV1DJ>', 'data': 'Report: \nworked with tms\n', 'slack_channel': [], 'message_type': 'simple_message', 'message_key': 'check-in'}
    system_require = []
    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}

    slack_user_detail1 = {'data': 'Report: \nworked with tms\n', 'slack_channel': [], 'message_type': 'simple_message', 'message_key': 'check-in'}
    slack_user_detail2 = {'slack_channel': [], 'message_type': 'simple_message', 'message_key': 'check-in'}


    def test_MakeMessage(self):
        message_string = MakeMessage(message_str=self.message,message_variables=self.message_variables,slack_user_detail=self.slack_user_detail,system_require=self.system_require,system_variable=self.system_variable)
        assert message_string != None
        assert type(message_string) == str

    def test_MakeMessage1(self):
        message_string = MakeMessage(message_str=self.message,message_variables=self.message_variables,slack_user_detail=self.slack_user_detail1,system_require=self.system_require,system_variable=self.system_variable)
        assert message_string != None
        assert type(message_string) == str

    def test_MakeMessage2(self):
        message_string = MakeMessage(message_str=self.message,message_variables=self.message_variables,slack_user_detail=self.slack_user_detail2,system_require=self.system_require,system_variable=self.system_variable)
        assert message_string != None
        assert type(message_string) == str


class TestConvertDatesToFormat:

    dates_converter = ["dateofjoining","dob","date","interview_date","training_completion_date","termination_date","next_increment_date","start_increment_date","fromDate","toDate","reporting_date"]
    request = {"message_key": "user_timesheet_entry","message_type": "simple_message","user": {"email": "aishwary@excellencetechnolgies.in","name":"aish"},
        "data": {
            "hours": "9",
            "date": "Friday, June 5th 2020, 2:15:49 pm"
                }
            }

    request1 = {"message_key": "user_timesheet_entry","message_type": "simple_message","user": {"email": "aishwary@excellencetechnolgies.in","name":"aish"},
            }

    request2 = {"message_key": "user_timesheet_entry","message_type": "simple_message","user": {"email": "aishwary@excellencetechnolgies.in","name":"aish"},
        "data": {
            "hours": "9",
            "date": ""
                }
            }

    def test_convert_dates_to_format(self):
        updated_data = convert_dates_to_format(dates_converter=self.dates_converter,req=self.request)
        assert updated_data is not None

    def test_convert_dates_to_format1(self):
        updated_data = convert_dates_to_format(dates_converter=self.dates_converter,req=self.request1)
        assert updated_data is not None

    def test_convert_dates_to_format2(self):
        updated_data = convert_dates_to_format(dates_converter=self.dates_converter,req=self.request2)
        assert updated_data is not None




class TestAttachLetterHead:

    header="This is header of template"
    footer="This is footer of template"
    message="This is message of template"

    def test_attach_letter_head(self):
        template = attach_letter_head(self.header,self.footer,self.message)
        assert template
        assert type(template) == str

class TestConstructMessageStr:

    message_detail = "you have made a entry on timesheet Date : @date: Hours: @hours:"
    request = {'hours': '9', 'date': '05 Jun 2020'}
    message_detail1 = "you have made a entry on timesheet Date : @ date : Hours: @ hours :"
    request1 = {'hour': '9', 'dat': '05 Jun 2020'}
    message_detail2 = "you have made a entry on timesheet Date : @date:: Hours: @hours::"

    def test_construct_message_str(self):
        message_str,missing_payload=construct_message_str(message_detail=self.message_detail,request=self.request,system_variable=system_variables)
        assert len(missing_payload) == 0
        assert message_str is not None

    def test_construct_message_str1(self):
        message_str,missing_payload=construct_message_str(message_detail=self.message_detail1,request=self.request,system_variable=system_variables)
        assert len(missing_payload) == 0
        assert message_str is not None

    def test_construct_message_str2(self):
        message_str,missing_payload=construct_message_str(message_detail=self.message_detail1,request=self.request1,system_variable=system_variables)
        assert len(missing_payload) == 0
        assert message_str is not None

    def test_construct_message_str3(self):
        message_str,missing_payload=construct_message_str(message_detail=self.message_detail2,request=self.request1,system_variable=system_variables)
        assert len(missing_payload) == 0
        assert message_str is not None


class TestConstructMobileMessage:

    message_detail = {'_id': ObjectId('5ee0bd14f1e987a7106610c1'), 'message_key': 'user_timesheet_entry', 'channels': 'public', 'email_group': None, 'for_email': False, 'for_phone': False, 'for_slack': False, 'for_zapier': True,"mobile_message":"you have made a entry on timesheet Date : @date: Hours: @hours:",'message': 'you have made a entry on timesheet \n Date : @date: \n Hours: @hours:', 'message_color': None, 'message_origin': 'HR', 'message_type': 'simple_message', 'sended_to': 'public', 'slack_channel': ['CHVFM6U30'], 'submission_type': 'HR', 'working': True, 'message_subject': 'user_timesheet_entry'}
    request = {'message_key': 'user_timesheet_entry', 'message_type': 'simple_message','smtp_email': ['aayush_saini@excellencetechnologies.in'], 'to': ['aayush_saini@excellencetechnologies.in'], 'subject': 'user_timesheet_entry', 'phone': '8445679788', 'user': {'email': 'aayush_saini@excellencetechnolgies.in', 'name': 'aish'}, 'data': {'hours': '9', 'date': '05 Jun 2020'}}
    message_detail1 = {'_id': ObjectId('5ee0bd14f1e987a7106610c1'), 'message_key': 'user_timesheet_entry', 'channels': 'public', 'email_group': None, 'for_email': False, 'for_phone': False, 'for_slack': False, 'for_zapier': True, 'message_color': None, 'message_origin': 'HR', 'message_type': 'simple_message', 'sended_to': 'public', 'slack_channel': ['CHVFM6U30'], 'submission_type': 'HR', 'working': True, 'message_subject': 'user_timesheet_entry'}
    message_detail2 = {'_id': ObjectId('5ee0bd14f1e987a7106610c1'), 'message_key': 'user_timesheet_entry', 'channels': 'public', 'email_group': None, 'for_email': False, 'for_phone': False, 'for_slack': False, 'for_zapier': True,"mobile_message":"you have made a entry on timesheet Date : @@date:: Hours: @@hours::",'message': 'you have made a entry on timesheet \n Date : @date: \n Hours: @hours:', 'message_color': None, 'message_origin': 'HR', 'message_type': 'simple_message', 'sended_to': 'public', 'slack_channel': ['CHVFM6U30'], 'submission_type': 'HR', 'working': True, 'message_subject': 'user_timesheet_entry'}


    def test_construct_mobile_message_str(self):
        mobile_message_str = construct_mobile_message_str(message_detail = self.message_detail,request=self.request,system_variable=system_variables)
        assert mobile_message_str is not None

    def test_construct_mobile_message_str1(self):
        mobile_message_str = construct_mobile_message_str(message_detail = self.message_detail1,request=self.request,system_variable=system_variables)
        assert mobile_message_str is not None

    def test_construct_mobile_message_str2(self):
        mobile_message_str = construct_mobile_message_str(message_detail = self.message_detail2,request=self.request,system_variable=system_variables)
        assert mobile_message_str is not None



class TestConstructMessageSubject:

    message_detail = {'_id': ObjectId('5ee0bd14f1e987a7106610c1'),'message_subject':'user_timesheet_entry','message_key': 'user_timesheet_entry', 'channels': 'public', 'email_group': None, 'for_email': False, 'for_phone': False, 'for_slack': False, 'for_zapier': True,"mobile_message":"you have made a entry on timesheet Date : @date: Hours: @hours:",'message': 'you have made a entry on timesheet \n Date : @date: \n Hours: @hours:', 'message_color': None, 'message_origin': 'HR', 'message_type': 'simple_message', 'sended_to': 'public', 'slack_channel': ['CHVFM6U30'], 'submission_type': 'HR', 'working': True}
    request = {'message_key': 'user_timesheet_entry', 'message_type': 'simple_message','smtp_email': ['aayush_saini@excellencetechnologies.in'], 'to': ['aayush_saini@excellencetechnologies.in'], 'subject': 'user_timesheet_entry', 'phone': '8445679788', 'user': {'email': 'aayush_saini@excellencetechnolgies.in', 'name': 'aish'}, 'data': {'hours': '9', 'date': '05 Jun 2020'}}
    message_detail2 = {'_id': ObjectId('5ee0bd14f1e987a7106610c1'),'message_key': 'user_timesheet_entry', 'channels': 'public', 'email_group': None, 'for_email': False, 'for_phone': False, 'for_slack': False, 'for_zapier': True,"mobile_message":"you have made a entry on timesheet Date : @date: Hours: @hours:",'message': 'you have made a entry on timesheet \n Date : @date: \n Hours: @hours:', 'message_color': None, 'message_origin': 'HR', 'message_type': 'simple_message', 'sended_to': 'public', 'slack_channel': ['CHVFM6U30'], 'submission_type': 'HR', 'working': True}
    message_detail3 = {'_id': ObjectId('5ee0bd14f1e987a7106610c1'),'message_subject':'user_timesheet_entry','message_key': 'user_timesheet_entry', 'channels': 'public', 'email_group': None, 'for_email': False, 'for_phone': False, 'for_slack': False, 'for_zapier': True,"mobile_message":"you have made a entry on timesheet Date : date: Hours: hours:",'message': 'you have made a entry on timesheet \n Date : date: \n Hours: hours:', 'message_color': None, 'message_origin': 'HR', 'message_type': 'simple_message', 'sended_to': 'public', 'slack_channel': ['CHVFM6U30'], 'submission_type': 'HR', 'working': True}


    def test_construct_message_subject(self):
        message_subject,missing_payload=construct_message_subject(message_detail=self.message_detail,request=self.request,system_variable=system_variables)
        assert len(missing_payload) == 0
        assert message_subject is not None

    def test_construct_message_subject2(self):
        message_subject,missing_payload=construct_message_subject(message_detail=self.message_detail2,request=self.request,system_variable=system_variables)
        assert len(missing_payload) == 0
        assert message_subject is not None

    def test_construct_message_subject3(self):
        message_subject,missing_payload=construct_message_subject(message_detail=self.message_detail3,request=self.request,system_variable=system_variables)
        assert len(missing_payload) == 0
        assert message_subject is not None

