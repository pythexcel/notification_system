from app import create_app as app
from app.email.util.template_util import attach_letter_head


#class for test attach letter head test cases
class TestAttachLetterHead:

    #Test case for if header footer message available
    def test_attach_letter_head(self):
        header="This is header of template"
        footer="This is footer of template"
        message="This is message of template"

        template = attach_letter_head(header,footer,message)
        assert template
        assert type(template) == str

    #Test case with header footer message is none data
    def test_attach_none_letter_head(self):
        header=""
        footer=""
        message=""

        template = attach_letter_head(header,footer,message)
        assert template
        assert type(template) == str
