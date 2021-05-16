# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# Walk through directory tree, replacing all files with OCR'd version
# Contributed by DeliciousPickle@github


import logging
logger = logging.getLogger('root')
import os
import subprocess
import sys
pjoin = os.path.join
import time
import doc_mgnt_libs.read_pdf as read_pdf

def convert_jpg_to_pdf(filename_jpg,folder):
    fileending = filename_jpg.split(".")[-1]
    filename_pdf = filename_jpg.replace(fileending, "pdf")
    proc = subprocess.Popen(['convert',
                             pjoin(folder, filename_jpg), 
                             pjoin(folder, filename_pdf) ,
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
        logger.info("file successfully converted, try to rotate now")

    proc = subprocess.Popen(['convert',
                            '-rotate',
                            '90',
                             pjoin(folder,filename_pdf), 
                             pjoin(folder,filename_pdf),
                               ],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    proc.wait()
    result_err = repr(proc.stderr.readline())
    result = repr(proc.stdout.readlines())
    if result_err != "''":
        logger.error(result_err)
    else:
        logger.info("file successfully rotated")
    


def ocr(folder, config):
    '''tested'''

    #for filename in os.listdir(folder):
    #    if filename.lower().endswith(".jpg") or filename.lower().endswith("JPEG"):
    #        logger.info("%s: is jpeg file, coverting to pdf" %filename)
    #        convert_jpg_to_pdf(filename,folder)

    returns = sorted([])

    for filename in os.listdir(folder):
        if filename.endswith(".pdf") or filename.endswith(".PDF"):
            logger.debug("%s: checking if document has already text" %filename)
            out_file = pjoin(folder, "dummy.txt")
            test_content = read_pdf.get_text_from_pdf(pjoin(folder, filename))
            logger.debug(len(test_content))
            logger.debug(test_content)
            if len(test_content ) > 15:
                logger.info("%s: found already text in pdf. skippin ocr" %filename)
                returns.append(True)
                #return True
            elif config["OCR"] == "True":
                logger.info("%s: no text in pdf. doing ocr now" %filename)
                cmd = ["ocrmypdf",  "--deskew", "--tesseract-timeout", "1800", "-l", "deu" , pjoin(folder, filename) , pjoin(folder, filename) ]
                t_begin = time.time()
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                result = proc.stdout.read()
                t_end = time.time()
                if proc.returncode == 6:
                    logger.debug("%s: Skipped document because it already contained text" %filename)
                elif proc.returncode == 0:
                    logger.info("%s: OCR complete" %filename)
                logger.debug(result)
                logger.info("%s:ocr took %.1f seonds" % (filename, (t_end - t_begin)))
                returns.append(True)
                #return True
            else:
                returns.append(False)
                #return False
    return returns
