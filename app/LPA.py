# 'https://www.guru99.com/accessing-forms-in-webdriver.html'
# https://pythonspot.com/selenium/

from datetime import datetime, timedelta
import json
import re
from time import time, sleep

from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import urllib3


class AspxScraper(object):
    def __init__(self, url, from_date=None, to_date=None,
                 working_dir=None, preferences=None, options=None, timeout=None):
        self.url = self.check_url_response(url)
        self.working_dir = working_dir
        self.preferences = preferences
        self.options = options
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

    def check_url_response(self, url_to_check):
        http = urllib3.PoolManager()
        r = http.request('GET', url_to_check)
        statuscode = r.status

        if statuscode == 200:
            return url_to_check
        else:
            raise ConnectionError('{}: url status code.'.format(statuscode))

    def access_aspx_url(self):
        # https://www.programcreek.com/python/example/100026/selenium.webdriver.FirefoxProfile
        # http://kb.mozillazine.org/Firefox_:_FAQs_:_About:config_Entries#Browser.
        aspx_url = self.url
        preferences = self.preferences
        options = self.options
        if preferences:
            profile = FirefoxProfile()
            for i in preferences:
                profile.set_preference(i, preferences[i])
            browser = webdriver.Firefox(firefox_profile=profile, options=options)
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

    def get_all_hrefs(self, xpath):
        hrefs = []
        # print('pass1')
        hrefs.extend(href.get_attribute('href') for href in self.browser.find_elements_by_xpath(xpath))
        return hrefs

    def get_LPA_hrefs(self, xpath):
        hrefs = []
        while True:
            try:
                # print('pass1')
                hrefs.extend(href.get_attribute('href') for href in self.browser.find_elements_by_xpath(xpath))
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
        """

        :param info_string: list of location, newspaper, and date.
        :return: tuple of strings (<County>, <Printed In>, <Printed On>)

        Example:
            info_string = [
            'County: East Baton Rouge '
            'Printed In: The Advocate '
            'Printed On: 2020/01/02',
            ]

        >> cleanup_info(info_string)
        >> 'East Baton Rouge', 'The Advocate', '20200102'

        """
        # print(info_string)
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
        print(
            'County: {}, Printed In: {}, Printed On: {}'.format(
                parish_name, paper_name, print_date
            )
        )
        return parish_name, paper_name, print_date

    def la_public_notice_get(self, search):
        '''
        This is the main function to run.
        '''
        # Access url
        self.access_aspx_url()

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
        self.hrefs = self.get_LPA_hrefs("//td/font/small/a")

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

            format_end_date = datetime.strptime(self.to_date, '%m/%d/%Y')
            new_end_date = format_end_date.strftime('%Y%m%d')
            with open('notice_dict_test_' + new_end_date + '.txt', 'w') as outfile:
                outfile.write(json.dumps(notice_dict))

        self.browser.quit()


if __name__ == "__main__":
    # Louisiana Public Notice script
    # Script to create a dictionary of Advertisements between the given date range with the key search phrase.'
    Lpa_url = 'http://www.publicnoticeads.com/LA/search/searchnotices.asp'
    search_phrase = "Engineer"  # "Public Notice Engineer qualification"

    # Define search date range.
    # start_date = datetime.today() - timedelta(7)
    # end_date = datetime.today()
    start_date = '3/30/2020'
    end_date = '4/10/2020'


    # Timer
    t0 = time()

    # Set Preferences
    directory_to_save = '/data'
    pref = {
        'profile.set_preference(''browser.download.dir': directory_to_save,
    }


    Lpa = AspxScraper(Lpa_url, start_date, end_date, directory_to_save, pref)
    Lpa.la_public_notice_get(search_phrase)

    t1 = time()
    print(str(t1-t0) + ' seconds')

# Run nltk_helper.py after this file.