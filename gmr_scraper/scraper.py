from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
import csv
import os

def reset_output_csv(csv_filename):
    if os.path.exists(csv_filename):
        os.remove(csv_filename)
        
def generate_csv_filename(base_path='output/by', date_format='%Y%m%d_%H%M%S', sort='default'):
    current_time = datetime.now().strftime(date_format)
    return f'{base_path}_{sort}_{current_time}.csv'

def read_input_csv(filename):
    with open(filename, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        return list(csv_reader)

def scroll_and_expand_reviews(driver, timeout=2, max_scroll_attempts=25):
    print("Scrolling down to load reviews and turn off auto-translation...")
    actions = ActionChains(driver)
    previous_length = 0
    scroll_attempts = 0
    scroll_counter = 0

    while scroll_attempts < max_scroll_attempts:
        actions.send_keys(Keys.PAGE_DOWN).perform()
        scroll_counter += 1
        time.sleep(0.2)  # Wait for the page

        # Click all "Show More" buttons
        show_more_buttons = driver.find_elements(By.CSS_SELECTOR, ".w8nwRe.kyuRq")
        for button in show_more_buttons:
            try:
                driver.execute_script("arguments[0].click();", button)
            except:
                pass  # Ignore errors if button is not clickable or not found

        # Click all buttons with class "kyuRq fontTitleSmall WOKzJe" where aria-checked="true"
        filter_buttons = driver.find_elements(By.CSS_SELECTOR, ".kyuRq.fontTitleSmall.WOKzJe")
        for button in filter_buttons:
            try:
                if button.get_attribute("aria-checked") == "true":
                    driver.execute_script("arguments[0].click();", button)
            except:
                pass  # Ignore errors if button is not clickable or not found

        # Extract the current set of reviews
        current_reviews = driver.find_elements(By.CLASS_NAME, "wiI7pd")

        # Check if the number of reviews has increased
        if len(current_reviews) > previous_length:
            previous_length = len(current_reviews)
            scroll_attempts = 0  # Reset the counter since new reviews were found
        elif scroll_attempts == 20:
            time.sleep(2)
            scroll_attempts += 1
        else:
            scroll_attempts += 1  # Increment the counter if no new reviews are found

        time.sleep(timeout)
        
    # Scroll back to the top
    print("Scrolling back to page top...")
    scroll_attempts2 = 0
    while scroll_attempts2 <= scroll_counter:
        actions.send_keys(Keys.PAGE_UP).perform()
        time.sleep(timeout)
        scroll_attempts2 += 1

def safe_extract(element, class_name, attribute=None):
    try:
        if attribute:
            return element.find_element(By.CLASS_NAME, class_name).get_attribute(attribute)
        else:
            return element.find_element(By.CLASS_NAME, class_name).text
    except NoSuchElementException:
        return 'NA'

def scroll_and_extract_reviews(driver, csv_filename, location_name, location_status, timeout=2, max_scroll_attempts=10):
    print("Scrolling down and extracting reviews...")
    actions = ActionChains(driver)
    file_exists = os.path.exists(csv_filename)  # Check if the file already exists

    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:  # Open file in append mode
        writer = csv.writer(file)
        if not file_exists:  # If the file does not exist, write the header
            header = ['Location', 'Status', 'Reviewer', 'Rating', 'Relative time', 'Scraping time', 'Review']
            writer.writerow(header)

        previous_length = 0
        scroll_attempts = 0

        while scroll_attempts < max_scroll_attempts:
            actions.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(timeout)  # Wait for the page

            # Click all "Show More"
            review_containers = driver.find_elements(By.CLASS_NAME, "jJc9Ad")

            # Check if the number of review containers has increased
            if len(review_containers) > previous_length:
                # Iterate over new reviews since the last time
                for review_container in review_containers[previous_length:]:
                    reviewer = safe_extract(review_container, "d4r55")
                    review_text = safe_extract(review_container, "wiI7pd")
                    rating = safe_extract(review_container, "kvMYJc", attribute="aria-label")
                    relative_time = safe_extract(review_container, "rsqaWe")
                    scraping_time = datetime.now().strftime("%Y-%m-%d,%H:%M:%S")

                    # Write the review to the CSV file
                    writer.writerow([location_name, location_status, reviewer, rating, relative_time, scraping_time, review_text])

                previous_length = len(review_containers)
                scroll_attempts = 0
            else:
                scroll_attempts += 1

            time.sleep(timeout)

def click_sort_option(driver, option='default'):
    print(f"Reviews sorting order is now by [{option}]...")
    # If no option is specified, return without doing anything
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
        sort_buttons = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'DVeyrd'))
        )
        sort_buttons[2].click()

        time.sleep(0.5)

        submenu_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f".fxNQSd[data-index='{sort_options[option]}']"))
        )
        submenu_option.click()

    except KeyError:
        print(f"The option '{option}' is not recognized. Available options are: {list(sort_options.keys())}")
    except Exception as e:
        print(f"An error occurred: {e}")

try:
    sort_option = 'newest' # Change this to 'most_relevant', 'newest', 'highest_rating', or 'lowest_rating'
    
    output_filename = generate_csv_filename(sort=sort_option)
    
    chrome_options = Options()
    chrome_options.add_argument("--lang=en-GB")  # EN
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en-GB'})
    # chrome_options.add_argument("--headless")  # Uncomment to run Chrome in headless mode

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    input_data = read_input_csv(r'input\urls.csv')
    location_list = []
    
    for data in input_data:
        url = data['URL']
        location_name = data['Location']
        location_status = data['Status']
        driver.get(url)
        location_list.append(location_name)

        print(f"Scraping Google Maps Reviews for [{location_name}]...")

        # Wait for the button with jsname='tWT92d' to be present and clickable, to handle the cookie pop-up
        try:
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[jsname='tWT92d']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
            close_button.click()
            print("Cookie popup closed.")
        except Exception as e:
            pass
        
        # Call the click_sort_option function to sort the reviews by 'newest'
        click_sort_option(driver, sort_option)

        # Scroll and click "Show More" until all reviews are expanded or until 10 scroll attempts with no new reviews
        scroll_and_expand_reviews(driver, timeout=0.1, max_scroll_attempts=10)

        # Extract the reviews and write them to the output CSV file
        scroll_and_extract_reviews(driver, output_filename, timeout=0.1, location_name=location_name, location_status=location_status)  # Pass the location name
        
        print(f"Scraping Google Maps Reviews for [{location_name}] is finished.")

        time.sleep(0.5)
        
    print(f"Finished scraping reviews for the following locations: {location_list}")
    print(f"Output file: {output_filename}")
    input("Press Enter to exit chromedriver...")  # Keep the window open until presses Enter

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()