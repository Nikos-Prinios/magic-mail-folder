#from pync import Notifier
# pip install pync
import os, fnmatch, smtplib, sys
import re, ntpath
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email import Encoders
import shutil
import subprocess
import time
from os.path import expanduser

global home, login, smtpserver, password, mmFolders
home = expanduser("~")
mmFolders = []

def sendmessage(message):
	cmd = "osascript -e \'display notification \""+ message + "\" with title \"Magic Mail Folder\"\'"
	os.system ( cmd )
	return

def init():
	global home, login,smtpserver,password
	settings = home + '/Magic-mail-folder/ressources/settings.txt'
	with open (settings, "r") as myfile:
		data=myfile.readlines()
		line = data[0].split()
	if len(line) == 4:
		login = line[0]
		smtpserver=line[1]+':'+line[2]
		password = line[3]
		return True
	else:
		sendmessage("Your email configuration doesn't work.")
		return False
		sys.exit()

def create_things(folder):
	d = folder + '/Sent files'
	f = folder + '/msg.txt'
	if not os.path.exists(d) :
		os.makedirs(d)
	if not os.path.exists(f) :
		file = open(f, "w")
		file.write("Magic Mail Folder - - - Things to keep")
		file.close()

def send_mail(to, subject, text, files):
    assert type(files) == list
    message = MIMEMultipart()
    message['From'] = login
    message['To'] = to
    message['Date'] = formatdate(localtime=True)
    message['Subject'] = subject
    message.attach(MIMEText(text))

    for f in files:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(f, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        message.attach(part)

    smtp = smtplib.SMTP(smtpserver)
    smtp.starttls()
    smtp.login(login, password)
    smtp.sendmail(login, to, message.as_string())
    smtp.close()
    sendmessage('Files sent to ' + to)
    return True

def subject(list):
	sub = '[MMF]'
	for f in list:
		sub = sub + ' ' + ntpath.basename(f)
	return sub

def body(folder):
	file = open(folder + '/msg.txt', 'r')
	return file.read()

def findFolders():
	global mmFolders
	for file in os.listdir(home + '/Desktop'):
		if re.search(r'[\w.-]+@[\w.-]+.\w+', file) :
			mmFolders.append(home + '/Desktop/' + file)

def searchForFiles(folder) :
	create_things(folder)
	pj = []
	for filename in os.listdir(folder):
		if not ".DS_Store" in filename and not "icon" in filename and not "Sent files" in filename and not "msg.tx" in filename :
			pj.append(folder + '/' + filename)
	if len(pj) > 0 :
		if send_mail(ntpath.basename(folder), subject(pj), body(folder),pj) :
			for f in pj :
				if not os.path.exists(folder + '/Sent files/' + ntpath.basename(f)):
					shutil.move (f,folder + '/Sent files/' + ntpath.basename(f))
				else :
					localtime = time.asctime(time.localtime(time.time()))
					shutil.move (f,folder + '/Sent files/[' + localtime + '] ' + ntpath.basename(f))

def zipit(folder)	:
	for filename in os.listdir(folder):
		if not "Sent files" in filename :
			if os.path.isdir(folder + '/' + filename):
				shutil.make_archive(folder + '/' + filename, "zip", folder + '/' + filename)
				shutil.rmtree(folder + '/' + filename)
				


if init() :
	findFolders()
	if len(mmFolders) > 0 :
		for folder in mmFolders:
			zipit(folder)
			searchForFiles(folder)

