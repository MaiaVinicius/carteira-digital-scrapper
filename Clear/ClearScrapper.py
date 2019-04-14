# coding=utf-8
from pprint import pprint
from time import sleep

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from helpers import getMonthNumber


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

    def _get(self, url):
        self.driver.get(url)
        sleep(1)

    def init(self):
        path = "/Users/maiavinicius/PycharmProjects/minha_carteira/driver/chromedriver-mac"
        caps = DesiredCapabilities().CHROME
        # caps["pageLoadStrategy"] = "normal"  #  complete
        # caps["pageLoadStrategy"] = "eager"  # interactive
        # caps["pageLoadStrategy"] = "none"

        self.driver = webdriver.Chrome(path, desired_capabilities=caps)

        self._get(self.initial_url)
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

        self._get("https://www.clear.com.br/pit/Selector/ToNew")

        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "logo_header")))
        print("Login finished")

    def getMovements(self):
        movements = []
        self._get("https://novopit.clear.com.br/MinhaConta/ExtratoFinanceiro")

        self.driver.switch_to.frame(self.driver.find_element_by_class_name("ifm"))

        wait = WebDriverWait(self.driver, 20)
        element = wait.until(EC.visibility_of_element_located((By.ID, "grouper-list")))

        select_period = Select(self.driver.find_element_by_id('combo-filter-range'))
        select_period.select_by_value('60')
        #
        sleep(5)
        months = self.driver.find_element_by_class_name('container_body_stmt').find_elements_by_class_name('cont_month')

        for month_div in months:
            month_div_el = month_div.find_element_by_class_name('cont_left')

            table = month_div.find_element_by_class_name('cblc')

            tbody = table.find_element_by_class_name('entries-cblc-holder')
            trs = tbody.find_elements_by_css_selector('tr')

            i = 0
            year = None
            month = None

            for tr in trs:
                actions = ActionChains(self.driver)
                actions.move_to_element(tr).perform()

                sleep(0.2)

                if i == 0:
                    year = month_div_el.find_element_by_class_name('grouper-year').text
                    month = getMonthNumber(month_div_el.find_element_by_class_name('grouper-month').text)

                tds = tr.find_elements_by_css_selector('td')
                movements.append({
                    "date_liquidation": year + "-" + month + "-" + tds[0].find_element_by_class_name(
                        'entry-date-day').text,
                    "date_sent": year + "-" + month + "-" + tds[1].find_element_by_class_name('entry-mov-day').text,
                    "description": tds[2].find_element_by_class_name('entry-description').text,
                    "amount": tds[3].find_element_by_class_name('entry-value').text,
                    "balance_after": tds[4].find_element_by_class_name('entry-balance').text,
                })

                i += 1

        pprint(movements)
        return movements

    def scrap(self):
        movements = self.getMovements()

        self._get("https://novopit.clear.com.br/MinhaConta/MeusAtivos")

        self.driver.switch_to.frame(self.driver.find_element_by_class_name("ifm"))

        wait = WebDriverWait(self.driver, 20)
        element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "value-total")))

        sleep(2)
        try:
            total_amount = self.driver.find_element_by_class_name("value-total").text
            in_account_amount = self.driver.find_element_by_xpath(
                '//*[@id="view-list"]/li[2]/a/div[2]/span[1]/i[2]').text

            applications = {
                "in_account": in_account_amount,
                "total": total_amount,
                "stock": [],
                "movements": movements,
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

            actions = ActionChains(self.driver)
            actions.move_to_element(stock).perform()

            stock.click()

            sleep(5)

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
