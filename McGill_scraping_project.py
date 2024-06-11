#This code will scrape McGill faculty of chemistry website "https://www.mcgill.ca/chemistry/faculty"
#It will fetch all links to the faculty's websites.
#It will then go through each faculty website and put their names in one column and a summary of their research in another one
#This program will help me have an idea about everyone's research without spending much time clicking through 
#every link and reading everything about their research

from bs4 import BeautifulSoup
import requests 
import pandas as pd
from transformers import pipeline

summarizer = pipeline('summarization')
main_website = "https://www.mcgill.ca/chemistry/faculty"

#The fuction transforms the contents of a provided link's webpage and turns it into a "soup" using BeautifulSoup library
#The soup can then be scraped
#@var link is a string containting the https address of a website whose contents need to be made into a soup
#@return soup; soup is basically html code of the page provided in the @link
def get_soup(link):
    page_to_scrape = requests.get(link)
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    return soup

#The function finds fourth to eighth <p> tags and puts the text in them in one string.
#The reason we are doing fourth to eights is because that is the region where Research Interests are typically outlined. 
#@var soup - is html soup from which we can extract text within <p> tags
#@return paragraphs is a string with all web text contained in <p> tags
def get_web_text(soup):
    ps = soup.findAll("p")
    paragraphs = ""
    for p in ps[4:8]:
        paragraphs = paragraphs + " " + p.get_text(strip=True, separator = '\n')
    return paragraphs

#The function uses transformers package to summarize text
#@var text must be a string of text that can be summarized 
#return summary_text a string of summarized text
def get_summary(text):
    summary_list = summarizer(text, max_length=200, min_length = 80, do_sample = False)
    summary_dictionary = summary_list[0]
    summary_text = list(summary_dictionary.values())[0]
    return summary_text

#This is the table with all the information about faculty on their main page
table = get_soup(main_website).find('table')

#The data I want to extract from main_website is just links to a personal webstie of faculty members
#I can make  a dataframe with only one column to store those links for later use
link_df = pd.DataFrame(columns=["link"])

#Looking at the code for the table we can see that all the rows are defined as <tr> tags
#and all the data in the rows are in the <td> tags
#We have to go through all the rows (<tr>s) and isolate the <td>s
rows = table.find_all("tr")

#This loop goes through all the contents of a table and retreives links faculty member websites
#row by row. It then adds that information to a @link_df we created earlier. 
i=0
for row in rows[1:]: #omiting the first one as it contains the titles of the table which are irrelevant
    row_data = row.find_all("td")
    first_column_data = row_data[0] #only need data in the first row
    #An example of first column data is <td><a href="https://www.mcgill.ca/chemistry/Node/19">Andrews, Mark</a></td>
    link = first_column_data.find("a").get('href') #getting the link

    #Now as we go through names and links we should add them one by one to the dataframe
    #We can put name in the first coulumn and the link in the second column 
    link_df.loc[i] = pd.Series({"link":link})
    i = i+1

#Now, I need to place the text found in each of the links in another column of the dataframe
#This turns out to be a scraping project inside of a scraping project

#We can go through all of the items in the links column and make soups out of all of them. Then we will 
#isolate <h1> tags, those are the names of faculty. 
#I also chose to isolate some <p> tags to get and summarize the faculty's research interests.       


df = pd.DataFrame(columns=["name", "research summary"])
i=0
for link in link_df["link"]: 
     soup = get_soup(link)
     name = soup.find('h1').get_text(strip=True, separator = '\n')
     text_to_summarize = get_web_text(soup)
     summary = get_summary(text_to_summarize)
     df.loc[i] = pd.Series({"name":name, "research summary":summary})
     i = i + 1

df.to_csv(r"/Users/mila/Desktop/Scrape/McGill_3.csv", index = False)

