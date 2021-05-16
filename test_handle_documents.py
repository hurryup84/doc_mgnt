# -*- coding: utf-8 -*-
import unittest
import handle_documents as handle_documents
import doc_mgnt_libs.mymail as mymail
import doc_mgnt_libs.ocr_pdf as ocr_pdf
import doc_mgnt_libs.read_pdf as read_pdf
import doc_mgnt_libs.nas as nas
from datetime import datetime
import os, shutil
import sys
import json
import time
import tempfile
import subprocess
import locale
#locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
pjoin = os.path.join
 

class Test_build_mail_content(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())
        self.path = os.path.abspath(".") 
        self.test_config = json.load(open(pjoin(self.path, "test_resources" , "main_test", "config.json")))
        pass

    def test_only_pdf(self):
        self.expected_string = "New PDFs stored\n\n category: test_category \n test_filename.pdf \n available at: \n %sdigital_depot/path/test_filename.pdf \n\n" %self.test_config["WEBDAV_PATH"]
        self.assertEqual( mymail.build_mail_content("", {"test_filename.pdf":"test_category"},self.test_config, {"test_filename.pdf":"path/test_filename.pdf"}), self.expected_string)

    def test_noting_to_mail(self):
        self.expected_string = ""
        self.assertEqual( mymail.build_mail_content("", {} ,self.test_config,), "")


    def test_only_key(self):
        self.expected_string = "Added new keys \nTestkeys"
        self.assertEqual( mymail.build_mail_content("Testkeys", "",self.test_config,), self.expected_string) 

    def test_key_and_pdf(self):
        self.expected_string_m = "New PDFs stored\n\n category: test_category \n test_filename.pdf \n available at: \n %sdigital_depot/path/test_filename.pdf \n\n" %self.test_config["WEBDAV_PATH"]
        self.expected_string_k = "Added new keys \nTestkeys"
        self.expected_string = "%s%s" %(self.expected_string_k, self.expected_string_m)
        self.assertEqual( mymail.build_mail_content("Testkeys", {"test_filename.pdf":"test_category"},self.test_config,{"test_filename.pdf":"path/test_filename.pdf"}), self.expected_string)

class Test_read_pdf(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())

        pass

        self.sample_text = "Hallo,dasisteinTestText.HierstehtdasDatum26.02.2017HieristeinkeyVericherungDiesisteineRechnungfürMaxMustermannMeineKundennummerist457689\x0c"
        self.lod_CAT = {"MeinFirma":"Firma_found", "dummycat":"dummycat_found" , "457689_found":"Vericherung_found"}
        self.lod_CWOID = {"eintesttext":"MeinFirma", "dummycwoid":"dummycwoid_found" }
        self.lod_CID = {"457689":"457689_found", "dummycid":"dummycid_found" }
        self.lod_DOC = {"rechnung":"RECHNUNG", "dummyr":"dummyr_found" } 
        self.lod_N = {"maxmustermann":"MaxMustermann_found", "dummyn":"dummyn_found" }
        self.lod_e = {"dummy":"dummy1", "lummy":"lummy2"}

    def test_search_in_content_good_sesult(self):
        self.lookup_dict = {"TestText":"TestText_found", "Hieristkey":"Hieristeinkey_found"}
        self.assertEqual(read_pdf.search_in_content("some text", self.lookup_dict, self.sample_text, "BAD"), "TestText_found")

    def test_search_in_content_bad_sesult(self):
        self.lookup_dict = {"TestsomeText":"TestText_found", "Hieristkey":"Hieristeinkey_found"}
        self.assertEqual(read_pdf.search_in_content("some text", self.lookup_dict, self.sample_text, "BAD"), "BAD")        

    def test_search_in_content_multiple_good_sesult(self):
        self.lookup_dict = {"TestText":"TestText_found", "Hieristeinkey":"Hieristeinkey_found"}
        self.assertEqual(read_pdf.search_in_content("some text", self.lookup_dict, self.sample_text, "BAD"), "Hieristeinkey_found")

    def test_analyse_content_max_found_items(self):
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[0],(["2017", "Firma_found"]) )
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][0],("2017-02-26") )        
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][1],("MaxMustermann_found") )  
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][2],("RECHNUNG") ) 
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][3][:2],("ID") ) 
        self.assertTrue(1000 <= int((read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][3][2:]  ) <= 999999)        
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][4],("MeinFirma") )  
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][5],("457689_found") )                                  
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[2],(["2017", "Vericherung_found"]))  

    def test_analyse_content_no_customer_id(self):
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_e, self.lod_DOC, self.lod_N))[0],(["2017", "Firma_found"]) )
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_e, self.lod_DOC, self.lod_N))[1][0],("2017-02-26") )        
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_e, self.lod_DOC, self.lod_N))[1][1],("MaxMustermann_found") )  
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_e, self.lod_DOC, self.lod_N))[1][2],("RECHNUNG") ) 
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_e, self.lod_DOC, self.lod_N))[1][3][:2],("ID") )
        self.assertTrue(1000 <= int((read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_e, self.lod_DOC, self.lod_N))[1][3][2:]) <= 999999)        
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_e, self.lod_DOC, self.lod_N))[1][4],("MeinFirma") )   
        self.assertEqual(len(        read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_e, self.lod_DOC, self.lod_N)[1]), 5) 
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_e, self.lod_DOC, self.lod_N))[2],([]) )                                        

    def test_analyse_content_no_cwoid(self):
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_e, self.lod_CID, self.lod_DOC, self.lod_N))[0],(["2017", "Vericherung_found"]) )
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_e, self.lod_CID, self.lod_DOC, self.lod_N))[1][0],("2017-02-26") )        
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_e, self.lod_CID, self.lod_DOC, self.lod_N))[1][1],("MaxMustermann_found") )  
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_e, self.lod_CID, self.lod_DOC, self.lod_N))[1][2],("RECHNUNG") ) 
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_e, self.lod_CID, self.lod_DOC, self.lod_N))[1][3][:2],("ID") ) 
        self.assertTrue(1000 <= int((read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_e, self.lod_CID, self.lod_DOC, self.lod_N))[1][3][2:]) <= 999999)        
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_e, self.lod_CID, self.lod_DOC, self.lod_N))[1][4],("457689_found") )  
        self.assertEqual(len(        read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_e, self.lod_CID, self.lod_DOC, self.lod_N)[1]), 5)
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_e, self.lod_CID, self.lod_DOC, self.lod_N))[2],([]) )  

    def test_analyse_content_no_cat(self):
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_e, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[0],(["2017", "UNDEFINED_CATEGORY"]) )
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_e, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][0],("2017-02-26") )        
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_e, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][1],("MaxMustermann_found") )  
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_e, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][2],("RECHNUNG") ) 
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_e, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][3][:2],("ID"))
        self.assertTrue(1000 <= int((read_pdf.analyse_content(self.sample_text, self.lod_e, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][3][2:]) <= 999999)        
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_e, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][4],("MeinFirma") )  
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_e, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[1][5],("457689_found") )                                  
        self.assertEqual(len(        read_pdf.analyse_content(self.sample_text, self.lod_e, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N)[1]), 6) 
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_e, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_N))[2],([]))

    def test_analyse_content_no_doc(self):
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_e, self.lod_N))[0],(["2017", "Firma_found"]) )
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_e, self.lod_N))[1][0],("2017-02-26") )        
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_e, self.lod_N))[1][1],("MaxMustermann_found") )  
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_e, self.lod_N))[1][2],("") ) 
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_e, self.lod_N))[1][3][:2],("ID") ) 
        self.assertTrue(1000 <= int((read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_e, self.lod_N))[1][3][2:]) <= 999999)        
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_e, self.lod_N))[1][4],("MeinFirma") )  
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_e, self.lod_N))[1][5],("457689_found") )                                  
        self.assertEqual(len(        read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_e, self.lod_N)[1]), 6) 
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_e, self.lod_N))[2],(["2017", "Vericherung_found"])) 

    def test_analyse_content_no_name(self):
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_e))[0],(["2017", "Firma_found"]) )
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_e))[1][0],("2017-02-26") )        
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_e))[1][1],("Familie") )  
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_e))[1][2],("RECHNUNG") ) 
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_e))[1][3][:2],("ID") ) 
        self.assertTrue(1000 <= int((read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_e))[1][3][2:]) <= 999999)        
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_e))[1][4],("MeinFirma") )  
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_e))[1][5],("457689_found") )                                  
        self.assertEqual(len(        read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_e)[1]), 6) 
        self.assertEqual((           read_pdf.analyse_content(self.sample_text, self.lod_CAT, self.lod_CWOID, self.lod_CID, self.lod_DOC, self.lod_e))[2],(["2017", "Vericherung_found"])) 

