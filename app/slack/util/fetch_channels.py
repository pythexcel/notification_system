

# Common function for fetch channels form tms request
def FetchChannels(user_detail=None,message_detail=None):
    channels = []          
    #It will take slack channels if slack channel available in user details
    if 'slack_channel' in user_detail:
        for data in user_detail['slack_channel']:
            channels.append(data)
    else:
        pass  
    #It will take slack channels if slack channel available in message details
    if 'slack_channel' in message_detail:
        if message_detail['slack_channel'] is not None:
            for elem in message_detail['slack_channel']:
                channels.append(elem)       
    #will return array of slack channels
    return channels




#function for fetch recipients if email group email available in message request it will fetch all mails and return array
def FetchRecipient(user_detail=None,message_detail=None):
    recipient = []
    if 'email_group' in user_detail:
        for data in user_detail['email_group']:
            recipient.append(data)
    else:
        pass
    if 'email_group' in message_detail:
        if message_detail['email_group'] is not None:
            for elem in message_detail['email_group']:
                recipient.append(elem)
    else:
        pass
    return recipient
