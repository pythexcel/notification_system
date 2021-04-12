
from app.email.util.date_convertor import convert_dates_to_format



#test cases for test date conversion 
class TestConvertDatesToFormat:

    dates_converter = ["dateofjoining","dob","date","interview_date","training_completion_date","termination_date","next_increment_date","start_increment_date","fromDate","toDate","reporting_date"]


    #test case with proper requets
    def test_convert_dates_to_format(self):
        request = {"message_key": "user_timesheet_entry","message_type": "simple_message","user": {"email": "aishwary@excellencetechnolgies.in","name":"aish"},
            "data": {
                "hours": "9",
                "date": "Friday, June 5th 2020, 2:15:49 pm"
                    }
                }
        updated_data = convert_dates_to_format(dates_converter=self.dates_converter,req=request)
        assert updated_data is not None


    #Test case for if date data variables not available in request
    def test_convert_dates_if_data_not_available(self):
        request = {"message_key": "user_timesheet_entry","message_type": "simple_message","user": {"email": "aishwary@excellencetechnolgies.in","name":"aish"},
                }
        updated_data = convert_dates_to_format(dates_converter=self.dates_converter,req=request)
        assert updated_data is not None


    #test case for if date is empty in request
    def test_convert_dates_if_not_date(self):
        request = {"message_key": "user_timesheet_entry","message_type": "simple_message","user": {"email": "aishwary@excellencetechnolgies.in","name":"aish"},
            "data": {
                "hours": "9",
                "date": ""
                    }
                }
        updated_data = convert_dates_to_format(dates_converter=self.dates_converter,req=request)
        assert updated_data is not None
