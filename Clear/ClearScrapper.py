# coding=utf-8
from pprint import pprint
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ClearScrapper:
    initial_url = "https://www.clear.com.br/pit/signin?controller=SignIn"
    driver = None

    cpf = None
    password = None
    birthdate = None

    def __init__(self, cpf, password, birthdate):
        self.cpf = cpf
        self.password = password
        self.birthdate = birthdate

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
        cpf_ipt = self.driver.find_element_by_id("identificationNumber")
        cpf_ipt.send_keys(self.cpf)

        pwd_ipt = self.driver.find_element_by_id("password")
        pwd_ipt.send_keys(self.password)

        birthdate_ipt = self.driver.find_element_by_id("dob")
        birthdate_ipt.send_keys(self.birthdate)

        submit_btn = self.driver.find_element_by_class_name("bt_signin")
        submit_btn.click()

    def wait_login(self):
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.ID, "wide")))
        print("Login finished")

        self.driver.get("https://www.clear.com.br/pit/Selector/ToNew")

        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "logo_header")))
        print("Login finished")

    def scrap(self):
        self.driver.switch_to.frame(self.driver.find_element_by_class_name("ifm"))

        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "value-total")))

        sleep(2)

        total_amount = self.driver.find_element_by_class_name("value-total").text
        in_account_amount = self.driver.find_element_by_xpath('//*[@id="legend-list"]/div[2]/label/span[2]').text

        return {
            "in_account": in_account_amount,
            "total": total_amount,
            "applications": [
                {
                    'label': 'Renda Fixa',
                    'amount': self.driver.find_element_by_xpath('//*[@id="legend-list"]/div[1]/label[2]/span[2]').text
                },
                {
                    'label': 'Renda Variável',
                    'amount': self.driver.find_element_by_xpath('//*[@id="legend-list"]/div[1]/label[1]/span[2]').text
                },
                {
                    'label': 'Garantias',
                    'amount': self.driver.find_element_by_xpath('//*[@id="view-list"]/li[2]/a/div[3]/label[2]/span[2]').text
                }
            ]
        }
