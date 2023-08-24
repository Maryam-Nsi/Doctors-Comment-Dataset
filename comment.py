from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pika
import json

rabbitmq_host = 'localhost'
exchange_name = 'doctor_data'
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host,heartbeat=500))
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name, exchange_type='direct')

queue_list = []
firefox_binary = 'C:/Program Files/Mozilla Firefox/firefox.exe'
options = webdriver.FirefoxOptions()
options.binary_location = firefox_binary
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
actions = ActionChains(driver=driver)

driver.get("https://drdr.ir/")
driver.maximize_window()
sleep(10)

button = driver.find_element('xpath', '//a[@class="style__StyledLink-sc-1eerurw-1 iQHcUq btnSize"]')
button.click()
sleep(20)

medical_branches = driver.find_elements('xpath', '//div[@class="card"]//div//a//h2')
count_medical_branches = len(medical_branches)
# print(count_medical_branches)

ind = 0
while ind < count_medical_branches:
    try:
        sleep(15)
        count_doctor = driver.find_elements('xpath' , '//*[contains(concat( " ", @class, " " ), concat( " ", "count", " " ))]')
        # print(int(count_doctor[ind].text))
        count_doctor_index = int(count_doctor[ind].text)
        medical_branches = driver.find_elements('xpath', '//div[@class="card"]//div//a//h2')
        sleep(40)
        branch = medical_branches[ind]
        print(f"branch_ind = {str(ind)}" + " " + f"{str(branch.text)}")
        queue_name = f"صف_{str(branch.text)}"
        queue_list.append(queue_name)
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=queue_name)
        ind += 1
        # print(str(ind) + " - " + branch.text + " ")
        branch.click()
        sleep(30)
        doctors_list = driver.find_elements('xpath' , '//div[@class="attr"]//a')
        index = 0
        for i in range (10):
            try:
                back = driver.find_element('xpath' , '//button[text()="بازگشت به لیست تخصص ها"]').click()
                break
            except:
                ind_doctor = 0
                while ind_doctor < len(doctors_list):
                    try:
                        doctors_list = driver.find_elements('xpath' , '//div[@class="attr"]//a')
                        sleep(30)
                        doctor = doctors_list[ind_doctor]
                        print(f"ind_doctor = {str(ind_doctor)}")
                        ind_doctor += 1
                        print(f"index = {str(index)}")
                        index += 1
                        sleep(5)
                        doctor.click()
                    except:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", doctor)
                        sleep(5)
                        doctor.click()
                    sleep(15)
                    try:
                        no_comment = driver.find_element('xpath' , '//div[text()="هنوز هیچ نظری برای این پزشک ثبت نشده است"]')
                    except:
                        while True:
                            try:
                                view_more = driver.find_element('xpath' , '//span[text()="مشاهده بیشتر نظر"]')
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", view_more)
                                sleep(10)
                                view_more.click()
                                sleep(20)
                            except:
                                dr_name = driver.find_element('xpath' , '//h1[contains(@class,"MuiTypography-root MuiTypography-h1")]').text
                                dr_specialty = driver.find_element('xpath' , "//h2[@data-cy='dr-speciality']").text
                                dr_city = driver.find_element('xpath' , "(//span[@class='icon-location']/following-sibling::span)[2]").text
                                # print(dr_name + dr_specialty + dr_city)
                                list_comment = driver.find_elements('xpath' , '//div[@class="rate rate-mobile"]//p')
                                sleep(10)
                                list_comment_star = driver.find_elements('xpath' , '(//div[@class="view-style"])')
                                sleep(10)
                                print("list comment:" + str(len(list_comment)))
                                print("list comment star: " + str(len(list_comment_star)))
                                ind_comment = 0
                                doctor_data = {
                                    "name": dr_name,
                                    "specialty": dr_specialty,
                                    "city": dr_city,
                                    "comments": [
                                        {
                                            "comment": list_comment[ind_comment].text,
                                            "rating": list_comment_star[ind_comment + 1].text
                                        }
                                        for ind_comment in range(len(list_comment))
                                    ]
                                }
                                # print(doctor_data)
                                doctor_data_json = json.dumps(doctor_data)
                                try:
                                    channel.basic_publish(
                                        exchange=exchange_name,
                                        routing_key=queue_name,
                                        body=doctor_data_json,
                                        properties=pika.BasicProperties(
                                            delivery_mode=2,
                                        )
                                    )
                                except Exception as e:
                                    print("An error occurred:", str(e))
                                break
                    driver.back()
                    sleep(20)
                next_page = driver.find_element('xpath' , '//div[text()="بعدی"]')
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page)
                sleep(10)
                next_page.click()
                sleep(30)
    except:
        page_el = driver.find_element('tag name', 'html')
        actions.send_keys_to_element(page_el, Keys.PAGE_DOWN).perform()
        sleep(10)
        branch.click()
        sleep(40)
        driver.back()
connection.close()
driver.quit()