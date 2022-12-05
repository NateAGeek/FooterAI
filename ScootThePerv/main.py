from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from mimetypes import guess_extension;
from base64 import b64decode;
from threading import Thread;
import requests;
from time import sleep;
import os;

def download_image(img_src):
    img_index = hash(img_src);
    if img_src.startswith("http"):
        # Gotta stream it if it is big
        img_response = requests.get(img_src, stream=True);
        mime_type = img_response.headers['content-type']
        file_extension = guess_extension(mime_type);
        output_file = "./data/image_{}{}".format(img_index, file_extension);
        if os.path.exists(output_file):
            print("Image file exists: " + output_file);
        else:
            with open(output_file, "wb") as image:
                for buffer_data in img_response.iter_content():
                    image.write(buffer_data);
                print("Wrote an image: " + output_file);
        
    elif img_src.startswith("data:image"):
        mime_type = img_src[:img_src.index(";")].split(":")[1];
        file_extension = guess_extension(mime_type);
        output_file = "./data/image_{}{}".format(img_index, file_extension);
        if os.path.exists(output_file):
            print("Image file exists: " + output_file);
        else:
            with open(output_file, "wb") as image:
                image.write(b64decode(img_src[img_src.index(","):]));
                print("Wrote an image: " + output_file);
    
    else:
        print("Image not supported" + img_src[:55]);
   
def download_google_image_feed(browser: webdriver.Chrome, browser_wait: WebDriverWait):
    img_index = 0;
    done_downloading = False;
    while not done_downloading:
        # Need to keep forcing scrolling...
        while True:
            try:
                print("Scrolling down to bottom");
                browser.execute_script("window.scrollBy(0, document.body.scrollHeight)");
                try:
                    show_more_button = WebDriverWait(browser, 1).until(expected_conditions.visibility_of_element_located((By.XPATH, "//input[@value='Show more results']")))
                    show_more_button.click();
                except:
                    pass;
                
                try:
                    WebDriverWait(browser, 1).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[text()=\"Looks like you've reached the end\"]")));
                    print("Out of images to grab");
                    done_downloading = True;
                    break;
                except:
                    pass;
                sleep(1);
                browser_wait.until(
                    expected_conditions.presence_of_element_located((By.XPATH, "(//div[@data-root-margin-pages]//img[@width])[{}]".format(img_index+1)))
                );
                break;
            except:
                print("Failed to scroll to the bottom for some reason...");
                break;
        sleep(2);
        #get the images
        images = browser.find_elements(by=By.XPATH, value="//div[@data-root-margin-pages]//img[@width]");
        threads = list();
        for image in images[img_index:]:
            # images thumbnails are encoded in base64, we really only need those for small models... Can explore getting the source when needed.
            img_src = image.get_attribute("src");
            
            if img_src is None:
                print("Did not get an image for element...");
                print(image.id);
                continue;

            download_image(img_src);
            thread_task = Thread(target=download_image, args=(img_src,))
            threads.append(thread_task);
            thread_task.start()
        
            img_index = img_index + 1;
        
        for index, thread in enumerate(threads):
            thread.join();

def main():
    # Setup a browser for use to use and click around and scrape, bc we need to do that to get data now.
    chromedriver = "/opt/homebrew/bin/chromedriver";
    chromedriver_options = Options();
    # chromedriver_options.add_argument("--headless");
    
    browser: webdriver.Chrome = webdriver.Chrome(chromedriver, chrome_options=chromedriver_options);
    browser_wait = WebDriverWait(browser, 30);
    
    print("Google Boi, Google");
    
    # Nice blog that covers some url params we can use to scrape data
    # https://stenevang.wordpress.com/2013/02/22/google-advanced-power-search-url-request-parameters/
    # but screw it we only want some feet
    browser.get("https://www.google.com/search?q=hot+dirty+foot+fetish&tbm=isch");
    
    # We stop when I say we stop
    while True:
        
        # Grab related feed... //div[@data-hp='imgrc']//div[text()='See more']/parent::div/parent::a
        reference_images = browser.find_elements(by=By.XPATH, value="//div[@data-root-margin-pages]//img[@width]//parent::div//parent::div//parent::div");
        for reference_page_element in reference_images:
            jsname = reference_page_element.get_attribute("jsname");
            WebDriverWait(browser, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[@jsname='{}']".format(jsname))));
            
            reference_page_element.click();
            WebDriverWait(browser, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[@data-hp='imgrc']//div[text()='See more']/parent::div/parent::a")));
            see_more_element = browser.find_element(by=By.XPATH, value="//div[@data-hp='imgrc']//div[text()='See more']/parent::div/parent::a");
            see_more_link = see_more_element.get_attribute("href");
            browser.get(see_more_link);
            download_google_image_feed(browser, browser_wait);
            browser.back();
            
                
        
if __name__ == "__main__":
    main();

