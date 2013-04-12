import re

from datetime import datetime,timedelta
import imaplib
import email


MONTHS = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7,
'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
#-------------------------------------------------------------------------------
#This function returns a list with the 'recieved' headers included in the e-mail
# received as a parameter.
#-------------------------------------------------------------------------------
def get_jumps(email_message):
	received = []
	for header in email_message.items():
		#print header[0].lower() + ': ' + header[1]
		if ('received' in header[0].lower() 
			and not 'spf' in header[0].lower()):
			received.append(header[0] + ': ' + header[1])
	return received
#-------------------------------------------------------------------------------
#Returns the body of an e-mail received as a parameter.
#-------------------------------------------------------------------------------
def get_body(email_message):
	maintype = email_message.get_content_maintype()
	if maintype == 'multipart':
		for part in email_message.get_payload():
			if part.get_content_maintype() == 'text':
				return part.get_payload()
	elif maintype == 'text':
		return email_message.get_payload()

#-------------------------------------------------------------------------------
#Space reserved for the function blind_search(body, text, prev_post_words)
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#Fetchs IP adresses in the headers and return on findings in a list.
#-------------------------------------------------------------------------------
def get_ip_addresses_implied(email_message):
	ip_addresses = []
	for header in email_message.items():
		ip = re.search(r'((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9])', header[1], re.I)
		if ip:
			ip=ip.group()
			ip_addresses.append(ip)
	return set(ip_addresses)

#-------------------------------------------------------------------------------
#Gets the timestamps of the different jumps that the e-mail did before reaching
#its destination. It returns a list of tuplas with the format 
#[timestamp, header]
#-------------------------------------------------------------------------------
def get_timestamps(jump_list):
	ts = []
	for jump in jump_list:
		timestamp = re.search(r'([0-9]{1,2}\s[a-zA-Z]{3}\s[0-9]{4}\s[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}\s[+-][0-9]{2}00)'
			, jump, re.I)
		ts.append([timestamp.group(),jump])
	return ts

#-------------------------------------------------------------------------------
#Parse the timestamps and TRY to syncronice them acording whit your local
#timezone. As the Daily Saving Time system changes depending on the different
#countries and continents, this function as it is right now won't work properly
#most of the time. I'm planning on keep working on it after studying how the
#different systems work...
#BTW, it receives as input a list of tuplas as the one that get_timestamps
#retuns and your local timezone (GMT). Returns a list of tuplas with the format:
#[timestamp, header], being timestamp a datetime.datetime object.
#-------------------------------------------------------------------------------
def sync_timestamps(ts_list, local_timezone=1):
	for ts in ts_list:
		bar = ts[0].split(' ')
		time_split = bar[3].split(':')
		date = datetime(int(bar[2]),MONTHS[bar[1]],int(bar[0]), 
			int(time_split[0]), int(time_split[1]), int(time_split[2]))
		server_timezone = int(bar[4][1:3])
		if bar[4][0] == '+':
			server_timezone *= -1
		ts[0] = date + timedelta(hours=(server_timezone + local_timezone))
	return ts_list

#-------------------------------------------------------------------------------
#Returns the attachments on the e-mail received. The return structure is a list 
#of dictionaries like:
#{'filename':filename, 'type': filetype, 'file':file_ready_to_be_processed}
#-------------------------------------------------------------------------------
def get_attachments(email_message):
    payload = email_message.get_payload()
    attachments = []
    for section in payload:
    	if section.get_filename():
    		attachment = {}
    		attachment['filename'] = section.get_filename()
    		attachment['type'] = section.get_content_type()
    		attachment['file'] = section.get_payload(decode=True)
    		attachments.append(attachment)
    return attachments


