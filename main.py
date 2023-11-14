import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from selenium.webdriver.remote.remote_connection import LOGGER


LOGGER.setLevel(logging.WARNING)
log = []
devices = {}

def logging(func):
    def wrapper( * args, ** kwargs):
        ip = ''.join(args)
        try:
            log.append(f"{threading.current_thread().getName()} is fetching data for {ip}")
            result = func( ''.join(args), ** kwargs)
            log.append(f"Function {func.__name__} executed successfully")
            return result
        except Exception as e:
            log.append(f"{ip} -> An error occurred while executing {func.__name__}: {e}")
    return wrapper


@logging
def get_signal(ip):
    # webdriver init
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")
    chrome_prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", chrome_prefs)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(5)
    # login to site
    driver = login(driver, "https://panel.wave.com.pl/?co=logowanie&redirect=%2F")
    # search for the node with the given ip
    try:
        driver.get(f"https://panel.wave.com.pl/?co=alias&alias={ip}")
    except:
        devices[ip] = ('-','-')
        return
    # get the node's host info table
    table = driver.find_element(By.CLASS_NAME, "dosrodka")
    tbody = table.find_element(By.TAG_NAME, "tbody")
    # fetch the rows of the table
    rows = tbody.find_elements(By.TAG_NAME, "tr")[1:] # skip the first row (header)
    # find the row that contains the given ip
    found = False
    row_index = 0
    for row in rows:
        tds = row.find_elements(By.CLASS_NAME, "edytowalny-text_ip-ip")
        for td in tds:
            # print(td.get_attribute("innerHTML"))
            a = td.find_element(By.TAG_NAME, "a")
            if a.get_attribute("innerHTML") == ip:
                # print(f"{ip} found")
                found = True
                break
        if found:
            rows[row_index].find_elements(By.TAG_NAME, "a")[2].click()
            break
        row_index += 1

    # get the signal strength table
    table = driver.find_element(By.CLASS_NAME, "dosrodka")
    rows = table.find_elements(By.TAG_NAME, "tr")[2] # select the row with monthly data
    tds = [rows.find_elements(By.TAG_NAME, "td")[index] for index in [9, 12]]
    monthlyBothAvg = tds[0].get_attribute("innerHTML")
    monthlyBoth1percent = tds[1].get_attribute("innerHTML")
    devices[ip] = (monthlyBothAvg, monthlyBoth1percent)
    driver.quit()

# login to site
def login(driver, url):
    driver.get(url)
    with open('.venv/password.txt', 'r') as f:
        password = f.readline().strip()
    try:
        driver.get("https://panel.wave.com.pl/?co=logowanie&redirect=%2F") # login page url
    except WebDriverException:
        print("Page down")
        exit()
    elem = driver.find_element(By.NAME, "pass")
    elem.clear()
    elem.send_keys(password + Keys.RETURN) # password 
    return driver

# read ips from file
with open ('ip.txt', 'r') as f:
    for line in f:
        devices[line.strip()] = ''

# create threads and start them
threads = []
for ip in devices.keys():
    thread = threading.Thread(target=get_signal, args=(ip,))
    threads.append(thread)
    thread.start()

# wait for all threads to finish
for thread in threads:
    thread.join()

# write output to file
with open('output.csv', 'w') as outputFile:
    outputFile.write("ip,avg,1%low\n")
    for ip in devices.keys():
        values = devices[ip]
        print(f"{ip}: {values}")
        try:
            outputFile.write(f'{ip},{values[0]},{values[1]}\n')
        except:
            outputFile.write(f'{ip},-,-\n')
        
# write log to file
with open('log.txt', 'w') as logFile:
    for line in log:
        logFile.write(line+"\n")