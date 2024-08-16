from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Setup Chrome driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open the URL
driver.get('https://rabattparadiset.com/post-sitemap.xml')

# Allow some time for the page to load
time.sleep(3)

# Find the table with id 'sitemap'
table = driver.find_element(By.ID, 'sitemap')

# Find all 'a' tags within the table
a_tags = table.find_elements(By.TAG_NAME, 'a')

# Extract the href attributes
urls = [a.get_attribute('href') for a in a_tags]

# Reverse the order of the URLs
urls.reverse()

# Take only the first 10 URLs
urls = urls[:10]

# Open the CSV file in write mode
keys = ['discount;', 'store;', 'code;', 'exp;', 'type;', 'description;', 'link;', 'cat;', 'form;']
with open('discounts.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, fieldnames=keys)
    dict_writer.writeheader()
    
    # Function to extract information from each URL
    def extract_information(url):
        driver.get(url)
        time.sleep(2)  # Adjust if necessary based on loading time
        
        try:
            store_element = driver.find_element(By.CSS_SELECTOR, 'div.store-intro-content')
            store_header = store_element.find_element(By.CSS_SELECTOR, 'h1.h2.store-intro-title')
            store = store_header.text.split('rabattkod')[0].strip()
            print(store)

            div_elements = driver.find_elements(By.CSS_SELECTOR, 'div.mb-5.store-offers-litem')
            for div_element in div_elements:        
                h3_element = div_element.find_element(By.CSS_SELECTOR, 'h3.h5.mb-2')
                discount = h3_element.text
                print(discount)

                # Find the type element and then the a tag within it
                type_element = div_element.find_element(By.CSS_SELECTOR, 'div.store-offer-buttons.d-grid.gap-2.mt-4')
                type_a_tag = type_element.find_element(By.TAG_NAME, 'a')
                type_ = type_a_tag.text.replace('Visa', '').strip()
                type_ = "rabattkod" if type_ == "rabattkod" else "erbjudande"
                print(type_)

                # Extract the href attribute if type_ is 'rabattkod'
                link = type_a_tag.get_attribute('href') if type_ == 'rabattkod' else ''
                print(link)

                try:
                    validity_element = div_element.find_element(By.CSS_SELECTOR, 'div.store-offer-validity')
                    if validity_element.text != "Gäller tillsvidare":
                        expiration = validity_element.text.replace('Gäller till', '').strip()
                        print(expiration)
                    else:
                        expiration = validity_element.text
                        print(expiration)
                        
                except Exception as e:
                    expiration = ''
                code = ''
                if link:
                    # Setup a separate Chrome driver instance for the secondary task
                    secondary_service = Service(ChromeDriverManager().install())
                    secondary_driver = webdriver.Chrome(service=secondary_service)
                    try:
                        # Navigate to the link
                        secondary_driver.get(link)
                        time.sleep(2)  # Adjust if necessary based on loading time

                        # Find the modal-content and input field
                        modal_content = secondary_driver.find_element(By.CSS_SELECTOR, 'div.modal-content.py-3')
                        coupon_code_input = modal_content.find_element(By.ID, 'field-coupon-code')
                        code = coupon_code_input.get_attribute('value').strip()
                        print(code)
                    except Exception as e:
                        code = ''
                    finally:
                        secondary_driver.quit()  # Ensure the new driver instance is closed

                row = {
                    'discount;': discount,
                    'store;': store,
                    'code;': code,
                    'exp;': expiration,
                    'type;': type_
                }
                dict_writer.writerow(row)

        except Exception as e:
            print(f"Error extracting information from {url}: {e}")

    # Loop through each URL and extract information
    for url in urls:
        extract_information(url)

# Close the main browser
driver.quit()

print(f"Extracted information from {len(urls)} URLs and saved to discounts.csv")
