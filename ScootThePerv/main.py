from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from mimetypes import guess_extension;
from base64 import b64decode;
from threading import Thread;
import requests;
import random;

def download_image(img_src):
    img_index = hash(img_src);
    if img_src.startswith("http"):
        # Gotta stream it if it is big
        img_response = requests.get(img_src, stream=True);
        mime_type = img_response.headers['content-type']
        file_extension = guess_extension(mime_type);
        output_file = "./data/image_{}{}".format(img_index, file_extension);
        with open(output_file, "wb") as image:
            for buffer_data in img_response.iter_content():
                image.write(buffer_data);
        print("Wrote an image: " + output_file);
        
    elif img_src.startswith("data:image"):
        mime_type = img_src[:img_src.index(";")].split(":")[1];
        file_extension = guess_extension(mime_type);
        output_file = "./data/image_{}{}".format(img_index, file_extension);
        with open(output_file, "wb") as image:
            image.write(b64decode(img_src[img_src.index(","):]));
        print("Wrote an image: " + output_file);
    
    else:
        print("Image not supported" + img_src[:55]);
    

def main():
    # Setup a browser for use to use and click around and scrape, bc we need to do that to get data now.
    chromedriver = "/opt/homebrew/bin/chromedriver";
    chromedriver_options = Options();
    # chromedriver_options.add_argument("--headless");
    
    browser = webdriver.Chrome(chromedriver, chrome_options=chromedriver_options);
    browser_wait = WebDriverWait(browser, 30);
    
    print("Google Boi, Google");
    
    # Nice blog that covers some url params we can use to scrape data
    # https://stenevang.wordpress.com/2013/02/22/google-advanced-power-search-url-request-parameters/
    # but screw it we only want some feet
    browser.get("https://www.google.com/search?q=hot+sexy+foot+feet+pics+fetish&tbm=isch");
    
    img_index = 0;
    
    # We stop when I say we stop
    while True:
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
        
            thread_task = Thread(target=download_image, args=(img_src,))
            threads.append(thread_task);
            thread_task.start()
        
            img_index = img_index + 1;
        
        for index, thread in enumerate(threads):
            thread.join();
        
        
        # Need to keep forcing scrolling...
        while True:
            try:
                print("Scrolling down to bottom");
                browser.execute_script("window.scrollBy(0, document.body.scrollHeight)");
                try:
                    show_more_button = WebDriverWait(browser, 1).until(expected_conditions.visibility_of_element_located((By.XPATH, "//input[@value='Show more results']")))
                    print(show_more_button);
                    print("Checking is show button is there");
                    show_more_button.click();
                except:
                    pass;
                
                browser_wait.until(
                    expected_conditions.presence_of_element_located((By.XPATH, "(//div[@data-root-margin-pages]//img[@width])[{}]".format(img_index+1)))
                );
                break;
            except:
                print("Failed to scroll to the bottom for some reason...");
                pass;
                
        
if __name__ == "__main__":
    main();

