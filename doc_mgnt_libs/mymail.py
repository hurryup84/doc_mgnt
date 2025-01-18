# -*- coding: utf-8 -*-
# Something in lines of http://stackoverflow.com/questions/348630/how-can-i-download-all-emails-with-attachments-from-gmail
# Make sure you have IMAP enabled in your gmail settings.
# Right now it won't download same file name twice even if their contents are different.

from datetime import date
from email.header import decode_header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import COMMASPACE, formatdate
from os.path import basename
import email
import getpass, imaplib
import json
import locale
import logging
import os
import smtplib
import sys
import imghdr
import shutil

logger = logging.getLogger('root')
pjoin = os.path.join




def build_mail_content(key_info, mail_info, config, mail_info_path={}):
    '''tested'''
    root_path = "%sdigital_depot" % config["WEBDAV_PATH"]
    if key_info:
        content = "Added new keys \n%s" %key_info
    else:
        content = ""
    if mail_info:
        content = "%sNew PDFs stored\n\n" % content
        for filename, category in mail_info.items():
            content = "%s category: %s \n %s \n" %(content, category, filename)
            full_path = "%s/%s" %(root_path, mail_info_path[filename])
            content = "%s available at: \n %s \n\n" %(content, full_path)

    return content  


def update_key_dict(dpath, dfile, key, value):
    '''tested'''
    keys = json.load(open(pjoin(dpath, dfile)))
    keys[key] = value

    try:
        json.dump(keys, open(pjoin(dpath, dfile),'w'), indent=4, ensure_ascii=False, sort_keys=True) 
        key_info = "updated %s with \n %s : %s" %(dfile, key, value) 
    except UnicodeDecodeError as e:
        logger.error("can not wrie %s sorted, writing unsorted." %dfile)
        try:
            json.dump(keys, open(pjoin(dpath, dfile),'w'), indent=4, ensure_ascii=False, sort_keys=False)  
            key_info = "updated %s with \n %s : %s" %(dfile, key, value)
        except UnicodeDecodeError as e:
            logger.error("having also trouble writing %s unsorted. skipping update of keys")
            key_info = "could not update %s, with %s:%s.unicode trouble \n" %(dfile, key, value)

    return key_info



def update_keys(subjects, keyfile_path):
    '''tested'''
    UNKNOWN_HELP = """could not identify keyword, please use one of #CAT #CID #CWOID #DOC #NAME #CIDCAT #CWOIDCAT"""
    key_infos = ""
    for subject in subjects:

        logger.debug("in update keys loop")
        key_info = ""
        logger.debug("try to interpret subject for new keys")
        subject = subject.split()
        key_len = len(subject)
        try:
            key_type = subject[0].upper()
            key = subject[1].lower().replace(" ", "")
            value = subject[2]
            if key_len == 4:
                value_cat = subject[3]
        except IndexError as e:
            logger.error("Get not well formed email subject")
            return key_info
        if key_len == 3:
            if key_type == "#CAT":
                key_info = update_key_dict(keyfile_path, "CATEGORY.json", key, value)

            elif key_type == "#CID":
                key_info =update_key_dict(keyfile_path, "CUSTOMER_ID.json", key, value)   
          
            elif key_type == "#CWOID":
                key_info = update_key_dict(keyfile_path, "COMPANIES_WO_ID.json", key, value) 

            elif key_type == "#DOC":
                key_info = update_key_dict(keyfile_path, "DOCTYPES.json", key, value) 

            elif key_type == "#NAME":
                key_info = update_key_dict(keyfile_path, "NAMES.json", key, value)   

            else:
                logger.error(UNKNOWN_HELP)
                key_info = "%s \n %s" %(key_info, UNKNOWN_HELP)        

        elif key_len == 4:
            if key_type == "#CIDCAT":
                key_info = update_key_dict(keyfile_path, "CUSTOMER_ID.json", key, value)
                key_info = "%s\n%s" %(key_info, update_key_dict(keyfile_path, "CATEGORY.json", value, value_cat)   )         
          
            elif key_type == "#CWOIDCAT":
                key_info = update_key_dict(keyfile_path, "COMPANIES_WO_ID.json", key, value)
                key_info = "%s\n%s" %(key_info, update_key_dict(keyfile_path, "CATEGORY.json", value, value_cat)   ) 
            else:
                logger.error(UNKNOWN_HELP)
                key_info = "%s \n %s" %(key_info, UNKNOWN_HELP)            
        else:
            warn = "Get not well formed email subject, regard keylen"
            logger.error(warn)
            key_info = "%s \n %s" %(key_info, warn)

        logger.info(key_info) 
        key_infos = "%s\n%s" %( key_info, key_infos)  
    return key_infos             


