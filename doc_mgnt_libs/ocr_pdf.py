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
import locale
locale.setlocale(locale.LC_ALL, 'de_DE.utf8')


def ocr(folder):
    '''tested'''

    for filename in os.listdir(folder):
        if filename.endswith(".pdf") or filename.endswith(".PDF"):
            new_filename = "%s.pdf" % filename.split(".")[0]
            logger.debug("%s: checking if has already text" %filename)
            out_file = pjoin(folder, "dummy.txt")
            subprocess.call(['pdftotext', pjoin(folder, filename), out_file])
            with open(out_file, 'r') as myfile:
                test_content=myfile.read().replace('\n', '').replace(" ", "")
            if len(test_content ) > 13:
                logger.info("%s: found already text in pdf. skippin ocr" %filename)
            else:
                logger.info("%s: no text in pdf. doing ocr now" %filename)
                cmd = ["ocrmypdf",  "--deskew", "--tesseract-timeout", "1800", "-l", "deu" , pjoin(folder, filename) , pjoin(folder, new_filename) ]
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
