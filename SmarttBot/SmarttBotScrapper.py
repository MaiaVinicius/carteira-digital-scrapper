# coding=utf-8
from pprint import pprint
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SmarttBotScrapper:
    initial_url = "https://antigoapp.smarttbot.com/login"
    driver = None

    username = None
    password = None

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def init(self):
        path = "/Users/maiavinicius/PycharmProjects/minha_carteira/driver/chromedriver-mac"
        self.driver = webdriver.Chrome(path)

        self.driver.get(self.initial_url)
        self.login()
        self.wait_login()
        res = self.scrap()

        return res

    def login(self):
        username_ipt = self.driver.find_element_by_id('login')
        username_ipt.send_keys(self.username)

        password_ipt = self.driver.find_element_by_id('password')
        password_ipt.send_keys(self.password)

        submit_btn = self.driver.find_element_by_class_name('submit-btn').find_element_by_css_selector('button')
        submit_btn.click()

    def wait_login(self):
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.ID, "create-instance-btn")))
        print("Login finished")

    def scrap(self):
        robots_ids = []
        # abre o dropdown contendo os filtros dos robos
        dropdown_mode_btn = self.driver.find_element_by_xpath('//*[@id="instances-all-view"]/div[1]/div/div[3]/div/a')
        dropdown_mode_btn.click()
        sleep(0.2)

        # clica na opcao "Reais"
        checkbox_simulationmode = self.driver.find_element_by_xpath(
            '//*[@id="instances-all-view"]/div[1]/div/div[3]/div/ul/li[2]/input')
        checkbox_simulationmode.click()

        sleep(2)

        table_el = self.driver.find_element_by_xpath('//*[@id="instances-all-view"]/table')
        table_body_el = table_el.find_elements_by_class_name('closed')

        data = {
            'bots': []
        }

        for tbody in table_body_el:
            try:
                expand_btn = tbody.find_element_by_class_name('link-no-decoration')
                expand_btn.click()

                sleep(3)

                try:
                    tds = tbody.find_elements_by_css_selector('td')
                    bot_name = tds[3].text
                    status = tds[7].text

                    if status != 'Carteira Zerada' and status != '-':
                        report_table_el = tbody.find_element_by_class_name('report-table-wrap')
                        report_tbody_el = report_table_el.find_element_by_css_selector('tbody')
                        report_tds = report_tbody_el.find_elements_by_css_selector('td')

                        total = report_tds[0].text
                        percent = report_tds[1].text
                        drawdown = report_tds[2].text
                        profit_rate = report_tds[3].text
                        today_amount = report_tds[5].text

                        current_line = {
                            'bot_name': bot_name,
                            'status': status,
                            'total': total,
                            'percent': percent,
                            'drawdown': drawdown,
                            'profit_rate': profit_rate,
                            'today_amount': today_amount
                        }

                        data['bots'].append(current_line)

                        expand_btn.click()
                except Exception as e2:
                    print(e2)

            except Exception as e:
                # print e
                pass

        pprint(data)

        return data
