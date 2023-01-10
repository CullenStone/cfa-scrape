from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import argparse
import us
import json
import time

# 1. Open webpage
# 2. Check if it needs to authorize/agree to terms
# 3. Loop through the states
# 4. Get the total number of pages
# 5. Scrape current page -> parse and throw in a data frame
# 6. Go to next page

def login(driver, username, password):
    """
        We will use the command line user name and password
    """
    login_url = "https://directory.cfainstitute.org/account/login?returnUrl=https://directory.cfainstitute.org/"
    
    driver.get(login_url)
    time.sleep(2)
    driver.find_element(By.XPATH, '//input[@id="email_withoutPattern"]').send_keys(username)

    next_button = driver.find_element(By.ID, 'next')
    next_button.click()
    
    time.sleep(3)

    driver.find_element(By.XPATH, '//input[@id="password"]').send_keys(password)
    submit_button = driver.find_element(By.ID, 'next')
    submit_button.click()




def authorize(driver):
    """
        If the webpage asks to check a box, this function will perform that action
    """
    checkbox = driver.find_element(By.XPATH, '//div[@class="checkbox"]')
    checkbox.click()

    search = driver.find_element(By.XPATH, '//div[@class="field-button"]')
    search.click()

def scrape_state(driver, url):

    driver.get(url)
    try:
        authorize(driver)
    except:
        pass
    
    num_pages = int(driver.find_element(By.XPATH, '//div[@class="cfa-pagination-pages"]').text.split(' ')[-1])
    num_results = int(driver.find_element(By.XPATH, '//span[@class="md-results-returned-number"]').text)
    
    print('Num pages:',num_pages)
    print(f"Results: {num_results}")

    current_url = driver.current_url


    details = []
    for i in range(1,num_pages + 1, 1):
        try:
            authorize(driver)
        except:
            pass
        finally:
            try:
                cards = driver.find_element(By.XPATH, '//ul[@class="md-results list-unstyled grid-layout"]')
                names = cards.text.split('View Profile')

                split_names = [x.split('\n') for x in names]

                for n in split_names:
                    details.append([x for x in n if x])

                driver.get(current_url + f'&page={i}')
            except:
                print(f"skipping {driver.current_url}")

    return details

def main(args):

    with open('scraped.json', 'r') as i:
        state_catalog = json.load(i)

    scraped_states = state_catalog.get('states')
    unused = []
    details = []
    # Loop through the states here
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # Figure out which states have been scraped

    # We need to log in here
    login(driver, args.username, args.password)

    time.sleep(3)
    
    #driver.maximize_window()
    states = [state.name for state in us.states.STATES_AND_TERRITORIES] if args.state is None else [args.state]

    for state in states:
        if state in scraped_states:
            print('Skipping', state)
            continue

        all_df = []

        print(state)
        URL = f'https://directory.cfainstitute.org/search?location={state}%2C+USA'
        try:
            details = scrape_state(driver, URL)
            count_of_results = 0
            two_elements = {}
            three_elements = {}
            four_elements = {}
            for i, n in enumerate(details):
                if len(n) == 2:
                    two_elements[i] = dict(zip(['Name', 'City'], n))
                    count_of_results += 1
                elif len(n) == 3:
                    three_elements[i] = dict(zip(['Name', 'Position', 'City'], n))
                elif len(n) == 4:
                    four_elements[i] = dict(zip(['Name', 'Position', 'Company', 'City'], n))
                    count_of_results += 1
                else:
                    unused.append(n)

            dfs = []
            df2 = pd.DataFrame.from_dict(two_elements, orient='index')
            df2.insert(1, 'Position', 0)
            df2.insert(2, 'Company', 0)
            dfs.append(df2)
            if len(three_elements) > 0:
                df3 = pd.DataFrame.from_dict(three_elements, orient='index')
                df3.insert(1, 'Position', 0)
                dfs.append(df3)
            df4 = pd.DataFrame.from_dict(four_elements, orient='index')
            dfs.append(df4)
            all_df.append(pd.concat(dfs))


            print(f"Results used: {count_of_results}")
            count_of_results = 0

        except Exception as e:
            print(e)

        try:
            pd.concat(all_df, ignore_index = True).to_csv(f'states/{state}.csv', index=False)
        except:
            breakpoint()
        scraped_states.append(state)
        state_catalog['states'] = scraped_states
        with open('scraped.json', 'w') as outfile:
            json.dump(state_catalog, outfile, indent=4)

    with open('unused.txt', 'a') as o:
        for u in unused:
            o.writelines(u)

if __name__ == '__main__':

    parse = argparse.ArgumentParser(description="This will scrape for names")
    parse.add_argument('-u', '--username', dest='username', type=str, required = True, help="The username of the account")
    parse.add_argument('-p', '--password', dest='password', type=str, required = True, help="The password of the account")
    parse.add_argument('--state', '-s', dest='state', type=str, default=None)

    args = parse.parse_args()

    main(args)


