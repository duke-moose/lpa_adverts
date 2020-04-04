# 'https://www.guru99.com/accessing-forms-in-webdriver.html'
# https://pythonspot.com/selenium/

from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import os
from time import time, sleep
from datetime import datetime, timedelta
from nltk.tokenize import sent_tokenize
import re
import json


class AspxScraper:
    def __init__(self, url, from_date, to_date, working_dir, preferences=None, timeout=None):
        self.url = url
        self.working_dir = working_dir
        self.preferences = preferences
        self.timeout = timeout

        self.browser = None
        self._ele_search_msg = None
        self._ele_search_header = None
        self.hrefs = None

        # Convert datetime and date to string to enter to webpage.
        if from_date is datetime:
            self.from_date = from_date.strftime('%m/%d/%Y')  # '1/1/1996'
            self.to_date = to_date.strftime('%m/%d/%Y')  # '1/31/1996'
        else:
            self.from_date = from_date
            self.to_date = to_date

    def access_aspx_url(self, aspx_url, preferences=None):
        # https://www.programcreek.com/python/example/100026/selenium.webdriver.FirefoxProfile
        # http://kb.mozillazine.org/Firefox_:_FAQs_:_About:config_Entries#Browser.
        if preferences:
            profile = FirefoxProfile()
            for i in preferences:
                profile.set_preference(i, preferences[i])
            browser = webdriver.Firefox(firefox_profile=profile)
        else:
            # url example: 'http://www.ethics.la.gov/CampaignFinanceSearch/SearchEfilingContributors.aspx'
            browser = webdriver.Firefox()
        browser.get(aspx_url)
        self.browser = browser

    def fill_element(self, name=None, send_keys=None):
        '''
        Use find_element_by_name and send keys.
        Can be updated with other find_XX as necessary.
        '''
        if name and send_keys:
            ele_user_search = self.browser.find_element_by_name(name)
            ele_user_search.clear()
            ele_user_search.send_keys(send_keys)

    def get_all_hrefs(self):
        hrefs = []
        while True:
            try:
                # print('pass1')
                hrefs.extend(href.get_attribute('href') for href in self.browser.find_elements_by_xpath("//td/font/small/a"))
                # print('pass2')
                self.browser.find_element_by_link_text('Next Records >>').click()
                # print('pass3')
                sleep(2)
            except Exception as e:
                if 'Unable to locate element: Next Records >>' in str(e):
                    print('End of record:: ' + str(e))
                else:
                    print('Error:: ' + str(e))
                break
        return hrefs

    def cleanup_info(self, info_string):
        '''info_string format:
            info = [
            'County: East Baton Rouge '
            'Printed In: The Advocate '
            'Printed On: 2020/01/02',
        '''
        print(info_string)
        parish_regex = re.compile(r'County:(.*)')
        parish = parish_regex.search(info_string)
        # print('Parish: ' + parish.group())
        parish_name = parish.group(1).strip(' ')

        paper_regex = re.compile(r'Printed In:(.*)')
        paper_name = paper_regex.search(info_string)
        # print('Paper: ' + paper_name.group(1))
        paper_name = paper_name.group(1).strip(' ')

        print_date_regex = re.compile('Printed On:(.*)')
        print_date = print_date_regex.search(info_string)
        # print('Date: ' + print_date.group(1))
        print_date = print_date.group(1).strip(' ')
        print_date = datetime.strptime(print_date, '%Y/%M/%d')
        print_date = print_date.strftime('%Y%m%d')

        return parish_name, paper_name, print_date

    def la_public_notice_get(self, search):
        '''
        This is the main function to run.
        '''
        # Access url
        self.access_aspx_url(self.url)

        # Finding "Search With all these words" input text field by name. And sending keys(entering data) in it.
        self.fill_element('txtSearchWordsAnd', search)

        # Find "Date from" input text field by name. And send keys.
        self.fill_element('txtDateFrom', self.from_date)

        # Find "Date to" input text field by name. And send keys.
        self.fill_element('txtDateTo', self.to_date)

        # Finding "Show Your Message" button element by css selector using both id and class name. And clicking it.
        ele_search_btn = self.browser.find_element_by_name('SearchRollOver')
        ele_search_btn.click()

        # Wait for search page to load
        sleep(2)

        # Copy the search string as read by the website
        _ele_search_msg = self.browser.find_elements_by_xpath("//text")
        self._ele_search_msg = [i.get_attribute('innerHTML').replace("\n", "").replace("  ", "")
                                for i in _ele_search_msg]

        # Copy the search header as read by the website
        _ele_search_header = self.browser.find_elements_by_xpath("//table/tbody/tr/th/font")
        self._ele_search_header = [i.get_attribute('innerHTML').replace("\n", "").replace(" ", "")
                                   for i in _ele_search_header]

        # Create list of all hrefs.
        self.hrefs = self.get_all_hrefs()

        # Get text from the notice

        # Organize text from the notice into dictionary.

        # Save text from notices dictionary
        notice_dict = {}
        for href in self.hrefs:
            self.browser.get(href)
            sleep(2)

            # Collect basic information about location, source, and date.
            info = self.browser.find_element_by_id('publicationInfo').text
            parish, paper, date = self.cleanup_info(info)

            notice_text = self.browser.find_element_by_id('noticeText').text

            try:
                count = len(notice_dict[parish]) + 1
                notice_dict[parish][count] = {
                    'paper': paper,
                    'date': date,
                    'text': notice_text,
                }
            except KeyError:
                notice_dict[parish] = {
                    1: {
                        'paper': paper,
                        'date': date,
                        'text': notice_text,
                    }
                }

            format_end_date = datetime.strptime(end_date, '%m/%d/%Y')
            new_end_date = format_end_date.strftime('%Y%m%d')
            with open('notice_dict_test_' + new_end_date + '.txt', 'w') as outfile:
                outfile.write(json.dumps(notice_dict))

        self.browser.quit()


if __name__ == "__main__":
    'Script creates the dictionary of Advertisements between the given date range with the key search phrase.'
    t0 = time()
    """Louisiana Public Notice script"""
    Lpa_url = 'http://www.publicnoticeads.com/LA/search/searchnotices.asp'
    search_phrase = "Engineer"  # "Public Notice Engineer qualification"
    directory_to_save = os.getcwd()
    # start_date = datetime.today() - timedelta(7)
    # end_date = datetime.today()
    start_date = '3/1/2020'
    end_date = '3/31/2020'
    pref = {
                'profile.set_preference(''browser.download.dir': directory_to_save,
            }

    Lpa = AspxScraper(Lpa_url, start_date, end_date, directory_to_save, pref)
    Lpa.la_public_notice_get(search_phrase)

    t1 = time()
    print(str(t1-t0) + ' seconds')

# Run nltk_helper.py after this file.