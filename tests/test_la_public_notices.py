import unittest
from time import sleep
from app import LPA
import os


class InputFormsCheck(unittest.TestCase):
    # Opening browser.
    @classmethod
    def setUpClass(cls):
        """
        Example: https: // stackoverflow.com / questions / 23667610 /
        what - is -the - difference - between - setup - and -setupclass - in -python - unittest
        """
        Lpa_url = 'http://www.publicnoticeads.com/LA/search/searchnotices.asp'
        search = "Engineer"
        from_date = "1/1/2020"
        to_date = "1/2/2020"
        directory = os.getcwd()
        save_dir = directory
        pref = {
            'profile.set_preference(''browser.download.dir': save_dir,
        }

        cls.lpa = LPA.AspxScraper(Lpa_url, from_date, to_date, save_dir, pref)

        # # Finding "Search With all these words" input text field by name. And sending keys(entering data) in it.
        cls.ele_search = search

        # # Find "Date from" input text field by name. And send keys.
        cls.from_date = cls.lpa.from_date

        # # Find "Date to" input text field by name. And send keys.
        cls.to_date = cls.lpa.to_date

        # Wait for search page to load
        sleep(2)

        cls.lpa.la_public_notice_get(search)
        # print(lpa)
        # cls._ele_search_msg = lpa._ele_search_msg

    # Test the element search word was found as search term.
    def test_ele_search(self):
        msg = 'You searched for: Engineer<br>Date Range: Between 1/1/2020 and 1/2/2020.'
        assert msg == self.lpa._ele_search_msg[0]

    # Test that header has 4 specific strings.
    def test_header_strings(self):
        ele_header = ['County', 'Date', 'PublicNoticePreview', 'Publication']
        assert ele_header == self.lpa._ele_search_header


if __name__ == "__main__":
    unittest.main()