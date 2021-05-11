# -*- coding: iso-8859-1 -*-
import shutil
import re
import os
from datetime import datetime
from datetime import date
pjoin = os.path.join
import subprocess
from random import randint
import json

#import mymail as mymail
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.converter import TextConverter
import io

import logging
logger = logging.getLogger('root')

import locale
try:
	locale.setlocale(locale.LC_ALL, 'de_DE')
except locale.Error as e:
	logger.error("Please set system locale")
	logger.error("Script is using %s %s as locale" % locale.getlocale())


def search_in_content(lookup_type, lookup_dict, content, bad_return):
	'''tested'''
	findings = []
	for key in lookup_dict.keys():
		if key in content:
			logger.debug("searched for: %s found: %s" %(lookup_type, lookup_dict[key]))	
			findings.append(key)
			#return lookup_dict[key]
	logger.warning("could not find a match for %s" % lookup_type)
	if len(findings) > 0:
		return lookup_dict[sorted(findings)[0]]
	else:
		return bad_return


def pdeudounique():
	return datetime.strftime(datetime.now(), "ID%m%d%H")


def analyse_content(content,CATEGORY,COMPANIES_WO_ID , CUSTOMER_ID, DOCTYPES, NAMES):
	'''tested'''
	lcontent = content.lower()

	found_date = search_for_date(content)
	year = found_date.strftime("%Y")
	date = found_date.strftime("%Y-%m-%d")

	
	company_id = search_in_content("Company by ID", CUSTOMER_ID, lcontent, "UNDEFINED_CUSTOMER_ID")
	doctype = search_in_content("Document type", DOCTYPES, lcontent, "")
	name = search_in_content("Names", NAMES, lcontent, "Familie" )
	company = search_in_content("Company without ID", COMPANIES_WO_ID, lcontent, "UNDEFINED_COMPANY" )

	#if company == "UNDEFINED_COMPANY" and company_id != "UNDEFINED_CUSTOMER_ID":
	#	company = company_id


	try:
		category = CATEGORY[company]
	except KeyError:
		category = "UNDEFINED_CATEGORY"
		logger.warning("%s not in categories" % company)

	try:
		category2 = CATEGORY[company_id]
	except KeyError:
		category2 = "UNDEFINED_CATEGORY"
		logger.warning("%s not in categories" % company_id)


	unique = pdeudounique()
	filename = sorted([])
	#filename = filename + [date] 
	filename = filename + [date, name, doctype, "%s" % unique] 

	if company != "UNDEFINED_COMPANY":
		filename.append(company)

	# The company can also be identified by an ID. If the ID does not eqal the name of the compayn, we should add it to the filename
	if company != company_id:
		if company_id != "UNDEFINED_CUSTOMER_ID":
			filename.append(company_id)	
	
	if company == "UNDEFINED_COMPANY" and company == "UNDEFINED_CUSTOMER_ID":
		filename.append("NO_REFERENCE")

	#filename = filename + [ name, doctype, "%s" % unique]

	folder = []
	if category != "UNDEFINED_CATEGORY":
		folder =  [year, category]
	folder2 = []
	if category2 != "UNDEFINED_CATEGORY":
		folder2 = [year, category2]

	if folder and not folder2:
		return folder, filename, []
	elif folder2 and not folder:
		return folder2, filename, []
	elif folder and folder2: 
		return folder, filename, folder2
	else:
		return [year, "UNDEFINED_CATEGORY"], filename, []



def nearest(base, dates):
	nearness = {}
	for date in dates:
		nearness[abs(date - base)] = date
		logger.debug("%s has a diff of %s" %(date, abs(date - base)))
	minimum = min(nearness.keys())
	return nearness[minimum]


