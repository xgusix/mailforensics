import mailforensics
import imaplib
import email

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('user@gmail.com', 'password')

mail.select("inbox") # connect to inbox.

result, data = mail.uid('search', None, "ALL") # search and return uids instead
latest_email_uid = data[0].split()[-1]
result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
raw_email = data[0][1]
email_message = email.message_from_string(raw_email)

mf = mailforensics

print mf.get_body(email_message)

jumps= mf.get_jumps(email_message)
for i in jumps:
	print "[+] " + i

ts= mf.get_timestamps(jumps)
for i in ts:
	print i

ts1 = mf.sync_timestamps(ts)
for i in ts1:
	print '[----] '+ str(i)


ips = mf.get_ip_addresses_implied(email_message)
for i in ips:
	print "[+] " + i

att = mf.get_attachments(email_message)

if len(att)>0:
	for i in att:
		print i['filename']
		f=open(i['filename'], 'w')
		f.write(i['file'])
		f.close()