import logging
import os, shutil
import subprocess
from datetime import date
pjoin = os.path.join
from datetime import datetime
logger = logging.getLogger('root')


def check_scan_folder(tempfolder, config):
    for each in os.listdir(config["SCAN_INPUT"]):
        logger.info("move file %s from scan input to OCR folder " % each)
        os.rename(pjoin(config["SCAN_INPUT"],each), pjoin(tempfolder, each))



def save_files_local(copy_actions, logfile, local_output_folder):
    '''tested'''
    
    copy_actions[pjoin(local_output_folder, "logfiles", "logfile_%s.log" %datetime.strftime(datetime.now(), "%Y-%m-%d_%H"))] = logfile 
    for destination, source in copy_actions.items():
        logger.info("move file %s to NAS" % destination)

        if not os.path.exists(os.path.dirname(destination)):
            try:
                os.makedirs(os.path.dirname(destination))
            except OSError as exc: # Guard against race condition
                logger.error("could not create output folder")
                return False
        try:
            shutil.copy(source, destination)
        except IOError as e:
            logger.error("could not find file %s" %e)
    return True

def save_files_to_depot(local_output_folder, config):
    logger.debug("local output folder:%s" % local_output_folder)
    logger.debug("DIGITAL_DEPOTOLDER:%s" % config["DIGITAL_DEPOT"])

    shutil.copytree(local_output_folder, config["DIGITAL_DEPOT"], dirs_exist_ok=True)