class Test_analyse(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())

        self.maxDiff = None
        self.tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.json_folder = pjoin(self.tempfolder, "main_test")
        self.ocr_folder = pjoin(self.tempfolder, "ocr_folder")
        self.output_folder = pjoin(self.tempfolder, "output_folder", "pdfs")
        if not os.path.exists(self.ocr_folder):
            os.makedirs(self.ocr_folder)        
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)  

        self.path = os.path.abspath(".") 
        shutil.copytree(pjoin(self.path, "test_resources", "main_test"), self.json_folder)
        self.pdf_with_simple_text = pjoin(self.ocr_folder, "sample_with.pdf") 
        self.pdf_with_simple_text_UC = pjoin(self.ocr_folder, "sample_with_UC.PDF") 
        self.pdf_with_simple_text_short = pjoin(self.ocr_folder,"sample_with_short.pdf") 
        #shutil.copy(pjoin(self.path,"test_resources/pdf_with_simple_text.pdf"),self.pdf_with_simple_text )       
        #shutil.copy(pjoin(self.path,"test_resources/pdf_with_simple_text_short.pdf"),self.pdf_with_simple_text_short )  
        self.path = os.path.abspath(".") 
        #print self.tempfolder
        self.unique = datetime.strftime(datetime.now(), "ID%m%d%H")
        self.expected_destination = pjoin(
            self.output_folder, 
            u"2017", 
            u"Firma_found", 
            u"2017-02-26_MaxMustermann_found_RECHNUNG_%s_MeinFirma_457689_found.pdf" %self.unique)        
        self.expected_destination2 = pjoin(
            self.output_folder, 
            u"2017", 
            u"Vericherung_found", 
            u"2017-02-26_MaxMustermann_found_RECHNUNG_%s_MeinFirma_457689_found.pdf" %self.unique)
        self.expected_destination3 = pjoin(
            self.output_folder, 
            "1984", 
            "UNDEFINED_CATEGORY", 
            "1984-01-01_Familie_%s.pdf" %self.unique)         

    def test_pdf_unknown_content_copy(self):
        shutil.copy(
            pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text_short.pdf"),
            self.pdf_with_simple_text_short )

        self.assertDictContainsSubset(
            ({self.expected_destination3:self.pdf_with_simple_text_short}), 
            (read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[0]))  

    def test_pdf_unknown_content_mail(self):
        shutil.copy(
            pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text_short.pdf"),
            self.pdf_with_simple_text_short )

        self.assertDictContainsSubset(
            ({'1984-01-01_Familie_%s.pdf' %self.unique: 'UNDEFINED_CATEGORY'}), 
            (read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[1]))                  

    def test_pdf_full_known_content_copy(self):
        shutil.copy(
            pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text.pdf"),
            self.pdf_with_simple_text )
        
        self.assertDictContainsSubset(
            ({self.expected_destination:self.pdf_with_simple_text}), 
            (read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[0]))
        
        self.assertDictContainsSubset(
            ({self.expected_destination2:self.pdf_with_simple_text}), 
            (read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[0])) 

    def test_pdf_full_known_content_copy_UC_PDF(self):
        shutil.copy(
            pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text.pdf"),
            self.pdf_with_simple_text_UC )
        
        self.assertDictContainsSubset(
            ({self.expected_destination:self.pdf_with_simple_text_UC}), 
            (read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[0]))
        
        self.assertDictContainsSubset(
            ({self.expected_destination2:self.pdf_with_simple_text_UC}), 
            (read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[0])) 
 
                      
    def test_pdf_full_known_content_mail(self):
        shutil.copy(
            pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text.pdf"),
            self.pdf_with_simple_text )
       
        self.assertDictContainsSubset(
            ({u'2017-02-26_MaxMustermann_found_RECHNUNG_%s_MeinFirma_457689_found.pdf' %self.unique:u'Firma_found and Vericherung_found'}), 
            (read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[1]))  

    def test_pdf_full_known_content_and_unknown_content_copy(self):
        shutil.copy(
            pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text.pdf"),
            self.pdf_with_simple_text )

        shutil.copy(
            pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text_short.pdf"),
            self.pdf_with_simple_text_short )        
        
               
        self.assertDictContainsSubset(
            ({self.expected_destination:self.pdf_with_simple_text}), 
            (read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[0]))
        
        self.assertDictContainsSubset(
            ({self.expected_destination2:self.pdf_with_simple_text}), 
            (read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[0])) 


        self.assertDictContainsSubset(
            ({self.expected_destination3:self.pdf_with_simple_text_short}), 
            (read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[0]))

    def test_pdf_full_known_content_and_unknown_content_mail(self):
            shutil.copy(
                pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text.pdf"),
                self.pdf_with_simple_text )

            shutil.copy(
                pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text_short.pdf"),
                self.pdf_with_simple_text_short )        
                    

            self.assertDictContainsSubset(
                ({u'2017-02-26_MaxMustermann_found_RECHNUNG_%s_MeinFirma_457689_found.pdf'%self.unique:u'Firma_found and Vericherung_found'}), 
                (read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[1]))  

            self.assertDictContainsSubset(
                ({'1984-01-01_Familie_%s.pdf' %self.unique: 'UNDEFINED_CATEGORY'}), 
                (read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[1] ))                                


    def test_pdf_not_in_folder_copy(self):

            self.assertEqual(
                (0), 
                (len(read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[0])))  

    def test_pdf_not_in_folder_mail(self):
            self.assertEqual(
                (0), 
                (len(read_pdf.analyse(self.ocr_folder, self.output_folder, self.json_folder)[1])))
    def tearDown(self):
        try:
            shutil.rmtree(self.tempfolder)
            #print "removed %s" % self.tempfolder
        except OSError as why:
            print(why)

