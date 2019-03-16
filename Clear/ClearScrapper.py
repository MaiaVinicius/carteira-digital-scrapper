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

        wait = WebDriverWait(self.driver, 20)
        element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "value-total")))

        sleep(2)
        try:
            total_amount = self.driver.find_element_by_class_name("value-total").text
            in_account_amount = self.driver.find_element_by_xpath('//*[@id="view-list"]/li[2]/a/div[2]/span[1]/i[2]').text

            applications = {
                "in_account": in_account_amount,
                "total": total_amount,
                "stock": [],
                "applications": [
                    {

                    },
                    {

                    },
                    {
                        'label': 'Garantias',
                        'amount': self.driver.find_element_by_xpath(
                            '//*[@id="view-list"]/li[2]/a/div[3]/label[2]/span[2]').text
                    }
                ]
            }
        except Exception as e:
            print(e)
            pass

        # adiciona os dados de acoes
        renda_variavel_btn = self.driver.find_element_by_xpath('//*[@id="view-list"]/li[2]/a')
        renda_variavel_btn.click()

        sleep(2)

        stocks_container = self.driver.find_element_by_class_name('container_left_myast_two')
        stocks = stocks_container.find_elements_by_class_name('stock')

        for stock in stocks:
            stock.click()

            sleep(14)

            stock_info_container = self.driver.find_element_by_class_name('container_equities')
            qtd = stock_info_container.find_element_by_class_name('position-quantity').text
            stock_current_total = stock_info_container.find_element_by_class_name('asset-value-current').text
            buy_total = stock_info_container.find_element_by_class_name('position-value-aquisition').text
            symbol_description = stock_info_container.find_element_by_class_name('asset-symbol').text

            symbol_description_split = symbol_description.split(" / ")
            symbol = symbol_description_split[0]
            description = ""

            applications["stock"].append({
                "qtd": qtd,
                "current_total": stock_current_total,
                "buy_total": buy_total,
                "symbol": symbol,
                "description": description,
            })

        return applications
