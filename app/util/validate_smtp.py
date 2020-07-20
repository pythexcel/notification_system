
import smtplib,ssl    




def validate_smtp(username,password,port,smtp):
    if port == 587:   
        context = ssl.create_default_context()     
        mail = smtplib.SMTP(str(smtp), port)
        mail.ehlo() 
        mail.starttls(context=context) 
        mail.ehlo() 
        mail.login(username,password)
    else:
        mail = smtplib.SMTP_SSL(str(smtp), port)
        mail.login(username,password)
    mail.quit()
