#Created by Timothy Gamble

import os
import re
import time
import json
import glob
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from PyPDF2 import PdfFileMerger, PdfFileReader
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

profile = webdriver.FirefoxProfile()
profile.set_preference("pdfjs.disabled", True)
profile.set_preference("browser.download.folderList",2)
profile.set_preference("browser.helperApps.alwaysAsk.force", False)
profile.set_preference("browser.download.manager.showWhenStarting",False)
profile.set_preference("browser.download.dir", "/Users/Tim/Documents/Github/muse-downloader/temp") #Point this to the temp folder
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
profile.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf")
driver = webdriver.Firefox(firefox_profile=profile)

__MAINURL__ = "https://muse.jhu.edu/login"
__BROWSEURL__ = "http://muse.jhu.edu/browse"
__USERNAME__ = raw_input('Username: ')
__PASSWORD__ = getpass.getpass('Password: ')

def login(): #Edit the login process for your school, mine is UIUC
	driver.get(__MAINURL__)
	select = Select(driver.find_element(By.XPATH,'//div[@id="shibboleth-box"]/select'))
	select.select_by_value('urn%3Amace%3Aincommon%3Auiuc.edu')
	driver.find_element(By.XPATH,'//div[@id="login-submit-button"]/button').click()
	driver.find_element(By.XPATH,'//input[@id="j_username"]').send_keys(__USERNAME__)
	driver.find_element(By.XPATH,'//input[@id="j_password"]').send_keys(__PASSWORD__)
	driver.find_element(By.XPATH,'//div[@id="submit_button"]/input').click()
	time.sleep(5)

def get_parent_links():
	driver.get(__BROWSEURL__)
	time.sleep(5)
	lis = driver.find_elements(By.XPATH,'//div[@class="listing"]/ul[@class="colone"]/li/a | //div[@class="listing"]/ul[@class="coltwo"]/li/a ')
	parent_links = []
	for li in lis:
		parent_links.append(li.get_attribute('href') + '?items_per_page=999&m=1')
	return parent_links

def get_book_links():
	book_links = []
	for link in get_parent_links():
		driver.get(link)
		time.sleep(5)
		flag = True
		driver.find_element(By.XPATH,'//input[@id="access_level"]').click()
		time.sleep(5)
		while(flag):
			book_names = driver.find_elements(By.XPATH,'//div[@class="single_result"]/div/h1/a')
			for book in book_names:
				link = book.get_attribute('href')
				if not 'journals' in link:
			 		book_links.append(book.get_attribute('href'))
			try:
				driver.find_element(By.XPATH,'//div[@class="control_nav"]/p[@class="select_page"]/a[@class="nextarrow"]').click()
				time.sleep(5)
			except:
				flag = False
	with open('book_links.json','w') as output:
		json.dump(book_links, output)

def download_book(url):
	driver.get(url)
	chapters = driver.find_elements(By.XPATH,'//div[@id="toc"]/div[@class="chapter"]/div[@class="chapter_detail"]/p/a | //div[@id="toc"]/div[@class="chapter"]/div[@class="chapter_detail"]/div/p/a')
	for chapter in chapters:
		driver.get(chapter.get_attribute('href'))
	time.sleep(5)
	merge_pdf(url)

def key_func(afilename):
	nondigits = re.compile("\D")
	return int(nondigits.sub("", afilename))

def merge_pdf(url):
	name = url.split('/')[-1]
	file_names = []
	for x in sorted(glob.glob('temp/*.pdf'), key=key_func):
		file_names.append(x)
	if len(file_names) != 0:
		merger = PdfFileMerger()
	for filename in file_names:
		merger.append(fileobj = PdfFileReader(file(filename, 'rb')), pages = (1,PdfFileReader(open(filename)).getNumPages()))
	merger.write("books/" + name + ".pdf")
	for f in file_names:
		os.remove(f)

def download_all_books():
	with open('book_links.json','r') as links:
		book_links = json.loads(links.read())
		for link in book_links:
			download_book(link)

if __name__ == '__main__':
	login()
	# get_book_links() #Comment this out after you gathered all of the book links.
	download_all_books()
	driver.close()
