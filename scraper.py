from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def click_sort_option(driver, option):
    # Dictionary mapping the option parameter to the data-index
    sort_options = {
        'most_relevant': '0',
        'newest': '1',
        'highest_rating': '2',
        'lowest_rating': '3',
    }

    try:
        # Find all elements with the class name 'DVeyrd'
        sort_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'DVeyrd'))
        )

        # Click the second sort button (index 1 since indexing starts at 0)
        sort_buttons[2].click()

        # Wait for a short delay to allow the submenu to animate in, if necessary
        time.sleep(2)  # Adjust the delay time as needed

        # Wait for the submenu to appear and find the option with the correct data-index
        submenu_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f".fxNQSd[data-index='{sort_options[option]}']"))
        )

        # Click the specified submenu option
        submenu_option.click()

    except KeyError:
        print(f"The option '{option}' is not recognized. Available options are: {list(sort_options.keys())}")
    except Exception as e:
        print(f"An error occurred: {e}")

try:
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--lang=en")  # Set language to English
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
    
    time.sleep(2)
    
    # Call the click_sort_option function to sort the reviews by 'newest'
    click_sort_option(driver, 'newest')

    # Keep the window open, or perform some actions, or wait for some element or user input
    input("Press Enter to quit...")  # Keep the window open until user presses Enter

except Exception as e:
    print(f"An error occurred: {e}")

#finally:
    # Close the driver after you are done
    #driver.quit()