class Test_search_date(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())

        self.expected_date = datetime.strptime("04-05-2017", "%d-%m-%Y").date()
        self.expected_date2 = datetime.strptime("01-04-2019", "%d-%m-%Y").date()
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())
       # import pdb; pdb.set_trace()
        pass

    def test_search_date1(self):
        content = "jfeiwojfiwej04-05-2017pokrgporek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date)


    def test_search_date2(self):
        content = "jfeiwojfiwej04.05.17pokrgporek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date)

    def test_search_date3(self):
        content = "jfeiwojfiwej04-Mai-2017pokrgporek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date)

    def test_search_date4(self):
        content = "jfeiwojfiwej04Mai2017pokrgporek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date)

    def test_search_date5(self):
        content = "jfeiwojfiwej04.Mai2017pokrgporek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date)

    def test_search_date6(self):
        content = "jfeiwojfiwej04052017pokrgporek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date)

    def test_search_date7(self):
        content = "jfeiwojfiwejpokrgporek"
        self.assertEqual(read_pdf.search_for_date(content), datetime.strptime("01-01-1984", "%d-%m-%Y").date())

    def test_search_date8(self):
        content = "jfeiwojfiwej01-04-19pokrgporek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date2)

    def test_search_date9(self):
        content = "jfeiwojfiwej04-05-2017pokrgp04-03-17orek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date)

    def test_search_date10(self):
        content = "jfeiwojfiwej04-05-2017pokr040617gporek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date)

    def test_search_date11(self):
        content = "jfeiwojfiwej04-05-2017pokrgFebruar2017porek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date)

    def test_search_date12(self):
        content = "jfeiwojfiwej04-13-2017pokrgporek"
        self.assertEqual(read_pdf.search_for_date(content), datetime.strptime("01-01-1984", "%d-%m-%Y").date())                                                                                        

    def test_search_date13(self):
        content = "jfeiwojfiwej04-05-2017pokr01-01-2017gporek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date)                                                                                        

    def test_search_date14(self):
        content = "jfeiwojfiwej04-05-2017pokr31-12-2017gporek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date) 

    def test_search_date15(self):
        content = "jfeiwojkr31-12-2017gfiwej04-05-2017pokr01-01-2017gporek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date) 

    def test_search_date16(self):
        content = "jfeiwojkr04 . 0 5 . 201 7gfiwepokr01-01-2017gporek"
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date)

    def test_search_date17(self):
        content = """3storf01.04.19AA/150/a_c-fe13.03.1935.2"""
        self.assertEqual(read_pdf.search_for_date(content), self.expected_date2)