def search_for_date(content):
	'''tested'''

	content = content.replace(" ", "")
	dates = []
	#### 01.01.1984
	matches = re.findall(r'\d{2}\.\d{2}\.\d{4}', content)  
	#import pdb; pdb.set_trace()
	if matches:
		for match in matches:
			try:
				fdate = datetime.strptime(match, '%d.%m.%Y').date()
				test = fdate.strftime("%d.%m.%Y")
				dates.append(fdate)
				logger.debug("format 01.01.1984 found: %s" % match)
			except ValueError:
				logger.warning("found preudo date -01.01.1984-, skipping it")

			
	#### 01-01-1984
	matches = re.findall(r'\d{2}\-\d{2}\-\d{4}', content)  
	#import pdb; pdb.set_trace()
	if matches:
		for match in matches:
			try:
				fdate = datetime.strptime(match, '%d-%m-%Y').date()
				test = fdate.strftime('%d-%m-%Y')
				dates.append(fdate)
				logger.debug("format 01-01-1984 found: %s" % match)				
			except ValueError:
				logger.warning("found preudo date -01-01-1984-, skipping it")
			
	
	##### 01.Januar1984
	matches = re.findall(r'\d{2}\.\D{3,9}\d{4}', content)  
	if matches:
		for match in matches:
			try:
				fdate = datetime.strptime(match, '%d.%B%Y').date()
				test = fdate.strftime('%d.%B%Y')
				dates.append(fdate)
				logger.debug("format 01.Januar1984 found: %s" % match)
			except ValueError:
				logger.error("found pseudo date -01.Januar1984-, skipping it")

	##### 01Januar1984
	matches = re.findall(r'\d{2}\D{3,9}\d{4}', content)  
	if matches:
		for match in matches:
			try:
				fdate = datetime.strptime(match, '%d%B%Y').date()
				test = fdate.strftime('%d%B%Y')
				dates.append(fdate)
				logger.debug("format 01Januar1984 found: %s" % match)
			except ValueError:
				logger.error("found pseudo date -01Januar1984-, skipping it")

	##### 01-Januar-1984
	matches = re.findall(r'\d{2}\-\D{3,9}-\d{4}', content)  
	if matches:
		for match in matches:
			try:
				fdate = datetime.strptime(match, '%d-%B-%Y').date()
				test = fdate.strftime('%d-%B-%Y')
				dates.append(fdate)
				logger.debug("format 01-Januar-1984 found: %s" % match)
			except ValueError:
				logger.error("found pseudo date -01-Januar-1984-, skipping it")				

	##### 15. Mai 2013 
	matches = re.findall(r'\d{2}\. \D{3,9} \d{4}', content)  
	if matches:
		for match in matches:
			try:
				fdate = datetime.strptime(match, '%d. %B %Y').date()
				test = fdate.strftime('%d. %B %Y')
				dates.append(fdate)
				logger.debug("format 01. Januar 1984 found: %s" % match)
			except ValueError:
				logger.error("found pseudo date -01. Januar 1984-, skipping it")	



	##### Januar1984
	if not dates:	
		matches = re.findall(r'\D{3,9}\d{4}', content)  
		if matches:
			for match in matches:
				try:
					fdate = datetime.strptime(match, '%B%Y').date()
					test = fdate.strftime('%B%Y')
					dates.append(fdate)
					logger.debug("format Januar1984 found: %s" % match)
				except ValueError:
					logger.error("found pseudo date -Januar1984-, skipping it")							

	#### 01.01.84 this will make 11.02.2017 to 22.02.2020 , so we do it only if all the previos have failed 
	if not dates:
		matches = re.findall(r'\d{2}\.\d{2}\.\d{2}', content)  
		if matches:
			for match in matches:
				try:
					fdate = datetime.strptime(match, '%d.%m.%y').date()
					test = fdate.strftime('%d.%m.%y')
					dates.append(fdate)
					logger.debug("format 01.01.84 found: %s" % match)
				except ValueError:
					logger.error("found pseudo date -01.01.84-, skipping it")

		matches = re.findall(r'\d{2}\-\d{2}\-\d{2}', content)  
		if matches:
			for match in matches:
				try:
					fdate = datetime.strptime(match, '%d-%m-%y').date()
					test = fdate.strftime('%d-%m-%y')
					dates.append(fdate)
					logger.debug("format 01-01-84 found: %s" % match)
				except ValueError:
					logger.error("found pseudo date #01-01-84#, skipping it")					
	#### 01011984
	if not dates:
		matches = re.findall(r'\d{2}\d{2}\d{4}', content)  
		if matches:
			for match in matches:
				try:
					fdate = datetime.strptime(match, '%d%m%Y').date()
					test = fdate.strftime('%d%m%Y')
					dates.append(fdate)
					logger.debug("format 0101984 found: %s" % match)
				except ValueError:
					logger.error("found pseudo date -01011984-, skipping it")

	if len(dates) > 1:
		for each in dates:
			if each.strftime('%d') == "01" and each.strftime('%m') == "01":
				dates.remove(each)
			if each.strftime('%d') == "31" and each.strftime('%m') == "12":
				dates.remove(each)



	if not dates:
		logger.error("could not find any date, taking default")
		dates.append(datetime.strptime("01.01.1984", '%d.%m.%Y').date())

	present = date.today()
	selected_date = nearest(present, dates)
	logger.debug("alle   %s " %dates)
	logger.debug("heute  %s " %present)
	logger.debug("select %s " %selected_date)

	return selected_date

