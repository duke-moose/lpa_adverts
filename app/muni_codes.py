import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import selenium.common.exceptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from app.LPA import AspxScraper as AS


def get_code_ordinances(url, save_dir, pref=None, opt=None, xpath_wait=None, timeout=20):
    """
    Use WebDriverWait for page to load and get all HTML that meets xpath_wait. Save HTML to save_dir.
    If the wait times out there are more HREF links to search. This returns those links.

    :param url: url for web scraping.
    :param save_dir: Directory to save scraping information
    :param pref: selenium.webdriver preferences
    :param opt: selenium.webdriver options
    :param xpath_wait: xpath to wait for load before website scrape.
    :param timeout: length of timeout in seconds
    :return: list of href links, if timeout fails
    """
    # Setup web scrape object.
    gcol = AS(url, working_dir=save_dir, preferences=pref, options=opt)
    # Perform web scrape
    gcol.access_aspx_url()

    if xpath_wait:
        href_all = None
        try:
            wdw_obj = WebDriverWait(gcol.browser, timeout).until(
              expected_conditions.presence_of_element_located((By.XPATH, xpath_wait))
            )
            txt = wdw_obj.text
            fname = '{}.txt'.format(url.split('=')[1])
            with open(os.path.join(gcol.working_dir, fname), 'w') as inf:
                inf.write(txt)

            # TODO Convert string to list to remove some common items.
            # print(txt.split('\n'))

            # Display to screen if the URL worked. This is for visual error handling.
            # print('Worked: {}'.format(url))
        except selenium.common.exceptions.TimeoutException:
            # Some pages have many Articles referenced elsewhere.
            href = gcol.get_all_hrefs("//a[@class='toc-item-heading']")
            href_all = [h for h in href if 'CH' in h]  # Get all Chapters.
            href_all.extend([h for h in href if 'ART' in h])  # Get all Articles.
            href_all.extend([h for h in href if 'DIV' in h])  # Get all Divisions.

            # print('Not Worked: {}'.format(url))
        finally:
            gcol.browser.quit()
        return href_all
    else:
        print('No XPATH provided. Develop new method that doesn\'t requpire xpath if this is needed.')


def run_loop(url_list, save_dir, pref=None, opt=None, xpath_wait=None):
    """
    Run the Code of Ordinances scraping loop.

    :param url_list: list of urls for web scraping.
    :param save_dir: Directory to save scraping information
    :param pref: selenium.webdriver preferences
    :param opt: selenium.webdriver options
    :param xpath_wait: xpath to wait for load before website scrape.
    :return: scrape and save all html as TXT files.
    """
    # Blank list to hold all searched URLs.
    searched_urls = []

    while url_list:
        # Loop through list from the end to prevent skipping items in the list as they're added.
        for url in reversed(url_list):
            # No matter what I try with list comprehension doubles make it in. This skips them.
            if url not in searched_urls:
                # Scrape ordinances, or return HREFs if scrape fails.
                more_urls = get_code_ordinances(
                    url, save_dir,
                    pref=pref,
                    opt=opt,
                    xpath_wait=xpath_wait
                )

                # Add all searched URLs to list. This is used to prevent visiting URLs more than once.
                searched_urls.append(url)
                if more_urls:
                    # make list of all_urls that have been and will be searched.
                    if url_list:
                        if searched_urls:
                            all_urls = url_list.extend(searched_urls)
                        else:
                            all_urls = url_list
                    else:
                        all_urls = searched_urls

                    # extend list to include only new urls.
                    new_urls = [x for x in more_urls if x not in all_urls]
                    url_list.extend(new_urls)
                    # Remove any repeat links from the list.
                    url_list = list(set(url_list))
            else:
                # # Used for troubleshooting.
                # print('code_urls', url_list)
                # print('already searched {}'.format(url))
                print('Searched {} urls......{} urls to go.'.format(len(searched_urls), len(url_list)))

            url_list.remove(url)  # After using url, remove it.


if __name__ == "__main__":
    # code_urls is a list with the first item being the main page for a Municode Website.
    code_urls = ['https://library.municode.com/la/jefferson_parish/codes/code_of_ordinances']

    # Set browser and options
    options = FirefoxOptions()
    options.add_argument("--headless")  # Headless browser

    # Set browser preferences
    save_directory = 'data/jeff_parish'
    preferences = {
        'profile.set_preference(''browser.download.dir': save_directory,
    }

    # Xpath to find on website before a scrape is preformed. This lets all Javascript load.
    xpath_municode = "//ul[@class='chunks list-unstyled small-padding']"

    run_loop(code_urls, save_directory, pref=preferences, opt=options, xpath_wait=xpath_municode)
