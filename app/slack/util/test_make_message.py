
import datetime
from app.slack.util.make_message import MakeMessage

#Test cases for create slack message with replace slack id with user tag
class TestMakeMessage:

    system_variable ={"Date":datetime.datetime.utcnow().strftime("%d-%B-%Y")}
    message = "@user:  @data:"
    message_variables = ['user','data']
    system_require = []


    #Test case with proper request
    def test_MakeMessage(self):
        user_detail = {'user': '<@UJCNCV1DJ>', 'data': 'Report: \nworked with tms\n', 'slack_channel': [], 'message_type': 'simple_message', 'message_key': 'check-in'}
        message_string = MakeMessage(message_str=self.message,message_variables=self.message_variables,user_detail=user_detail,system_require=self.system_require,system_variable=self.system_variable)
        assert message_string != None
        assert type(message_string) == str

    #Test case if user data not available in request
    def test_MakeMessage_if_not_user(self):
        user_detail = {'data': 'Report: \nworked with tms\n', 'slack_channel': [], 'message_type': 'simple_message', 'message_key': 'check-in'}
        message_string = MakeMessage(message_str=self.message,message_variables=self.message_variables,user_detail=user_detail,system_require=self.system_require,system_variable=self.system_variable)
        assert message_string != None
        assert type(message_string) == str

    #Test case if user data and data variables not available in request
    def test_MakeMessage_(self):
        user_detail = {'slack_channel': [], 'message_type': 'simple_message', 'message_key': 'check-in'}
        message_string = MakeMessage(message_str=self.message,message_variables=self.message_variables,user_detail=user_detail,system_require=self.system_require,system_variable=self.system_variable)
        assert message_string != None
        assert type(message_string) == str
