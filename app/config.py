import datetime

message_needs={"simple_message":{"message_type":True,"message_key":True,"email":True},"notfication_message":{"message_type":True,"email":True,"message_key":True}}
Mail_update_needs = {"mail_server":True,"mail_port":True,"mail_use_tls":True,"mail_username":True,"mail_password":True}

date_time = datetime.datetime.utcnow()
formatted_date = date_time.strftime("%d-%B-%Y")
system_variable ={"Date":formatted_date}