class Test_new_scanned_files(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())

        self.path = os.path.abspath(".") 
        self.test_file = pjoin(self.path, "test_resources" , "pdfs", "pdf_with_simple_text.pdf") 
        self.test_file_short = pjoin(self.path, "test_resources" , "pdfs", "pdf_with_simple_text_short.pdf") 
        self.tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.tempfolder_dd = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.tempfolder_si = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.test_config = json.load(open(pjoin(self.path, "test_resources" , "nas_test", "user1.json")))
        self.test_config["DIGITAL_DEPOT"] = self.tempfolder_dd
        self.test_config["SCAN_INPUT"] = self.tempfolder_si

        shutil.copy(self.test_file,pjoin(self.tempfolder, self.test_config["SCAN_INPUT"]))
        shutil.copy(self.test_file_short,pjoin(self.tempfolder, self.test_config["SCAN_INPUT"]))
        pass


    def test_new_scanned_files(self):
        nas.check_scan_folder(self.tempfolder, self.test_config)

        self.assertEqual(str(os.listdir(self.tempfolder)), "['pdf_with_simple_text_short.pdf', 'pdf_with_simple_text.pdf']")
        self.assertEqual(str(os.listdir(self.test_config["SCAN_INPUT"])), "[]")

    def tearDown(self):
        try:
            shutil.rmtree(self.tempfolder)
            shutil.rmtree(self.tempfolder_dd)
            shutil.rmtree(self.tempfolder_si)
            #print "removed %s" % self.tempfolder
        except OSError as why:
            print(why)


class Test_send_mail_key(unittest.TestCase):
    def setUp(self): 
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())
        self.path = os.path.abspath(".") 
        self.tempfolder_dd = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.orig_config = json.load(open(pjoin(self.path, "test_resources" , "mail_test", "user2.json")))

        self.test_config = json.load(open(pjoin(self.path, "test_resources" , "mail_test", "user1.json")))
        self.test_config["DIGITAL_DEPOT"] = self.tempfolder_dd

        self.tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")

    def test_sending_one_pdf_mail(self):
        self.path = os.path.abspath(".") 
        self.test_file = pjoin(self.path, "test_resources" , "pdfs", "pdf_with_simple_text.pdf") 
        self.assertEqual(mymail.send_mail("content", "to_be_ocred", self.orig_config, [self.test_file]), True)
        time.sleep(1)
        mymail.get_mail(self.tempfolder,self.test_config)
        self.assertEqual(["pdf_with_simple_text.pdf"], os.listdir(self.tempfolder))

    def test_sending_one_pdf_mail(self):
        self.path = os.path.abspath(".") 
        self.test_file = pjoin(self.path, "test_resources" , "pdfs", "pdf_with_simple_text.pdf") 
        self.test_file2 = pjoin(self.path, "test_resources" , "pdfs", "pdf_without_simple_text.pdf") 
        mymail.send_mail("content", "to_be_ocred", self.orig_config, [self.test_file])
        mymail.send_mail("content", "to_be_ocred", self.orig_config, [self.test_file2]) 
        time.sleep(1)
        mymail.get_mail(self.tempfolder,self.test_config)
        self.assertEqual(sorted(["pdf_with_simple_text.pdf", "pdf_without_simple_text.pdf"]), sorted(os.listdir(self.tempfolder)))

    def test_sending_key_mails(self):
        self.assertEqual(mymail.send_mail("Testcontent", "#Testsubject", self.orig_config), True)
        mymail.send_mail("Testcontent", "#Testsubject2", self.orig_config)
        time.sleep(1)
        self.assertEqual(sorted(mymail.get_mail(self.tempfolder,self.test_config)), sorted([u"#Testsubject",u"#Testsubject2" ]))

    def test_sending_key_mails_one_without(self):
        mymail.send_mail("Testcontent", "Testsubject", self.orig_config)
        mymail.send_mail("Testcontent", "#Testsubject2", self.orig_config)
        time.sleep(1)
        self.assertEqual(sorted(mymail.get_mail(self.tempfolder,self.test_config)), sorted([u"#Testsubject2" ]))

    def test_sending_key_mails_all_without(self):
        self.assertEqual(mymail.send_mail("", "Testsubject", self.orig_config), False)

    def tearDown(self):
        try:
            shutil.rmtree(self.tempfolder)
            shutil.rmtree(self.tempfolder_dd)
            #print "removed %s" % self.tempfolder
        except OSError as why:
            print(why)



