message_needs={
    "simple_message":[
            "message_type",

            "message_key",

            "user"],

    "notfication_message":[

            "message_type",
            
            "email",
            
            "message_key"]
            }




messages = [
    {
        "message_key":"check-in",
        "channel":"private",
        "message":"@user: \n @data:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"check-in_notification",
        "channel":"public",
        "message":"@user: have created daily check-in at @Date:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"weekly_notification",
        "channel":"public",
        "message":"@user: have created weekly report at @Date:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"weekly_reviewed_notification",
        "channel":"public",
        "message":"@user: your weekly report is reviewed by @data:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"monthly_reviewed_notification",
        "channel":"public",
        "message":"@user: your monthly report is reviewed by @data:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"weekly_skipped_notification",
        "channel":"public",
        "message":"@user: your weekly report is skipped by @data:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"missed_checkin_notification",
        "channel":"public",
        "message":"@user: you have missed @data: check-in",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"monthly_notification",
        "channel":"public",
        "message":"@user: have created monthly report @Date:",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"monthly_manager_reminder",
        "channel":"public",
        "message":"@user: you have monthly report's pending to be reviewed",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    },
    {
        "message_key":"monthly_reminder",
        "channel":"public",
        "message":"@user: Please create your monthly report of @data: till 10th of this month. Failing to do so will automatically set your monthly review to 0.",
        "message_color":None,
        "message_origin":"TMS",
        "message_type":"simple_message",
        "working":True
    }
]