def get_mail(download_folder, config):
    '''tested'''
    subjects = []
    temp_img_folder = None  # Initialize to None

    imapSession = imaplib.IMAP4_SSL(config["IMAP_SERVER"])
    typ, accountDetails = imapSession.login(config["MAILUSER"], config["MAILPASS"])
    if typ != 'OK':
        logger.error('Not able to sign in!')
    else:
        logger.info("logged in")

    imapSession.select()
    typ, data = imapSession.search(None, "UnSeen")
    if typ != 'OK':
        logger.error('Error searching Inbox.')
        raise

    # Iterating over all emails
    logger.info("%s new mails" % len(data[0].split()))
    for msgId in data[0].split():
        typ, messageParts = imapSession.fetch(msgId, '(RFC822)')
        if typ != 'OK':
            logger.error('Error fetching mail.')
            raise
        emailBody = messageParts[0][1]
        mail = email.message_from_string(str(emailBody,'utf-8'))
        default_charset = 'ASCII'        
        emailSubject = decode_header(mail['subject'])[0][0]

        if "mattis" in mail['from'] or "myfritz.net" in mail['from']:      
            if str(emailSubject).startswith("#"):
                subjects.append(emailSubject)
            
            # Check if subject is 'tablet'
            is_tablet_subject = str(emailSubject).lower() == 'tablet'
            
            for part in mail.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                fileName = part.get_filename()
                if bool(fileName):
                    # Determine if file is an image
                    is_image = part.get_content_maintype() == 'image'
                    
                    # Create temp_img_folder only when needed
                    if is_tablet_subject and is_image and temp_img_folder is None:
                        temp_img_folder = os.path.join(download_folder, 'temp_images')
                        os.makedirs(temp_img_folder, exist_ok=True)
                    
                    # For tablet subject, only process images
                    if is_tablet_subject and not is_image:
                        continue
                    # For non-table subjects, only process PDFs
                    if not is_tablet_subject and not fileName.lower().endswith('.pdf'):
                        continue
                        
                    # Choose appropriate folder based on content type
                    if is_tablet_subject and is_image:
                        temp_path = os.path.join(temp_img_folder, fileName)
                        pictures_volume = config.get("PICTURES_VOLUME", download_folder)
                        logger.info("Using pictures volume: %s" % pictures_volume)
                        logger.info("Temp path: %s" % temp_path)
                        
                        os.makedirs(pictures_volume, exist_ok=True)
                        final_path = os.path.join(pictures_volume, fileName)
                        logger.info("Final path: %s" % final_path)
                        
                        if not os.path.isfile(final_path):
                            logger.info("Writing image to temp location")
                            with open(temp_path, 'wb') as fp:
                                fp.write(part.get_payload(decode=True))
                            logger.info("Moving image from %s to %s" % (temp_path, final_path))
                            shutil.move(temp_path, final_path)
                            logger.info("Successfully moved image to %s" % final_path)
                    else:
                        filePath = os.path.join(download_folder, fileName)
                        if not os.path.isfile(filePath):
                            logger.info("found new file %s" % fileName)
                            with open(filePath, 'wb') as fp:
                                fp.write(part.get_payload(decode=True))
                elif not emailSubject.startswith("#"):
                    warn = "$ got email without pdf and without command%s" %mail['subject']
                    logger.warning(warn)
                    subjects.append(warn)
        else:
            warn = "$ got email from unknown sender %s" %mail['from']
            logger.warning(warn)
            subjects.append(warn)
    imapSession.close()
    imapSession.logout()

    return subjects


def send_mail(content, subject, config, files=None):
    '''tested'''

    if content.replace("\n", "") or files:
        msg = MIMEMultipart()
        msg['From'] = config["MAILFROM"]
        msg['To'] = config["MAILTO"]
        #msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(content))

        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
                msg.attach(part)


        smtp = smtplib.SMTP(config["SMTP_SERVER"])
        smtp.login(config["MAILUSER"], config["MAILPASS"])
        smtp.sendmail(config["MAILFROM"], config["MAILTO"], msg.as_string())
        smtp.close()  
        return True 
    else:
        return False 