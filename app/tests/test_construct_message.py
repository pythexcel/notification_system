from app.util.template_util import construct_message_str


#Test cases for create messages
class TestConstructMessageStr:
    system_variables = [{'_id': '5dfc6108c837f7bc90ab3ccd', 'name': '#joining_date', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd5', 'name': '#director_signature', 'value': '<p><strong>Excellence Technologies,</strong></p>\n<p><strong>Manish Prakash</strong></p>\n<p><strong>(Director)</strong></p>', 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd6', 'name': '#venue', 'value': 'C-86 B Excellence Technosoft Pvt. Ltd Noida Sector 8', 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cd9', 'name': '#numberOfDays', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce5', 'name': '#relieving_date', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce9', 'name': '#office_time', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd3', 'name': '#termination_date', 'value': None, 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cd7', 'name': '#company', 'value': 'Excellence Technosoft Pvt. Ltd', 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3ce3', 'name': '#date_of_sending', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cdf', 'name': '#details', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cda', 'name': '#name', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cdd', 'name': '#reason', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce0', 'name': '#job_title', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd0', 'name': '#map_location', 'value': 'https://www.google.co.in/maps/place/Excellence+Technologies/@28.5959817,77.3260043,17z/data=!3m1!4b1!4m5!3m4!1s0x390ce4fc8c75d9e:0x4ea29a8e67042fb9!8m2!3d28.595977!4d77.328193?hl=en', 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cd1', 'name': '#employee_user_name', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce1', 'name': '#login_id', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd8', 'name': '#hr_signature', 'value': '<p>HR <br/> Juhi Singh <br/> Landline No: 0120-4113772 <br/> https://excellencetechnologies.in/<br/>https://www.facebook.com/ExcellenceTechnologies<br/>https://itunes.apple.com/in/app/career-app-by-etech/id1399557922?mt=8<br/>', 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3ce4', 'name': '#resignation_date', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce7', 'name': '#upper_limit_salary', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cce', 'name': '#logo', 'value': "<p><img src='https://res.cloudinary.com/dp0y84e66/image/upload/v1568791251/logo.e5be347d_yf4q90.png' width='170' height='50'/></p>", 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cdc', 'name': '#toDate', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce8', 'name': '#increament_after_month', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cdb', 'name': '#fromDate', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce2', 'name': '#employee_id', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ccc', 'name': '#date', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ccf', 'name': '#salary', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cde', 'name': '#month', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3ce6', 'name': '#lower_limit_salary', 'value': None, 'variable_type': 'user'}, {'_id': '5dfc6108c837f7bc90ab3cd2', 'name': '#training_completion_date', 'value': None, 'variable_type': 'system'}, {'_id': '5dfc6108c837f7bc90ab3cd4', 'name': '#designation', 'value': None, 'variable_type': 'user'}]


    #Test case with proper request.
    def test_construct_message_str(self):
        message_detail = "you have made a entry on timesheet Date : @date: Hours: @hours:"
        request = {'hours': '9', 'date': '05 Jun 2020'}
        message_str,missing_payload=construct_message_str(message_detail=message_detail,request=request,system_variable=self.system_variables)
        assert len(missing_payload) == 0
        assert message_str is not None


    #Test case for if data variables not proper in request
    def test_construct_message_if_message_not_proper(self):
        message_detail = "you have made a entry on timesheet Date : @ date : Hours: @ hours :"
        request = {'hour': '9', 'dat': '05 Jun 2020'}
        message_str,missing_payload=construct_message_str(message_detail=message_detail,request=request,system_variable=self.system_variables)
        assert len(missing_payload) == 0
        assert message_str is not None


    #test case for if data variables available in message details but not value available in request
    def test_construct_message_data_variables(self):
        message_detail = "you have made a entry on timesheet Date : @date: Hours: @hours:"
        request = {'number': '9', 'dateutil': '05 Jun 2020'}
        message_str,missing_payload=construct_message_str(message_detail=message_detail,request=request,system_variable=self.system_variables)
        assert len(missing_payload) == 0
        assert message_str is not None

