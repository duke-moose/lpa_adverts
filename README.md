
# Purpose 
Utilize Selenium to scrape websites with a headless browser. 
=======
Purpose to create a website or email list of RFPs and RFQs from Louisiana Public Notice website.
Website would be a table or list showing: Date, Parish, Public Notice Source, and a brief description of the notice.

_TODO_  
get "tests/webdriver_test.py" to run.

**LPA.py**  
Search Louisiana Public Notice for RFP & RFQs. 

'http://www.publicnoticeads.com/LA/search/searchnotices.asp'

Input search term and date range to generate dictionary of serachable results.

_TODO_  
- Read monthly meeting notes to search for Board actions to release or prepare RFPs.  
- Make each found item a list on a website.

**nltk_helper.py**  
Will be used to format results to place into a readable list to email.

**muni_codes.py**  
Scrape Jefferson parish municodes website. Saves each html page as a txt file.
