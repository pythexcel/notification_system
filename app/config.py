import cloudinary

base_url = "http://176.9.137.77:8005/"

smtp_counts = {
    'smtp.gmail.com' : 5 ,
    'smtp.office365.com' : 2
}

dates_converter = [
    "dateofjoining",
    "dob",
    "training_completion_date",
    "termination_date",
    "next_increment_date",
    "start_increment_date",
    "fromDate",
    "toDate"
    ]
message_needs={
    "simple_message":[
            "message_type",

            "message_key",

            ],

    "notfication_message":[

            "message_type",
            
            "user",
            
            "message_key"],
            
    "button_message":[

            "message_type",
            
            "message_key"
                ]        
            }

config_info = cloudinary.config( 
    cloud_name='dp0y84e66',
    api_key= '166465296448686',
    api_secret= '0ks_nfDa39dimm7joD8gKSEdz6g'
)

fcm_api_key = "AIzaSyBO2S6xvT5qD2KuTYw-emCpNaJMVFZrzU0"
