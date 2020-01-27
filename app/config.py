import cloudinary

bounced_mail_since = '23-Jan-2020'
remind_mail_since = '24-Jan-2020'


hard_bounce_status = ["5.0.0","5.1.0","5.1.1","5.1.2","5.1.3","5.1.4","5.1.5","5.1.6","5.1.7","5.1.8","5.2.3","5.2.4","5.3.0","5.3.2","5.3.3","5.3.2","5.3.3","5.3.4","5.4.0","5.4.1","5.4.2","5.4.3","5.4.4","5.4.6","5.4.7","5.5.0","5.5.1","5.5.2","5.5.4","5.5.5","5.6.0","5.6.1","5.6.2","5.6.3","5.6.4","5.6.5","5.7.0","5.7.1","5.7.2","5.7.3","5.7.4","5.7.5","5.7.6","5.7.7"]
soft_bounce_status = ["5.2.0","5.2.1","5.2.2","5.3.1","5.4.5","5.5.3"]


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

messages = [
    {
        "message_key":"check-in",
        "channels":"private",
        "message":"@user: \n @data:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"check-in_notification",
        "channels":"public",
        "message":"@user: have created daily check-in at @Date:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"weekly_notification",
        "channels":"public",
        "message":"@user: have created weekly report at @Date:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"weekly_reviewed_notification",
        "channels":"public",
        "message":"@user: your weekly report is reviewed by @data:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"monthly_reviewed_notification",
        "channels":"public",
        "message":"@user: your monthly report is reviewed by @data:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"weekly_skipped_notification",
        "channels":"public",
        "message":"@user: your weekly report is skipped by @data:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"missed_checkin_notification",
        "channels":"public",
        "message":"@user: you have missed @data: check-in",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"monthly_notification",
        "channels":"public",
        "message":"@user: have created monthly report @Date:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"monthly_manager_reminder",
        "channels":"public",
        "message":"@user: you have monthly report's pending to be reviewed",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"monthly_reminder",
        "channels":"public",
        "message":"@user: Please create your monthly report of @data: till 10th of this month. Failing to do so will automatically set your monthly review to 0.",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"review_count_message",
        "channels":"public",
        "message":"@user: you have @data: reports left to review",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    }
]



