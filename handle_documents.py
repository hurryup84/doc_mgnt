# -*- coding: utf-8 -*-
import os
import shutil
import sys
import doc_mgnt_libs.mymail as mymail
import doc_mgnt_libs.read_pdf as read_pdf
import doc_mgnt_libs.ocr_pdf as ocr_pdf
import doc_mgnt_libs.nas as nas
import doc_mgnt_libs.log
from datetime import date
import json
import tempfile

pjoin = os.path.join
import locale
#locale.setlocale(locale.LC_ALL, 'de_DE.utf8')

tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt_tmp")
local_output_folder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt_lf")

logfile = pjoin(tempfolder, "hande_documents.log")
logger = doc_mgnt_libs.log.setup_custom_logger('root', logfile, "DEBUG", "w")

def main(arguments):

    if not len(arguments) == 2:
        print("usage:")
        print("python handle_documents.py absolute_path_to_config_folder")
        shutil.rmtree(tempfolder)    
        shutil.rmtree(local_output_folder)  
        
        return False
    else:
        keyfile_path = arguments[1]
        try:
            config = json.load(open(pjoin(keyfile_path, "config.json")))
        except IOError as e:
            logger.error("could not find configfile")
            logger.error(e)
            shutil.rmtree(tempfolder)    
            shutil.rmtree(local_output_folder)  
            return False
            
        subjects = mymail.get_mail(tempfolder, config)
        key_info = mymail.update_keys(subjects, keyfile_path)
        nas.check_scan_folder(tempfolder, config)
        ocr_pdf.ocr(tempfolder, config)
        copy_actions, mail_info, mail_info_path = read_pdf.analyse(tempfolder, local_output_folder, keyfile_path)
        nas.save_files_local(copy_actions, logfile, local_output_folder)
        nas.save_files_to_depot(local_output_folder, config)
        content = mymail.build_mail_content(key_info, mail_info, config, mail_info_path)
        event = mymail.send_mail(content, 'OCR Status %s' %date.today(), config)
        if event:
            nas.save_files_local(copy_actions, logfile, local_output_folder)
            nas.save_files_to_depot(local_output_folder, config)
        shutil.rmtree(tempfolder)    
        shutil.rmtree(local_output_folder)  
        return True

if __name__ == '__main__':
    main(sys.argv)