class Test_save_files_local(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())

        self.tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.source_folder = pjoin(self.tempfolder, "source")
        self.dest_folder = pjoin(self.tempfolder, "dest")
        self.path = os.path.abspath(".") 
        self.logfile = pjoin(self.path, "test_resources", "logfile.log")
        shutil.copytree(pjoin(self.path, "test_resources", "pdfs"), self.source_folder)


    def test_copy_all_files(self):
        self.src_files = os.listdir( self.source_folder )
        copy_dict = {}
        for file_ in self.src_files:
            copy_dict[pjoin(self.dest_folder, file_)] = pjoin(self.source_folder, file_)
        self.assertEqual(nas.save_files_local(copy_dict, self.logfile, self.dest_folder), True  )
        self.dst_files = os.listdir( self.dest_folder )
        #self.src_files.append("logfile_%s.log" %datetime.strftime(datetime.now(), "%Y-%m-%d_%H"))
        self.expected_files = self.src_files
        self.expected_files.append("logfiles")

        self.assertEqual(sorted(self.dst_files), sorted(self.expected_files) )     

    def test_copy_all_files_some_duplicated(self):
        self.src_files = os.listdir( self.source_folder )
        copy_dict = {}
        for file_ in self.src_files:
            copy_dict[pjoin(self.dest_folder, file_)]= pjoin(self.source_folder, file_)
        copy_dict[pjoin(self.dest_folder, "duplicated.pdf")] = pjoin(self.source_folder, self.src_files[0])
        self.assertEqual(nas.save_files_local(copy_dict, self.logfile, self.dest_folder), True  )
        self.dst_files = os.listdir( self.dest_folder )
        #self.src_files.append("logfile_%s.log" %datetime.strftime(datetime.now(), "%Y-%m-%d_%H"))
        self.expected_files = self.src_files
        self.expected_files.append("logfiles")
        self.expected_files.append("duplicated.pdf")

        self.assertEqual(sorted(self.dst_files), sorted(self.expected_files) )             




    def tearDown(self):
        try:
            shutil.rmtree(self.tempfolder)
            #print "removed %s" % self.tempfolder
        except OSError as why:
            print(why)

class Test_update_keys(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())

        self.tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.json_folder = pjoin(self.tempfolder, "main_test")
        self.path = os.path.abspath(".") 
        shutil.copytree(pjoin(self.path, "test_resources", "main_test"), self.json_folder)


    
    def test_cwoid(self):
        self.assertEqual(mymail.update_keys(["#CWOID new_search_string new_company"], self.json_folder), "updated COMPANIES_WO_ID.json with \n new_search_string : new_company\n")
        self.assertEqual(mymail.update_keys(["#cwoid new_search_string new_company"], self.json_folder), "updated COMPANIES_WO_ID.json with \n new_search_string : new_company\n")

    def test_cid(self):
        self.assertEqual(mymail.update_keys(["#CID new_search_string new_company"], self.json_folder), "updated CUSTOMER_ID.json with \n new_search_string : new_company\n")
        self.assertEqual(mymail.update_keys(["#cid new_search_string new_company"], self.json_folder), "updated CUSTOMER_ID.json with \n new_search_string : new_company\n")

    def test_cat(self):
        self.assertEqual(mymail.update_keys(["#CAT new_search_string new_company"], self.json_folder), "updated CATEGORY.json with \n new_search_string : new_company\n")
        self.assertEqual(mymail.update_keys(["#cat new_search_string new_company"], self.json_folder), "updated CATEGORY.json with \n new_search_string : new_company\n")

    def test_doc(self):
        self.assertEqual(mymail.update_keys(["#DOC new_search_string new_company"], self.json_folder), "updated DOCTYPES.json with \n new_search_string : new_company\n")
        self.assertEqual(mymail.update_keys(["#doc new_search_string new_company"], self.json_folder), "updated DOCTYPES.json with \n new_search_string : new_company\n")

    def test_name(self):
        self.assertEqual(mymail.update_keys(["#NAME new_search_string new_company"], self.json_folder), "updated NAMES.json with \n new_search_string : new_company\n")
        self.assertEqual(mymail.update_keys(["#name new_search_string new_company"], self.json_folder), "updated NAMES.json with \n new_search_string : new_company\n")

    def test_cwoidcat(self):
        self.assertEqual(mymail.update_keys(["#CWOIDCAT new_search_string new_company new_category"], self.json_folder), "updated COMPANIES_WO_ID.json with \n new_search_string : new_company\nupdated CATEGORY.json with \n new_company : new_category\n")
        self.assertEqual(mymail.update_keys(["#cwoidcat new_search_string new_company new_category"], self.json_folder), "updated COMPANIES_WO_ID.json with \n new_search_string : new_company\nupdated CATEGORY.json with \n new_company : new_category\n")

    def test_cidcat(self):
        self.assertEqual(mymail.update_keys(["#CIDCAT new_search_string new_company new_category"], self.json_folder), "updated CUSTOMER_ID.json with \n new_search_string : new_company\nupdated CATEGORY.json with \n new_company : new_category\n")
        self.assertEqual(mymail.update_keys(["#cidcat new_search_string new_company new_category"], self.json_folder), "updated CUSTOMER_ID.json with \n new_search_string : new_company\nupdated CATEGORY.json with \n new_company : new_category\n")

    def test_cidcat_no_hash(self):
        self.assertEqual(mymail.update_keys(["CIDCAT new_search_string new_company new_category"], self.json_folder), """ \n could not identify keyword, please use one of #CAT #CID #CWOID #DOC #NAME #CIDCAT #CWOIDCAT\n""")
        self.assertEqual(mymail.update_keys(["cidcat new_search_string new_company new_category"], self.json_folder), """ \n could not identify keyword, please use one of #CAT #CID #CWOID #DOC #NAME #CIDCAT #CWOIDCAT\n""")
  
    def test_cid_and_cat(self):
        self.assertEqual(mymail.update_keys(["#CID new_search_string new_company", "#CAT new_search_string new_company"], self.json_folder), "updated CATEGORY.json with \n new_search_string : new_company\nupdated CUSTOMER_ID.json with \n new_search_string : new_company\n")
        self.assertEqual(mymail.update_keys(["#cid new_search_string new_company", "#cat new_search_string new_company"], self.json_folder), "updated CATEGORY.json with \n new_search_string : new_company\nupdated CUSTOMER_ID.json with \n new_search_string : new_company\n")

    def test_unknown(self):
        self.assertEqual(mymail.update_keys(["#CWID new_search_string new_company"], self.json_folder), """ \n could not identify keyword, please use one of #CAT #CID #CWOID #DOC #NAME #CIDCAT #CWOIDCAT\n""")

    def test_unknown2(self):
        self.assertEqual(mymail.update_keys(["#CWID new_search_string new_company sometjing_else"], self.json_folder), """ \n could not identify keyword, please use one of #CAT #CID #CWOID #DOC #NAME #CIDCAT #CWOIDCAT\n""")



    def tearDown(self):
        try:
            shutil.rmtree(self.tempfolder)
            #print "removed %s" % self.tempfolder
        except OSError as why:
            print(why)

