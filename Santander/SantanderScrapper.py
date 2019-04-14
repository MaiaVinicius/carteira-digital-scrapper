# coding=utf-8
from pprint import pprint
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SantanderScrapper:
    initial_url = "https://www.santander.com.br/?segmento=especial"
    driver = None

    username = None
    last_digits = None
    password = None

    def __init__(self, cpf, password, last_digits):
        self.cpf = cpf
        self.password = password
        self.last_digits = last_digits

    def init(self):
        path = "/Users/maiavinicius/PycharmProjects/minha_carteira/driver/chromedriver-mac"
        self.driver = webdriver.Chrome(path)

        self.driver.get(self.initial_url)
        self.login()
        self.wait_login()
        res = self.scrap()

        return res

    def login(self):
        sleep(2)

        username_ipt = self.driver.find_element_by_xpath(
            '//*[@id="appHeader"]/header-desktop/header/div[2]/div/div[3]/login-field/div/form/div/div/div[1]/div/input')
        username_ipt.send_keys(self.cpf)

        submit_btn = self.driver.find_element_by_class_name('submit-button')
        submit_btn.click()

        sleep(2)

        self.driver.switch_to_frame("Principal")
        self.driver.switch_to_frame("MainFrame")
        sleep(1)

        ipt_cartao = self.driver.find_element_by_id('txtCartao')
        ipt_cartao.send_keys(self.last_digits)

        ipt_senha = self.driver.find_element_by_id('txtSenha')
        ipt_senha.send_keys(self.password)

        btn_submit = self.driver.find_element_by_class_name('btn_confirmar')
        btn_submit.click()

    def wait_login(self):
        sleep(2)
        print("Login finished")

    def scrap(self):
        # ...
        sleep(5)
        self.driver.execute_script("top.Principal.Corpo.document.getElementById('layer_aviso').style.display='none';")

        self.driver.switch_to.frame("Principal")
        self.driver.switch_to.frame("Corpo")

        # ....
        # .
        sleep(1)
        btn_fatura = self.driver.find_element_by_xpath(
            '//*[@id="divCartoes"]/table/tbody/tr[1]/td[1]/table/tbody/tr[4]/td[2]/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/table')

        btn_fatura.click()
        # ...
        sleep(2)

        # self.driver.switch_to.frame("Principal")
        # self.driver.switch_to.frame("Corpo")
        self.driver.switch_to.frame("iframePrinc")

        select_box = self.driver.find_element_by_id("cboFatura")

        select = Select(select_box)
        # if your select_box has a name.. why use xpath?.....
        # this step could use either xpath or name, but name is sooo much easier.

        options = [x for x in select_box.find_elements_by_tag_name("option")]
        # this part is cool, because it searches the elements contained inside of select_box
        # and then adds them to the list options if they have the tag name "options"

        self.driver.switch_to.frame("iDetalhes")

        for element in options:

            month_label = ""
            try:
                option_value = element.get_attribute("value")
                month_label = element.text

                select.select_by_value(option_value)

            except Exception as e:
                print(e)
                self.driver.switch_to.parent_frame()

                continue

            self.driver.execute_script("onExibir();")

            sleep(2)

            self.driver.switch_to.frame("iDetalhes")

            html = self.driver.page_source

            self.driver.switch_to.parent_frame()

            month_label = month_label.replace(" - ", "|")
            month_label = month_label.replace("/", "-")

            f = open('output/credit-card/' + month_label + '.html', 'w+')
            f.write(html)
            f.close()

        # cboFatura

        return True
