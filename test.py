import re

words = ("fromDate","to",)
message = " HELLO ASDASD  #fromDate! to #toDate:"

all([re.search(w, text) for w in words])

rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:]|[\;])'
message_subject = re.sub(rexWithString, request.json['data'][detail], message_subject)