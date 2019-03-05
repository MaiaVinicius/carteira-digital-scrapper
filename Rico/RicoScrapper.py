# coding=utf-8
from pprint import pprint
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RicoScrapper:
    initial_url = "https://www.rico.com.vc/login/"
    driver = None

    username = None  # type: str
    password = None  # type: int

    def __init__(self, username, password):
        """
        :param username: O usuário de acesso à corretora
        :param password: Senha numérica 6 digitos
        """
        self.username = username
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

    def skip_intro(self):
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "introjs-skipbutton")))
        element.click()
        sleep(1)

        print("Intro Skiped")

    def scrap(self):
        self.skip_intro()

        print("Scrapping ... ")

        table = self.driver.find_element_by_id("tableAllocatedValue")

        rows = table.find_element_by_css_selector("tbody").find_elements_by_class_name("user-select-none")
        balance = {
            "applications_summary": [],
            "applications": [],
            "in_account": self.driver.find_element_by_xpath('//*[@id="tableAllocatedValue"]/tfoot/tr[2]/td[4]').text,
            ''
            "total": self.driver.find_element_by_xpath('//*[@id="tableAllocatedValue"]/tfoot/tr[3]/td[4]').text
        }

        for row in rows:
            tds = row.find_elements_by_css_selector('td')

            try:
                label = tds[0].text
                percentage = tds[1].text
                applied = tds[2].text
                amount = tds[3].text

                balance["applications_summary"].append({
                    "label": label,
                    "percentage": percentage,
                    "applied": applied,
                    "amount": amount
                })
            except:
                pass

        self.driver.get('https://www.rico.com.vc/dashboard/renda-fixa/')

        try:
            fixed_income = self.driver.find_element_by_id('tableAllocatedValue')

            tbody = fixed_income.find_element_by_css_selector('tbody')
            trs = tbody.find_elements_by_css_selector('tr')

            for tr in trs:
                try:
                    tds = tr.find_elements_by_css_selector('td')

                    balance['applications'].append({
                        'type': 'fixed_income',
                        'type_id': 9,
                        'description': tds[0].text,
                        'initial_balance': tds[4].text,
                        'balance': tds[5].text,
                        'buy_date': tds[2].text,
                        'profitability': tds[1].text,
                        'expires': tds[3].text
                    })
                except:
                    pass

        except:
            pass

        return balance

    def wait_login(self):
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.ID, "homeBrokerLink")))
        print("Login finished")

    def login(self):
        self.fill_username()
        self.fill_password()

        print("Login submitted")

    def fill_username(self):
        #         preenche o username
        user_input = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div[1]/input')
        user_input.send_keys(self.username)

        #         aperta enter
        submit_btn = self.driver.find_element_by_xpath('//*[@id="loginForm"]/button')
        submit_btn.click()

        sleep(1)

    def fill_password(self):
        btns = self.driver.find_elements_by_class_name("font-lnum")

        for password_number in self.password:
            password_number = int(password_number)

            for btn in btns:
                btn_numbers = btn.text
                btn_numbers_split = btn_numbers.split(" ou ")

                # ter certeza de que tem duas opções: 1 ou 2
                if len(btn_numbers_split) == 2:
                    number_option_1 = int(btn_numbers_split[0])
                    number_option_2 = int(btn_numbers_split[1])

                    if number_option_1 == password_number or number_option_2 == password_number:
                        btn.click()

        sleep(1)
        submit_btn = self.driver.find_element_by_xpath(
            '//*[@id="login-component"]/div/div[2]/div/div[1]/div/form/button')
        submit_btn.click()
