# coding=utf-8
from datetime import datetime
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
        balance = {
            "applications_summary": [],
            "applications": [],
            "in_account": self.driver.find_element_by_xpath('//*[@id="tableAllocatedValue"]/tfoot/tr[2]/td[4]').text,
            'movements': [],
            "total": self.driver.find_element_by_xpath('//*[@id="tableAllocatedValue"]/tfoot/tr[3]/td[4]').text
        }
        balance["movements"] = self.getMovements()

        # pega os valores de tesouro direto
        self.driver.get("https://www.rico.com.vc/dashboard/tesouro-direto/")
        description = ""

        treasure = self.driver.find_element_by_id('tableAllocatedValue')

        tbody = treasure.find_elements_by_css_selector('tbody')[1]
        trs = tbody.find_elements_by_css_selector('tr')

        # roda por cada tr clicando no btn de mais para expandir
        for tr in trs:
            tds = tr.find_elements_by_css_selector('td')

            try:
                plus_btn = tr.find_element_by_class_name('plus-indicator')
                plus_btn.click()
                description = tds[0].text

                print(description)
            except Exception as e:
                print(tr.text)

                try:
                    th = tr.find_element_by_css_selector('th')
                except Exception as e:
                    print("tesouro encotrado!")

                    print(tr.text)

                    if tds[4].text != '':
                        tesouro = {
                            'type': 'tesouro',
                            'type_id': 12,
                            'description': description,
                            'initial_balance': tds[4].text,
                            'quantity': tds[3].text,
                            'balance': tds[5].text,
                            'buy_date': tds[1].text,
                            'profitability': tds[0].text,
                            'expires': tds[2].text
                        }
                        pprint(tesouro)

                        balance['applications'].append(tesouro)

        self.driver.get("https://www.rico.com.vc/dashboard/")
        sleep(2)

        self.skip_intro()

        print("Scrapping ... ")

        table = self.driver.find_element_by_id("tableAllocatedValue")
        rows = table.find_element_by_css_selector("tbody").find_elements_by_class_name("user-select-none")

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

        # pega os valores de renda fixa
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

        # pega os dados de fundo
        self.driver.get("https://www.rico.com.vc/arealogada/fundos-de-investimento/ordens")
        tbody = self.driver.find_element_by_xpath('//*[@id="app"]/div/main/div/section[2]/div/div[2]/table/tbody')
        trs = tbody.find_elements_by_css_selector('tr')
        for tr in trs:
            tds = tr.find_elements_by_css_selector('td')

            balance_total = tds[4].text
            initial_balance = tds[2].text

            if balance_total == "0,00":
                liquidacao = tds[5].text

                balance_total = liquidacao
                initial_balance = liquidacao

                print(liquidacao)

            balance['applications'].append({
                'type': 'fundo',
                'type_id': 11,
                'description': tds[0].find_element_by_css_selector('span').text,
                'initial_balance': initial_balance,
                'balance': balance_total,
                'buy_date': False
            })

        return balance

    def monthdelta(self, date, delta):
        m, y = (date.month + delta) % 12, date.year + ((date.month) + delta - 1) // 12
        if not m: m = 12
        d = min(date.day, [31,
                           29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][
            m - 1])
        return date.replace(day=d, month=m, year=y)

    def getMovements(self):
        movements = []

        self.driver.get("https://www.rico.com.vc/dashboard/conta/extrato/")
        datestart = self.monthdelta(datetime.now(), -3).strftime("%d/%m/%Y")
        dateend = datetime.today()

        date_start_ipt = self.driver.find_element_by_xpath(
            '/html/body/section/div/div[2]/div/div/section/div/form/div/div[1]/div/input')
        date_start_ipt.clear()
        date_start_ipt.send_keys(datestart)

        sleep(3)

        table = self.driver.find_element_by_xpath('/html/body/section/div/div[2]/div/div/section/div/table')
        tbody = table.find_element_by_css_selector('tbody')
        trs = tbody.find_elements_by_css_selector('tr')

        for tr in trs:
            tds = tr.find_elements_by_css_selector('td')
            date_liquidation = tds[0]
            date_sent = tds[1]
            description = tds[2]
            amount = tds[3]
            balance_after = tds[4]

            movements.append({
                "date_liquidation": date_liquidation.text,
                "date_sent": date_sent.text,
                "description": description.text,
                "amount": amount.text,
                "balance_after": balance_after.text,
            })

        # pprint(movements)

        return movements

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
        wait = WebDriverWait(self.driver, 10)
        user_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="loginForm"]/div[1]/input')))
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
