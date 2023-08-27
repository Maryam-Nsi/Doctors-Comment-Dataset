from selenium import webdriver
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
import pika
import json

rabbitmq_host = 'localhost'
exchange_name = 'doctor_data'
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host,heartbeat=500))
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
queue_name = "صف_نازایی و ناباروری"
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=queue_name)

firefox_binary = 'C:/Program Files/Mozilla Firefox/firefox.exe'
options = webdriver.FirefoxOptions()
options.binary_location = firefox_binary
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
actions = ActionChains(driver=driver)

driver.get("https://drdr.ir/search/expertise-10/?page=3")
driver.maximize_window()
sleep(10)

num_page = 1
index = 0
while(True):
    try:
        back = driver.find_element('xpath' , '//button[text()="بازگشت به لیست تخصص ها"]').click()
        break
    except:
        doctors_list = driver.find_elements('xpath' , '//div[@class="attr"]//a')
        ind_doctor = 2
        while ind_doctor < len(doctors_list):
            try:
                doctors_list = driver.find_elements('xpath' , '//div[@class="attr"]//a')
                sleep(10)
                doctor = doctors_list[ind_doctor]
                print(f"ind_doctor = {str(ind_doctor)}")
                ind_doctor += 1
                doctor.click()
            except:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", doctor)
                sleep(5)
                doctor.click()
            index += 1
            print(f"index : {str(index)}")
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
                        list_comment = driver.find_elements('xpath' , '//div[@class="rate rate-mobile"]//p')
                        sleep(5)
                        list_comment_star = driver.find_elements('xpath' , '(//div[@class="view-style"])')
                        sleep(5)
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
                        doctor_data_json = json.dumps(doctor_data)
                        channel.basic_publish(
                            exchange=exchange_name,
                            routing_key=queue_name,
                            body=doctor_data_json,
                            properties=pika.BasicProperties(
                                delivery_mode=2,
                            )
                        )
                        print("sent to rabbitMQ")
                        break
            driver.back()
        num_page += 1
        str_link = "https://drdr.ir/search/expertise-10/?page="
        str_link += str(num_page)
        driver.get(str_link)
        print("new page")
        sleep(10)
connection.close()
driver.quit()
    

