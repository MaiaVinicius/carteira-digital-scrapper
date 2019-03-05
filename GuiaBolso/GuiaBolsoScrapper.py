# coding=utf-8
from pprint import pprint
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GuiaBolsoScrapper:
    initial_url = "https://www.guiabolso.com.br/comparador/#/login"
    driver = None

    email = None
    birthdate = None

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def init(self):
        path = "/Users/maiavinicius/PycharmProjects/minha_carteira/driver/chromedriver-mac"
        self.driver = webdriver.Chrome(path)

        self.driver.get(self.initial_url)
        self.login()
        self.wait_login()
        res = self.scrap()

        self.driver.close()

        return res

    def login(self):
        sleep(5)

        email_ipt = self.driver.find_element_by_xpath('//*[@id="app"]/div/div/div/main/form/div[1]/input')
        email_ipt.send_keys(self.email)

        pwd_ipt = self.driver.find_element_by_xpath('//*[@id="app"]/div/div/div/main/form/div[2]/input')
        pwd_ipt.send_keys(self.password)

        submit_btn = self.driver.find_element_by_xpath('//*[@id="app"]/div/div/div/main/form/p[1]/span/button')
        submit_btn.click()

        return

    def wait_login(self):
        wait = WebDriverWait(self.driver, 120)
        element = wait.until(EC.visibility_of_element_located((By.ID, "root")))
        print("Login finished")

    def scrap(self):

        sleep(8)

        total = self.driver.find_element_by_class_name('hEMTnY')

        total_balance_btn = self.driver.find_element_by_class_name('eIwspU')

        total_balance_btn.click()

        sleep(2)

        main_content = self.driver.find_element_by_class_name('bYNpJH')
        i = 0

        accounts = main_content.find_elements_by_class_name('hNKaST')

        applications = {
            'accounts': [],
            'overview': []
        }

        sleep(2)

        overview_card = main_content.find_element_by_class_name('mVzbU')
        overview_lines = overview_card.find_elements_by_class_name('dmQSRW')
        for overview_line in overview_lines:
            overview_name = overview_line.find_element_by_class_name('jss97').text
            overview_amount = overview_line.find_element_by_class_name('jss93').text

            applications['overview'].append({
                'name': overview_name,
                'amount': overview_amount,
            })

        for account in accounts:
            try:
                name = account.find_element_by_class_name('sc-cHGsZl')

                name = name.find_element_by_css_selector('h1').text

                sub_accounts = account.find_elements_by_class_name('gprueo')
                sub_applications = []

                for sub_account in sub_accounts:
                    sub_account_name = sub_account.find_element_by_class_name('jss98').text
                    sub_account_type = sub_account.find_element_by_class_name('jss97').text
                    sub_account_amount = sub_account.find_element_by_class_name('jss93').text

                    sub_applications.append({
                        'application_name': sub_account_name,
                        'application_type': sub_account_type,
                        'amount': sub_account_amount
                    })

                data = {
                    'account_name': name,
                    'applications': sub_applications
                }

                applications['accounts'].append(data)
            except Exception as e:
                print("Error ocurred")
                print(e)
                pass

        return applications
