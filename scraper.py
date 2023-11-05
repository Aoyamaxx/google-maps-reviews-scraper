from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
import csv

def scroll_and_expand_reviews(driver, timeout=2, max_scroll_attempts=10):
    actions = ActionChains(driver)
    previous_length = 0
    scroll_attempts = 0
    scroll_counter = 0

    while scroll_attempts < max_scroll_attempts:
        # Scroll down once
        actions.send_keys(Keys.PAGE_DOWN).perform()
        scroll_counter += 1
        time.sleep(timeout)  # Wait for the page to potentially load more items

        # Try to click all "Show More" buttons to expand truncated reviews
        show_more_buttons = driver.find_elements(By.CSS_SELECTOR, ".w8nwRe.kyuRq")
        for button in show_more_buttons:
            try:
                driver.execute_script("arguments[0].click();", button)
            except:
                pass  # Ignore errors if button is not clickable or not in view

        # Extract the current set of reviews
        current_reviews = driver.find_elements(By.CLASS_NAME, "wiI7pd")

        # Check if the number of reviews has increased
        if len(current_reviews) > previous_length:
            previous_length = len(current_reviews)
            scroll_attempts = 0  # Reset the counter since new reviews were found
        else:
            scroll_attempts += 1  # Increment the counter if no new reviews are found

        # Wait a bit before the next scroll attempt
        time.sleep(timeout)
        
    scroll_attempts2 = 0

    while scroll_attempts2 <= scroll_counter:
        # Scroll up once
        actions.send_keys(Keys.PAGE_UP).perform()
        time.sleep(timeout)  # Wait for the page to potentially load previous items
        scroll_attempts2 += 1

def safe_extract(element, class_name, attribute=None):
    """Safely extract information from an element, return 'NA' if not found."""
    try:
        if attribute:
            return element.find_element(By.CLASS_NAME, class_name).get_attribute(attribute)
        else:
            return element.find_element(By.CLASS_NAME, class_name).text
    except NoSuchElementException:
        return 'NA'

def scroll_and_extract_reviews(driver, csv_filename, timeout=2, max_scroll_attempts=10):
    # Initialize ActionChains
    actions = ActionChains(driver)

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Define the header with the column names
        header = ['Location', 'Reviewer', 'Rating', 'Relative time', 'Scraping time', 'Review']
        # Write the header row
        writer.writerow(header)

        previous_length = 0
        scroll_attempts = 0

        while scroll_attempts < max_scroll_attempts:
            # Scroll down once
            actions.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(timeout)  # Wait for the page to potentially load more items

            # Extract the review container elements
            review_containers = driver.find_elements(By.CLASS_NAME, "jJc9Ad")

            # Check if the number of review containers has increased
            if len(review_containers) > previous_length:
                # Iterate over new reviews since the last time
                for review_container in review_containers[previous_length:]:
                    reviewer = safe_extract(review_container, "d4r55")
                    review_text = safe_extract(review_container, "wiI7pd")
                    rating = safe_extract(review_container, "kvMYJc", attribute="aria-label")
                    relative_time = safe_extract(review_container, "rsqaWe")
                    scraping_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Write the extracted information to the CSV file
                    writer.writerow(['NA', reviewer, rating, relative_time, scraping_time, review_text])

                previous_length = len(review_containers)
                scroll_attempts = 0  # Reset the counter since new reviews were found
            else:
                scroll_attempts += 1  # Increment the counter if no new reviews are found

            # Wait a bit before the next scroll attempt
            time.sleep(timeout)

def click_sort_option(driver, option='default'):
    # If the option is 'default', we do nothing and return immediately
    if option == 'default':
        return

    # Dictionary mapping the option parameter to the data-index
    sort_options = {
        'most_relevant': '0',
        'newest': '1',
        'highest_rating': '2',
        'lowest_rating': '3'
    }

    try:
        # Click the sort button to open the submenu
        sort_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'DVeyrd'))
        )
        sort_buttons[2].click()

        # Wait for a short delay to allow the submenu to animate in, if necessary
        time.sleep(2)

        # Wait for the submenu to appear and find the option with the correct data-index
        submenu_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f".fxNQSd[data-index='{sort_options[option]}']"))
        )
        submenu_option.click()

    except KeyError:
        print(f"The option '{option}' is not recognized. Available options are: {list(sort_options.keys())}")
    except Exception as e:
        print(f"An error occurred: {e}")

try:
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--lang=en-GB")  # Set language to English
    # chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en'})
    # chrome_options.add_argument("--headless")  # Uncomment if you want to run Chrome in headless mode

    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Open the specified URL
    url = "https://www.google.com/maps/place/Gaasperplas/@52.3069241,4.9864444,16z/data=!4m12!1m2!2m1!1sGaasperplas!3m8!1s0x47c60c5dbd560937:0xd8ce181a2c1f975b!8m2!3d52.3058653!4d4.994065!9m1!1b1!15sCgtHYWFzcGVycGxhc1oNIgtnYWFzcGVycGxhc5IBBGxha2WaASNDaFpEU1VoTk1HOW5TMFZKUTBGblNVUmhYelpwWkVGbkVBReABAA!16s%2Fg%2F11bc656tmn?entry=ttu"
    driver.get(url)
    
    # Wait for the button with jsname='tWT92d' to be present and clickable
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[jsname='tWT92d']"))
    )

    # Scroll the close_button element into view
    driver.execute_script("arguments[0].scrollIntoView(true);", close_button)

    # Click the close_button
    close_button.click()
    
    # Call the click_sort_option function to sort the reviews by 'newest'
    click_sort_option(driver, 'newest')
    
    # Scroll and click "Show More" until all reviews are expanded or until 10 scroll attempts with no new reviews
    scroll_and_expand_reviews(driver, timeout=0.1, max_scroll_attempts=10)

    # Extract the reviews and write them to a CSV file
    scroll_and_extract_reviews(driver, 'reviews.csv', timeout=0.1)

    # Keep the window open, or perform some actions, or wait for some element or user input
    input("Press Enter to quit...")  # Keep the window open until user presses Enter

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the driver after you are done
    driver.quit()