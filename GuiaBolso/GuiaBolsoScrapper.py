# coding=utf-8
from pprint import pprint
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from helpers import getMonthNumber


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

        wait = WebDriverWait(self.driver, 160)
        email_ipt = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div/main/form/div[1]/input')))
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

    def getMovements(self):
        movements = []

        self.driver.get('https://www.guiabolso.com.br/extrato')
        sleep(2)

        banks_divs = self.driver.find_elements_by_class_name('unstyled')

        content = self.driver.find_element_by_id('main')
        pagination = content.find_element_by_id('pagination')

        for i in range(3):
            ahref = pagination.find_elements_by_css_selector('a')[0]
            ahref.click()

            sleep(2)

        for banks_div in banks_divs:
            print("Div encontrada")
            i = 0
            banks = banks_div.find_elements_by_css_selector('li')

            for bank in banks:
                print("Percorrendo banco")
                if i > 0:
                    sleep(2)

                    bank_number = bank.find_element_by_class_name('title').text
                    bank.find_element_by_css_selector('a').click()

                    sleep(5)
                    forms = content.find_elements_by_class_name('transactions-form')

                    bank_transaction = {
                        "bank_number": bank_number,
                        "transactions": []
                    }

                    for form in forms:
                        month = form.find_element_by_class_name('month').text
                        month_split = month.split(" ")
                        month = getMonthNumber(month_split[0])
                        year = month_split[2]

                        transactions = form.find_elements_by_class_name('transaction')

                        for transaction in transactions:
                            try:

                                date = transaction.find_element_by_class_name('date').text.split(" ")[0]

                                mov = {
                                    "date": year + "-" + month + "-" + date,
                                    "description": transaction.find_element_by_class_name(
                                        'name').find_element_by_class_name(
                                        'edit').text,
                                    "amount": transaction.find_element_by_class_name('value-label').text,
                                    "category": transaction.find_element_by_class_name('category').text
                                }

                                pprint(mov)
                                bank_transaction['transactions'].append(mov)
                            except Exception as e:
                                print(e)
                                pass
                    movements.append(bank_transaction)
                i += 1

        return movements

    def scrap(self):

        movements = self.getMovements()

        self.driver.get('https://www.guiabolso.com.br/web/#/financas/resumo')

        sleep(1)
        wait = WebDriverWait(self.driver, 160)
        total = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "hEMTnY")))

        total_balance_btn = self.driver.find_element_by_class_name('eIwspU')

        total_balance_btn.click()

        sleep(2)

        main_content = self.driver.find_element_by_class_name('bYNpJH')
        i = 0

        accounts = main_content.find_elements_by_class_name('hNKaST')

        applications = {
            'accounts': [],
            'overview': [],
            'movements': movements
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
