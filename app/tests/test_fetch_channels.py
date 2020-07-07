from app.util.fetch_channels import FetchChannels


#test case for fetch channels from user details
class TestFetchChannels:

    #test case for fetch slack channels from request
    def test_FetchChannels(self):
        slack_user_detail = {"slack_channel":['CVHCL21','CHGT21'],"sended_to":"public"}
        message_detail = {"slack_channel":['CVHCL21','CHGT21'],"sended_to":"public"}
        channels = FetchChannels(user_detail=slack_user_detail,message_detail=message_detail)
        assert type(channels) == list
        assert len(channels)>0
