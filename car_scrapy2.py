import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

# CSV file paths
csv_file_path = '/home/alibi/Documents/Python/Car Tracker/combined_data/combined_csv.csv'
new_csv_file_path = '/home/alibi/Documents/Python/Car Tracker/output_csvs/flag.csv'

#Global list to store combined data
combined_data = []

def navigate_to_dashboard(driver, url):
    driver.get(url)
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, 'filterVin'))
        )
        return True
    except TimeoutException:
        print("Page load timeout or element not found")
        return False

def wait_for_manual_action(driver):
    input("Login in the browser and then press enter to continue...")

def click_and_scrape(driver, no_sale_link, vin, selling_dealership, vehicle):
    try:
        no_sale_link.click()

        #Wait for the popup to appear
        popup_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.in.fade.modal > .modal-dialog > .modal-content'))
        )

        #Now interact with elements inside the popup_element
        popup_html = popup_element.get_attribute('innerHTML')

        soup = BeautifulSoup(popup_html, 'html.parser')

        #Extract Orig. Closing Price
        orig_closing_price_div = soup.find('label', text='Orig. Closing Price').find_next_sibling('div')
        orig_closing_price = orig_closing_price_div.text.strip() if orig_closing_price_div else 'N/A'

        #Extract Floor Price
        floor_price_div = soup.find('label', text='Floor Price').find_next_sibling('div')
        floor_price = floor_price_div.text.strip() if floor_price_div else 'N/A'

        print("Floor Price:", floor_price)
        print("Orig. Closing Price:", orig_closing_price)

        #Combine data
        combine_data(vin, selling_dealership, vehicle, floor_price, orig_closing_price)

        #Add a short delay to ensure the element is fully interactive
        time.sleep(1)

        #Press Esc key to close the modal
        driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.ESCAPE)

        #Ensure the modal dialog is closed
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, '.in.fade.modal > .modal-dialog > .modal-content'))
        )

        time.sleep(1)

    except TimeoutException:
        print("The modal popup did not appear in the expected time frame")
    except NoSuchElementException:
        print("Could not find the necessary elements in the modal popup")
    except Exception as e:
        print(f"An error occurred: {e}")

def search_by_vin(driver, vin, selling_dealership, vehicle):
    try:
        #First clear the VIN search field
        search_field = driver.find_element(By.ID, 'filterVin')
        search_field.clear()
        search_field.send_keys(vin)

        #Submit the search
        search_button = driver.find_element(By.XPATH, '//button[@type="submit" and @class="btn btn-primary form-control"]')
        search_button.click()

        #Loading time
        time.sleep(2)

        no_sale_links = driver.find_elements(By.XPATH, '//a[text()="No Sale"]')

        if no_sale_links:
            click_and_scrape(driver, no_sale_links[0], vin, selling_dealership, vehicle)
    except Exception as e:
        print(f"An error occurred during VIN search: {e}")

def combine_data(vin, selling_dealership, vehicle, floor_price, orig_closing_price):
    combined_data.append([vin, selling_dealership, vehicle, floor_price, orig_closing_price])

def save_combined_data_to_csv():
    with open(new_csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['VIN', 'Selling Dealership', 'Vehicle', 'Floor Price', 'Orig. Closing Price'])
        writer.writerows(combined_data)

def main():
    #Initialize driver for browser
    driver = webdriver.Firefox()

    #If pages fail to load, exit gracefully
    if not navigate_to_dashboard(driver, 'https://tools.acvauctions.com/auctions/dashboard'):
        driver.quit()
        return

    #Allow user to manually enter login for 2FA reasons
    wait_for_manual_action(driver)

    #Read CSV to get VIN, Selling Dealership, and Vehicle
    df = pd.read_csv(csv_file_path)

    #Iterate through each row in CSV
    for index, row in df.iterrows():
        vin = row['VIN']
        selling_dealership = row['Selling Dealership']
        vehicle = row['Vehicle']
        search_by_vin(driver, vin, selling_dealership, vehicle)

    #Save combined data to new CSV
    save_combined_data_to_csv()

    driver.quit()

if __name__ == "__main__":
    main()
