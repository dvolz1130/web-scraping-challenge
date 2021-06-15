from bs4 import BeautifulSoup
import pandas as pd
from splinter import Browser
import pymongo
from webdriver_manager.chrome import ChromeDriverManager


# setting up the chrome driver with a method
def init_web():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=True)

# The scraper method
def scrape():
    browser = init_web()

    # Mars News
    mars_url = "https://redplanetscience.com/"
    browser.visit(mars_url)
    mars_html = browser.html
    mars_soup = BeautifulSoup(mars_html, 'html.parser')
    mars_article_title = mars_soup.find("div", class_="content_title").text
    mars_article_para = mars_soup.find("div", class_="article_teaser_body").text

    # Mars Feature Image
    img_url = "https://spaceimages-mars.com/"
    browser.visit(img_url)
    img_html = browser.html
    img_soup = BeautifulSoup(img_html, 'html.parser')
    base_img_url = "https://spaceimages-mars.com/"
    mars_img = img_soup.find("img", class_="headerimage fade-in").get("src")
    featured_image_url = base_img_url + mars_img

    # Mars Facts
    facts_url = "https://galaxyfacts-mars.com/"
    facts_table = pd.read_html(facts_url)
    mars_facts_df = facts_table[0]
    mars_facts_df.columns = ["", "Mars", "Earth"]
    mars_fact_html = mars_facts_df.to_html(index=False)

    #Mars Hemispheres
    mars_hem_url = "https://marshemispheres.com/"
    browser.visit(mars_hem_url)
    mars_hem_html = browser.html
    mars_hem_soup = BeautifulSoup(mars_hem_html, 'html.parser')
    mars_hem = mars_hem_soup.find_all("div", class_="item")
    hemisphere_image_urls = []
    for mar_h in mars_hem:
        hem_dict = {}
        title = mar_h.find("h3").text
        to_image_page = mar_h.find("a")["href"]
        image_url = mars_hem_url + to_image_page 
        browser.visit(image_url)
        html = browser.html
        image_soup = BeautifulSoup(html, 'html.parser')
        image_download = image_soup.find("div", class_ = "downloads")
        image_jpg = image_download.find("a")["href"]
        image = mars_hem_url + image_jpg
        hem_dict["title"] = title
        hem_dict["image_url"] = image
        hemisphere_image_urls.append(hem_dict)

    # Close out the browers
    browser.quit()

    # Setup connection to mongodb
    conn = "mongodb://localhost:27017"
    client = pymongo.MongoClient(conn)
    db = client.mars_facts_db
    # drop the collection if it exist
    mars_col = db.mars_facts
    mars_col.drop()
        
    # Dictionary to hold the Mars data to be inserted into Mongo
    mars_data = {
        "news_title": mars_article_title,
        "news_p": mars_article_para,
        "featured_image": featured_image_url,
        "facts_table": mars_fact_html,
        "hemispheres_images": hemisphere_image_urls
    }

    # Insert into the collection
    mars_col.insert_one(mars_data)