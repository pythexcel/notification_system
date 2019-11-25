import cloudinary
Base_url = '176.9.137.77:8007'

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



