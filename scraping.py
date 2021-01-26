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
        "listdict": hemi_img(browser)
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
    full_image_elem = browser.find_by_xpath('/html/body/div/div/div/main/div[2]/div[2]/div[2]/div/section/div[4]/div/a')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_xpath('/html/body/div/div/div/main/div/div[2]/div/div/div[2]/button', wait_time=1)
    more_info_elem = browser.find_by_xpath('/html/body/div/div/div/main/div/div[2]/div/div/div[2]/button')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
     # Find the relative image url
    browser.is_element_present_by_xpath('/html/body/div/div/div/main/div/div[2]/div/div/div[3]/div[2]/div[2]/div/div/img', wait_time=1)
    # Add try/except for error handling
    try:
       
        marsImage = browser.find_by_xpath('/html/body/div/div/div/main/div/div[2]/div/div/div[3]/div[2]/div[2]/div/div/img')['src']

    except BaseException:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://www.jpl.nasa.gov{marsImage}'
    

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

def hemi_img(browser):

    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []
    # site = 'https://astrogeology.usgs.gov/'
    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    for hemi in range(4):
        # Create dictionary object inside the for loop
        hemi_dict = {}    
        keys = range(2)
        # click the link
        link = browser.find_by_tag("div.description a.itemLink.product-item")[hemi]
        link.click()
        # Reset the parser
        html2 = browser.html
        image_soup = soup(html2, 'html.parser')
    
        # get the image link for the full sized image
        image_target = image_soup.select_one('li a').get('href')
    
        # get the title for the image
        image_title = image_soup.select_one('h2').get_text()
        values = [image_target, image_title]
        # For loop will: Click on each link, navigate to full-res image and pull image URL string and title for each image
        for key in keys:
            hemi_dict[key] = values[key]
        hemi_dict['img_url'] = hemi_dict.pop(0)
        hemi_dict['title'] = hemi_dict.pop(1)
        hemisphere_image_urls.append(hemi_dict)
        browser.back()
        
    return hemisphere_image_urls


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())