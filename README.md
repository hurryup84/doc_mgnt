# doc_mgnt
a framework to handle paper-mail. scan to mail, ocr, sort by content and send email reports

The goal was to have handy way to make all the daily paper-mail available on a NAS.
Therefore I created a little framework around ocrmypdf from https://github.com/jbarlow83/OCRmyPDF

The workflow is as follows:

## Scan paper and send per mail
Put the paper-mail on a scanner, which is capable of sending the scanned PDF to a email server. For example I use EPDON WorkForce WF-2760DWF. It was cheap, is easy to handle and even the scanning function is not blocked when the paint is empty.

## check mail
I host a little mail server on my raspberry pi, which is collecting the mails. Every hour (i think this is sufficient) a cronjob checks if some new mail have arrived. 

## ocr mailed pdfs
If a new mail with new pdf is available it is downloaded and OCRed with OcrMyPDF (https://github.com/jbarlow83/OCRmyPDF)

## categorize pdfs from content
There are 5 JSON files, which define some kind of categories, to sort the files. This is a bit stupid string searching in the ocred content. „string_to_be_searched“:“what this string stands for“


The JSON files are:

### DOCTYPE: 
if you have a quotation or an invoice etc.
### NAMES: 
to whom of your family the file belongs to
### CUSTOMER_ID: 
if you have a ID from some company, we can use it to look the company up (the company name itself is often integrated in a logo, so its hard to find)
### COMPANY_WO_ID: 
if you have no ID from a company, you may use the street name or similar to identify the company
### CATEGORY: 
All companies are assigned to categories. Categories may be shops, bank, insurance, etc.

## build filename 
After going through the json files, the name for the file will be build from the info:

DATE_NAME_DOCTYPE_PSEUDO-ID_COMPANY.pdf
(PSEUDO-ID is used to avoid overwriting a file, if you have two or more files with similar keys for the same date.)

If a company can be found from CUSTIMER_ID.json and COMPANY_WO_ID.json, two files are created and saved. 

## save to correct NAS folder
After the filename way created, the files is moved to a NAS. (Use NASSERVER, NASUSER, NASPATH, please exchange ssh-keys for easy login)
The files are moved to NASFOLDER/YEAR/CATEGORY/DATE_NAME_DOCTYPE_PSEUDO-ID_COMPAN.pdf

## report to some mail address
A report is created and send via mail to the MAILTO mail address, with the information about the identified file, and the webdav address where it is available (use WEBDAV_PATH)

## small mail interface
I figured out, that i often have to update the json files with new customer-id or similar. (At least during the first year)
So i added a litte communication interface via mail. Just send mails from your normal mail account to the same address as the scanner sends the pdfs to. You can send the following:

„#CAT company category“
e.g. #CAT Allianz Insurance

„#CID customer_id_key company“
e.g. #CID 4567853534 Allianz
          
„#CWOID customer_wo_id_key company“
e.g. #CWOID Reinholdstraße Allianz

„#DOC doctype_key doctype“
e.g. #DOC Invoice Rechnung

„#NAME name_key name“
e.g. #NAME MaxMustermann Max

There are to commands, which are combination of two of the aboven, which i used ofthe

„#CIDCAT customer_id_key company category“
e.g. #CIDCAT 4567853534 Allianz Insurance

→ will lead to the same, as sending the two mails:
	#CAT Allianz Insurance
	#CID 4567853534 Allianz

      
„#CWOIDCAT customer_wo_id_key company category“
e.g. #CWOIDCAT Reinholdstraße Allianz Insurance

→ will lead to the same, as sending the two mails:
	#CAT Allianz Insurance
	#CWOID Reinholdstraße Allianz

After adding new key, you will also receive a mail (use REPORT) with some info about it.


# how to setup:
the setup is draft, please contact me if i should add something

i recommend to setup a pi with rasbian-jessie-lite, but for sure you can use any other device a server

sudo apt-get update
install ocrmypdf (refer to https://github.com/jbarlow83/OCRmyPDF)
ocrmypdf must be in the path
 
sudo apt-get install python-pip 
sudo pip2 install PyPDF2

sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install subversion
sudo apt-get install qpdf
sudo apt-get install ghostscript
sudo apt-get install poppler-utils

Mailserver :
sudo modprobe ipv6
sudo mkdir -p /etc/citadel/netconfigs/7
sudo apt-get install citadel-suite  (or any other of your choice, follow instructions for seup)

if german:
set locate to German
sudo dpkg-reconfigure locales
select de_DE.UTF-8 UTF-8 with "Leertaste"
OK
select de_DE.UTF-8 UTF-8 as default

ssh keys mit NAS austauschen



The content of the configfile is described in:
	config/config.json.tmpl
Update toyour specific environment and rename to config.json

Modify also the configfiles in 
*	test_ressources/mail_test/*.json
*	test_ressources/main_test/*.json
*	test_ressources/nas_test/*.json
to get the unittests run.

## run the tool
Finally run the tool with:

python handle_documents.py PATH_TO_FOLDER_WITH_CONFIG_FILE

	