class Test_handle_subjects(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())

        self.tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.json_folder = pjoin(self.tempfolder, "main_test")
        self.path = os.path.abspath(".") 
        shutil.copytree(pjoin(self.path, "test_resources", "main_test"), self.json_folder)

    
    def tearDown(self):
        try:
            shutil.rmtree(self.tempfolder)
            #print "removed %s" % self.tempfolder
        except OSError as why:
            print(why)




class Test_ocr_pdf(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())

        self.tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.config = {"OCR":"False"}
        self.pdf_without_simple_text = pjoin(self.tempfolder, "sample_without.pdf")
        self.pdf_without_simple_text_short = pjoin(self.tempfolder,  "sample_without_short.pdf")  
            
        self.path = os.path.abspath(".") 
        pass 

    def test_pdf_with_simple_text_without_ocr(self):
        shutil.copy(pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text.pdf"),self.pdf_without_simple_text )
        ocr_feature = ocr_pdf.ocr(self.tempfolder,self.config)
        if self.config["OCR"] == "True":
            test_content = read_pdf.get_text_from_pdf(self.pdf_without_simple_text)
            self.expected_string = "Hallo,dasisteinTestText.HierstehtdasDatum26.02.2017HieristeinkeyVericherungDiesisteineRechnungfürMaxMustermannMeineKundennummerist457689\x0c"
            self.assertEqual(test_content, self.expected_string)
        else:
            self.assertEqual(ocr_feature, [True])

    def test_pdf_with_simple_text_with_ocr(self):
        shutil.copy(pjoin(self.path,"test_resources/pdfs/pdf_without_simple_text.pdf"),self.pdf_without_simple_text )
        ocr_feature =ocr_pdf.ocr(self.tempfolder,self.config)
        if self.config["OCR"] == "True":
            test_content = read_pdf.get_text_from_pdf(self.pdf_without_simple_text)
            self.expected_string = "Hallo,dasisteinTestText.HierstehtdasDatum26.02.2017HieristeinkeyVericherungDiesisteineRechnungfürMaxMustermannMeineKundennummerist457689\x0c"
            self.assertEqual(test_content, self.expected_string) 
        else:
            self.assertEqual(ocr_feature, [False])  
         

    def test_pdf_with_simple_text_without_ocr_multiple_files(self):
        shutil.copy(pjoin(self.path,"test_resources/pdfs/pdf_without_simple_text.pdf"),self.pdf_without_simple_text )
        shutil.copy(pjoin(self.path,"test_resources/pdfs/pdf_without_simple_text_short.pdf"),self.pdf_without_simple_text_short )        
        ocr_feature= ocr_pdf.ocr(self.tempfolder,self.config)
        if self.config["OCR"] == "True":  
            test_content = read_pdf.get_text_from_pdf(self.pdf_without_simple_text)  
            self.expected_string = "Hallo,dasisteinTestText.HierstehtdasDatum26.02.2017HieristeinkeyVericherungDiesisteineRechnungfürMaxMustermannMeineKundennummerist457689\x0c"
            self.assertEqual(test_content, self.expected_string)
            test_content_short = read_pdf.get_text_from_pdf(self.pdf_without_simple_text_short)  
            self.expected_string_short = "DiesisteinzweiternichtsolangerBeispieltext\x0c"  
            self.assertEqual(test_content_short, self.expected_string_short)  
        else:
            self.assertEqual(ocr_feature, [False, False])  

              
    def test_pdf_with_simple_text_with_and_without_ocr_multiple_files(self):
        shutil.copy(pjoin(self.path,"test_resources/pdfs/pdf_without_simple_text.pdf"),self.pdf_without_simple_text )
        shutil.copy(pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text_short.pdf"),self.pdf_without_simple_text_short )        
        ocr_feature = ocr_pdf.ocr(self.tempfolder,self.config)
        if self.config["OCR"] == "True":  
            test_content = read_pdf.get_text_from_pdf(self.pdf_without_simple_text)  
            self.expected_string = "Hallo,dasisteinTestText.HierstehtdasDatum26.02.2017HieristeinkeyVericherungDiesisteineRechnungfürMaxMustermannMeineKundennummerist457689\x0c"
            self.assertEqual(test_content, self.expected_string)
            test_content_short = read_pdf._from_pdf(self.pdf_with_simple_text_short)
            self.expected_string_short = "DiesisteinzweiternichtsolangerBeispieltext\x0c" 
        else:
            self.assertEqual(ocr_feature, [True, False])   

    def tearDown(self):
        try:
            shutil.rmtree(self.tempfolder)
            #print "removed %s" % self.tempfolder
        except OSError as why:
            print(why)


class Test_ocr_not_supported_pdf(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())
        self.config = {"OCR":"False"}
        self.tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.pdf_with_simple_text = pjoin(self.tempfolder, "sample_with.pdf") 
        self.pdf_without_simple_text = pjoin(self.tempfolder, "sample_without.pdf")
        self.pdf_with_simple_text_short = pjoin(self.tempfolder,  "sample_with_short.pdf")       
        self.path = os.path.abspath(".") 
        pass

    def test_pdf_with_simple_text_without_ocr_can_not_do_ocr(self):
        shutil.copy(pjoin(self.path,"test_resources/pdfs/pdf_without_simple_text.pdf"),self.pdf_without_simple_text )
        self.assertEqual([False], ocr_pdf.ocr(self.tempfolder,self.config))

    def test_pdf_with_simple_text_with_ocr_can_not_do_ocr(self):
        shutil.copy(pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text.pdf"),self.pdf_with_simple_text )
        self.assertEqual([True], ocr_pdf.ocr(self.tempfolder,self.config)) 
        test_content = read_pdf.get_text_from_pdf(self.pdf_with_simple_text)
        self.expected_string = "Hallo,dasisteinTestText.HierstehtdasDatum26.02.2017HieristeinkeyVericherungDiesisteineRechnungfürMaxMustermannMeineKundennummerist457689\x0c"
        self.assertEqual(test_content, self.expected_string) 
          


    def tearDown(self):
        try:
            shutil.rmtree(self.tempfolder)
            #print "removed %s" % self.tempfolder
        except OSError as why:
            print(why)



class Test_ocr_jpeg_pdf(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())
        self.config = {"OCR":"True"}
        self.tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.jpeg_with_simple_text = pjoin(self.tempfolder,  "sample_jpeg_with_short.jpg")       
        self.path = os.path.abspath(".") 
        pass

    def test_jpeg_with_simple_text_with_ocr(self):
        shutil.copy(pjoin(self.path,"test_resources/jpegs/geheim.JPG"),self.jpeg_with_simple_text )
        ocr_pdf.ocr(self.tempfolder, self.config)
        test_content = read_pdf.get_text_from_jpeg(self.jpeg_with_simple_text)
        self.expected_string = "geheimzuhalten\x0c"
        self.assertEqual(test_content, "not implemented")  

    def tearDown(self):
        try:
            shutil.rmtree(self.tempfolder)
            #print "removed %s" % self.tempfolder
        except OSError as why:
            print(why)


class Test_ocr_jpeg_and_pdf(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())
        self.config = {"OCR":"True"}
        self.tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.jpeg_with_simple_text = pjoin(self.tempfolder,  "sample_jpeg_with_short.jpg")   
        self.pdf_with_simple_text = pjoin(self.tempfolder,  "sample_with_short.pdf")    
        self.path = os.path.abspath(".") 
        pass

    def test_jpeg_and_pdf_with_simple_text_with_ocr(self):
        shutil.copy(pjoin(self.path,"test_resources/jpegs/geheim.JPG"),self.jpeg_with_simple_text )
        shutil.copy(pjoin(self.path,"test_resources/pdfs/pdf_with_simple_text.pdf"),self.pdf_with_simple_text )
        ocr_pdf.ocr(self.tempfolder, self.config)
        test_content = read_pdf.get_text_from_pdf(self.pdf_with_simple_text)
        self.expected_string = "Hallo,dasisteinTestText.HierstehtdasDatum26.02.2017HieristeinkeyVericherungDiesisteineRechnungfürMaxMustermannMeineKundennummerist457689\x0c"
        self.assertEqual(test_content, self.expected_string)  

    def tearDown(self):
        try:
            shutil.rmtree(self.tempfolder)
            #print "removed %s" % self.tempfolder
        except OSError as why:
            print(why)





class Test_update_key_dict(unittest.TestCase):
    def setUp(self):
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())

        import tempfile

        self.tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.test_dict = {"test_key": "test_value"}
        json.dump(self.test_dict, open(pjoin(self.tempfolder, "test_key.txt"),'w'),  ensure_ascii=False)        
        json.dump(self.test_dict, open(pjoin(self.tempfolder, "test_key_untouch.txt"),'w'), ensure_ascii=False)         
        json.dump(self.test_dict, open(pjoin(self.tempfolder, "test_key_umlaut.txt"),'w'),  ensure_ascii=False)          
        pass

    def test_category_add(self):
        self.keys = json.load(open(pjoin(self.tempfolder, "test_key.txt")))
        mymail.update_key_dict(self.tempfolder, "test_key.txt", "new_key", "new_value")
        self.expected_dict = {"test_key":"test_value", "new_key":"new_value"}
        self.assertDictContainsSubset(json.load(open(pjoin(self.tempfolder, "test_key.txt"))), self.expected_dict)

    def test_category_add_umlaut_value(self):
        self.keys = json.load(open(pjoin(self.tempfolder, "test_key_umlaut.txt")))
        mymail.update_key_dict(self.tempfolder, "test_key_umlaut.txt", "new_key_with", "new_value_withä")
        self.expected_dict = {"test_key":"test_value", "new_key_with":"new_value_withä"}
        loaded_dict = json.load(open(pjoin(self.tempfolder, "test_key_umlaut.txt")))
        self.assertEqual(loaded_dict["new_key_with"], self.expected_dict["new_key_with"])
        self.assertDictContainsSubset(json.load(open(pjoin(self.tempfolder, "test_key_umlaut.txt"))), self.expected_dict)

    def test_category_add_umlaut_key(self):
        self.keys = json.load(open(pjoin(self.tempfolder, "test_key_umlaut.txt")))
        mymail.update_key_dict(self.tempfolder, "test_key_umlaut.txt", "new_key_withä", "new_value_with")
        self.expected_dict = {"test_key":"test_value", "new_key_withä" :"new_value_with"}
        loaded_dict = json.load(open(pjoin(self.tempfolder, "test_key_umlaut.txt")))
        self.assertEqual(loaded_dict["new_key_withä"], self.expected_dict["new_key_withä"])
        self.assertDictContainsSubset(json.load(open(pjoin(self.tempfolder, "test_key_umlaut.txt"))), self.expected_dict)        


    def test_category_not_add(self):
        self.keys = json.load(open(pjoin(self.tempfolder, "test_key.txt")))
        mymail.update_key_dict(self.tempfolder, "test_key_untouch.txt", "new_key", "new_value")
        self.expected_dict = {"test_key":"test_value"}
        self.assertDictContainsSubset(json.load(open(pjoin(self.tempfolder, "test_key.txt"))), self.expected_dict)        

    def tearDown(self):
        try:
            shutil.rmtree(self.tempfolder)
            #print "removed %s" % self.tempfolder
        except OSError as why:
            print(why)



class Test_handle_documents_main(unittest.TestCase):
    def setUp(self): 
        print("------------------------------------------------------------")
        print("Executing :%s" %self.id())
        self.path = os.path.abspath(".") 
        self.orig_config = json.load(open(pjoin(self.path, "test_resources" , "main_test", "config.json")))
        self.tempfolder = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt")
        self.tempfolder_dd = tempfile.mkdtemp(dir="/tmp", prefix="doc_mgnt_dd")
        self.orig_config["DIGITAL_DEPOT"] = self.tempfolder_dd
        pass

    #def test_main_no_config_path(self):
    #    self.assertEqual(handle_documents.main(["handle_documents.py"]), False)
#
 #   def test_main_wrong_config_path(self):
  #      self.assertEqual(handle_documents.main(["handle_documents.py", "/tmp/"]), False)

    def test_main_with_key_and_pdf_mail(self):
        self.path = os.path.abspath(".") 
        self.test_file = pjoin(self.path, "test_resources" , "pdfs", "pdf_with_simple_text.pdf") 
        self.test_file_short = pjoin(self.path, "test_resources" , "pdfs", "pdf_with_simple_text_short.pdf") 
        self.config_path = pjoin(self.path, "test_resources" , "main_test")
        #pre_state = nas.list_files_on_nas(self.orig_config).split("\n")
        mymail.send_mail("content", "to_be_ocred", self.orig_config, [self.test_file])
        mymail.send_mail("Testcontent", "#Testsubject", self.orig_config)
        shutil.copy(self.test_file_short,pjoin(self.tempfolder, self.orig_config["SCAN_INPUT"]))
        self.assertEqual(handle_documents.main(["handle_documents.py", self.config_path]), True)

 
    def tearDown(self):
        try:
            shutil.rmtree(self.tempfolder)
            shutil.rmtree(self.tempfolder_dd)
            #print "removed %s" % self.tempfolder
        except OSError as why:
            print(why)
if __name__ == '__main__':
   # unittest.main()

    fast = unittest.TestSuite()
    fast.addTest(unittest.makeSuite(Test_build_mail_content))
    fast.addTest(unittest.makeSuite(Test_read_pdf))
    fast.addTest(unittest.makeSuite(Test_analyse))
    fast.addTest(unittest.makeSuite(Test_search_date))

    fast.addTest(unittest.makeSuite(Test_save_files_local))
    fast.addTest(unittest.makeSuite(Test_update_keys))
    fast.addTest(unittest.makeSuite(Test_handle_subjects))
    fast.addTest(unittest.makeSuite(Test_update_key_dict))

    

    slow = unittest.TestSuite()
    slow.addTest(unittest.makeSuite(Test_ocr_pdf))
    slow.addTest(unittest.makeSuite(Test_ocr_jpeg_and_pdf))
    slow.addTest(unittest.makeSuite(Test_ocr_jpeg_pdf))  
    slow.addTest(unittest.makeSuite(Test_new_scanned_files))
    slow.addTest(unittest.makeSuite(Test_ocr_not_supported_pdf))
    slow.addTest(unittest.makeSuite(Test_send_mail_key))
    slow.addTest(unittest.makeSuite(Test_handle_documents_main))


    if len(sys.argv) == 2:
        try:
            suite = eval(sys.argv[1])
            unittest.TextTestRunner().run(suite)
        except NameError as e:
            print( "please give valid test plan")
            print("%s fast (to run only fast tests)" % sys.argv[0])
            print("%s slow (to run only slow tests, including OCR, Mailcheck etc.)" % sys.argv[0])
            print("%s      (to run all test)" % sys.argv[0])
    else:
        unittest.TextTestRunner().run(eval("fast"))
        unittest.TextTestRunner().run(eval("slow"))

