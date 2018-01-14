import logging
import os, shutil
import subprocess
from datetime import date
pjoin = os.path.join
from datetime import datetime
logger = logging.getLogger('root')

def save_files_local(copy_actions, logfile, local_output_folder):
    '''tested'''
    
    copy_actions[pjoin(local_output_folder, "logfiles", "logfile_%s.log" %datetime.strftime(datetime.now(), "%Y-%m-%d_%H"))] = logfile 
    for destination, source in copy_actions.iteritems():
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

def save_files_to_nas(local_output_folder, config):
    real_local_dir = "/tmp/digital_depot"
    if os.path.exists(real_local_dir):
        try:
            shutil.rmtree(real_local_dir)
        except OSError as exc: # Guard against race condition
            logger.error("could not remove old local dir")
            return False
    os.rename(local_output_folder, real_local_dir)
    ## changing permissions before copying to nas
    for your_dir in [real_local_dir]:
        for root, dirs, files in os.walk(your_dir):
            for d in dirs:
                logger.debug("changing dir permission %s" %d)
                os.chmod(os.path.join(root, d), 0777)
            for f in files:
                logger.debug("changing file permission %s" %f)
                os.chmod(os.path.join(root, f), 0777)

    proc = subprocess.Popen(['scp',
                            "-pr",
                            real_local_dir, 
                             "%s@%s:%s" % (config["NASUSER"], config["NASSERVER"], config["NASFOLDER"]),
                               ],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    proc.wait()
    result = repr(proc.stderr.readline())
    if result != "''":
        logger.error(result)
        return False
    else:
        logger.info("saved files succesfully on NAS") 
        return True   

def list_files_on_nas(config):
    proc = subprocess.Popen(['ssh',
                             '%s@%s'% (config["NASUSER"], config["NASSERVER"] ),
                             'ls' ,
                             config["NASFOLDER"]
                               ],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    proc.wait()
    result_err = repr(proc.stderr.readline())
    result = repr(proc.stdout.readlines())
    if result_err != "''":
        logger.error(result_err)
        return result_err
    else:
        logger.info("listed files succesfully on NAS") 
        return result   

def remove_folder_from_nas(config):
    proc = subprocess.Popen(['ssh',
                             '%s@%s'% (config["NASUSER"], config["NASSERVER"] ),
                             'rm' ,
                             '-rf',
                             config["NASFOLDER"]
                               ],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    proc.wait()
    result_err = repr(proc.stderr.readline())
    result = repr(proc.stdout.readlines())
    if result_err != "''":
        logger.error(result_err)
        return result_err
    else:
        logger.info("removed files succesfully on NAS") 
        return result  