def get_text(in_file):
	resource_manager = PDFResourceManager()
	fake_file_handle = io.StringIO()
	converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
	page_interpreter = PDFPageInterpreter(resource_manager, converter)
	with open(in_file, 'rb') as fh:
		for page in PDFPage.get_pages(fh,
									caching=True,
									check_extractable=True):
			page_interpreter.process_page(page)
		pdftext = fake_file_handle.getvalue()
	converter.close()
	fake_file_handle.close()
	content=pdftext.replace('\n', '').replace(" ", "")
	return content

def analyse(folder, output_folder, keyfile_path):
	'''tested'''

	CATEGORY= json.load(open(pjoin(keyfile_path, "CATEGORY.json")))
	COMPANIES_WO_ID= json.load(open(pjoin(keyfile_path, "COMPANIES_WO_ID.json")))
	CUSTOMER_ID= json.load(open(pjoin(keyfile_path, "CUSTOMER_ID.json")))
	DOCTYPES= json.load(open(pjoin(keyfile_path, "DOCTYPES.json")))
	NAMES= json.load(open(pjoin(keyfile_path, "NAMES.json")))

	copy_actions = {}   # will be copy_actions[soucre] = destination
	mail_info = {}
	mail_info_path = {}
	created_files = []
	for pdf in os.listdir(folder):
		if pdf.endswith(".pdf") or pdf.endswith(".PDF"):
			logger.info("-------------------------------------")
			logger.debug("processing %s " % pdf)
			in_file = pjoin(folder, pdf)
			content = get_text(in_file)
			folder_tags, file_tags , second_folder = analyse_content(
											content,
											CATEGORY,
											COMPANIES_WO_ID , 
											CUSTOMER_ID, 
											DOCTYPES, NAMES)
			try:
				new_filename = "%s.pdf" % "_".join(file_tags).replace("__", "_")  # __ in case of unknow doctype
			except TypeError:
				logger.error("errors with filename %s" %filetags)
				#import pdb; pdb.set_trace()
			source_file = pjoin(folder, pdf)
			#import pdb; pdb.set_trace()
			dest_file = pjoin('', *([output_folder] + folder_tags + [new_filename]))
			mail_info[new_filename] = folder_tags[1]
			mail_info_path[new_filename] = pjoin('', *(folder_tags + [new_filename]))			
			logger.info("old file was     %s" % source_file)
			logger.info("new file will be %s" % dest_file)
			logger.info("-------------------------------------")
			copy_actions[dest_file] = source_file			
			if second_folder:
				dest_file2 = pjoin('', *([output_folder] + second_folder + [new_filename]))
				mail_info[new_filename] = "%s and %s" % (folder_tags[1], second_folder[1])
				mail_info_path[new_filename] = pjoin('', *(folder_tags + [new_filename]))
				logger.info("second new file will be %s" % dest_file2)
				logger.info("-------------------------------------")
				copy_actions[dest_file2] = source_file

	return copy_actions, mail_info, mail_info_path

