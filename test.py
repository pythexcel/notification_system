import smtplib,ssl  





def work(port):
    if port == 587:   
        context = ssl.create_default_context()     
        mail = smtplib.SMTP(str("smtp.gmail.com"), port)
        mail.ehlo() 
        mail.starttls(context=context) 
        mail.ehlo() 
        mail.login("etechmusic8@gmail.com","Java@12345")
    else:
        mail = smtplib.SMTP_SSL(str(mail_server), port)
        mail.login(username,password)
    mail.quit()




try:
    work(port=587)
except Exception as e:
    print(repr(e))