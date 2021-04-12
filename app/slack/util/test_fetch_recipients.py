
from app.slack.util.fetch_channels import FetchRecipient


class TestFetchRecipient:

    #Test case for fetch email recipients from requests
    def test_FetchRecipient(self):
        slack_user_detail = {"email_group":["testing1@gmail.com","testing2@gmail.com"]}
        message_detail = {"email_group":["testing3@gmail.com","testing4@gmail.com"]}
        status = FetchRecipient(user_detail=slack_user_detail,message_detail=message_detail)
        assert type(status) == list
        assert status
