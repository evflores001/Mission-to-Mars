# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="/usr/local/bin/chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "listdict": hem_scrape(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except BaseException:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hem_scrape(browser):

    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Get BS4 working
    html = browser.html
    moons_soup = soup(html, 'html.parser')

    # Find all the URLs and put into a list
    hemis = moons_soup.find_all("a", class_="itemLink product-item")

    hemilist = []

    for hemi in hemis:
        hemilist.append(hemi.get("href"))

    # Remove the duplicates and put back into a unique list
    hemilist = np.unique(hemilist)
    hemisp = hemilist.tolist()

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []
    site = 'https://astrogeology.usgs.gov/'
    # 3. Write code to retrieve the image urls and titles for each hemisphere.


    # Write for loop to iterate through the tags/CSS elements

    for hemi in hemisp:
            
        # Create dictionary object inside the for loop
        hem_dict = {}    
        
        # click the link
        browser.visit(f"{site}{hemi}")
      
        # Reset the parser
        html2 = browser.html
        moons_soup = soup(html2, 'html.parser')
        
        # get the image link for the full sized image
        imgtarget = moons_soup.select_one('li a').get('href')
        
        # get the title for the image
        imgtitle = moons_soup.select_one('h2').get_text()
        
        # Update the dictionary with this info
        hem_dict.update({'img_url': imgtarget, 'title':imgtitle})
        
        # Append the dictionary to the URL list
        hemisphere_image_urls.append(hem_dict)
            
        # For loop will: Click on each link, navigate to full-res image and pull image URL string and title for each image
        browser.back()

    return hemisphere_image_urls


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())