import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import datetime
import pygsheets
import pytz
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
import argparse
import time


class ScraperAdmin:
    def __init__(self):
        __chrome_options = Options()
        __chrome_options.add_argument("--headless")
        __chrome_options.add_argument("--no-sandbox")
        __chrome_options.add_argument("--disable-dev-shm-usage")
        __chrome_prefs = {}
        __chrome_options.experimental_options["prefs"] = __chrome_prefs
        __chrome_prefs["profile.default_content_settings"] = {"images": 2}
        self.driver = webdriver.Chrome(options=__chrome_options)

        # self.driver = webdriver.Chrome('/Users/mytarget/Projects/State/chromedriver')  # use for local lunch

        self._all_cities = ['BOR', 'BRO', 'CHE', 'CHK', 'CHN', 'DNP', 'IRP', 'IVF', 'KHA', 'KHE', 'KHM', 'KIE', 'KRO',
                            'KRR', 'KYI', 'LUT', 'LVI', 'MKL', 'ODE', 'ODS', 'POL', 'RVN', 'SUM', 'TNP', 'VNT', 'ZHY',
                            'MPL', 'KRK', 'BTA', 'ZPR', 'UZH', 'UMA', 'TRK', 'CHS', 'DRH', 'BDK', 'KAM', 'KPD']

        self.timezone = pytz.timezone('Europe/Kiev')

        tracker_conn = pygsheets.authorize(service_file='tracker.json')
        tracker_wks = tracker_conn.open('Tracker')
        self._tracker_sheet = tracker_wks.worksheet('title', 'UA')

        state_conn = pygsheets.authorize(service_file='key_state.json')
        self._state_wks = state_conn.open('StateBigCity')

    def wait_element(self, xpath: str) -> None:
        wait = WebDriverWait(self.driver, 30, poll_frequency=1,
                             ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

    def wait_text(self, text: str, xpath: str):
        wait = WebDriverWait(self.driver, 30, poll_frequency=1,
                             ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
        wait.until(EC.text_to_be_present_in_element((By.XPATH, xpath), text))

    def login_google(self, email: str, password: str, entry_code: str) -> None:
        """
        login with google auth
        :param email:
        :param password:
        :param entry_code:
        :return:
        """
        url_one_login = 'https://glovoapp.onelogin.com/login2'
        self.driver.get(url_one_login)

        email_input_xpath = '/html/body/div/div/div[2]/div[1]/div[2]/form/div/div[1]/input'
        self.wait_element(email_input_xpath)
        user_email = self.driver.find_element_by_tag_name('input')
        user_email.click()
        user_email.send_keys(email, Keys.TAB, Keys.TAB, Keys.ENTER)
        pass_input_xpath = '/html/body/div/div/div[2]/div[1]/div[2]/form/div/div[2]/input'
        self.wait_element(pass_input_xpath)
        user_pass = self.driver.find_element_by_id('password')
        user_pass.click()
        user_pass.send_keys(password, Keys.TAB, Keys.ENTER)

        code_input_xpath = '/html/body/div/div/div[2]/div[1]/div[2]/div/form/div/div[1]/div[2]/input'
        self.wait_element(code_input_xpath)
        auth_code = self.driver.find_element_by_xpath(code_input_xpath)
        auth_code.click()
        auth_code.send_keys(entry_code)

        xpath_continue_btn = '/html/body/div/div/div[2]/div[1]/div[2]/div/form/div/div[2]/div/button'
        self.wait_element(xpath_continue_btn)
        continue_btn = self.driver.find_element_by_xpath(xpath_continue_btn).click()

        try:
            auth_code.send_keys(entry_code)
        except:
            xpath_skip_btn = '/html/body/div/main/div/div/p[2]/button'
            self.wait_element(xpath_skip_btn)
            self.driver.find_element_by_xpath(xpath_skip_btn).click()
            xpath_admin = '/html/body/div/main/div/div[2]/div/div/div/div[1]/a'
            self.wait_element(xpath_admin)
            self.driver.find_element_by_xpath(xpath_admin).click()
            window_name = self.driver.window_handles[0]
            self.driver.switch_to_window(window_name)
            self.driver.close()
            window_name = self.driver.window_handles[0]
            self.driver.switch_to_window(window_name)
            xpath_menu_bar = '/html/body/div/div/div[3]/div[1]/div[1]'
            self.wait_element(xpath_menu_bar)
            try:
                self.driver.find_element_by_xpath(xpath_menu_bar).click()
            except ElementClickInterceptedException:
                self.driver.find_element_by_xpath(xpath_menu_bar).click()

        live_map = 'https://beta-admin.glovoapp.com/livemap'
        self.driver.get(live_map)
        time.sleep(2)

        select_cities = self.driver.find_element_by_class_name('top-bar__cities')
        select_cities.click()

        click_on_ua = self.driver.find_element_by_xpath(
            '/html/body/div/div/div[3]/div[1]/div[3]/div[2]/section/section/div[2]/div[2]/div[1]/div[2]/div[45]/div[1]/span[2]/span').click()

        for div_num in range(1, 83):
            name_city = self.driver.find_element_by_xpath(
                f'/html/body/div/div/div[3]/div[1]/div[3]/div[2]/section/section/div[2]/div[2]/div[1]/div[2]/div[45]/div[2]/div[{div_num}]/div/span[2]/span/span[1]').text
            checkbox = self.driver.find_element_by_xpath(
                f'/html/body/div/div/div[3]/div[1]/div[3]/div[2]/section/section/div[2]/div[2]/div[1]/div[2]/div[45]/div[2]/div[{div_num}]/div/label/span/span'
            )
            if name_city in self._all_cities:
                checkbox.click()

        self.driver.find_element(By.XPATH, "//span[text()=' Save ']").click()

    def login_onelogin(self, email: str, password: str) -> None:
        """
        login with google auth
        :param email:
        :param password:
        :param entry_code:
        :return:
        """
        url_one_login = 'https://glovoapp.onelogin.com/login2'
        self.driver.get(url_one_login)

        email_input_xpath = '/html/body/div/div/div[2]/div[1]/div[2]/form/div/div[1]/input'
        self.wait_element(email_input_xpath)
        user_email = self.driver.find_element_by_tag_name('input')
        user_email.click()
        user_email.send_keys(email, Keys.TAB, Keys.TAB, Keys.ENTER)
        pass_input_xpath = '/html/body/div/div/div[2]/div[1]/div[2]/form/div/div[2]/input'
        self.wait_element(pass_input_xpath)
        user_pass = self.driver.find_element_by_id('password')
        user_pass.click()
        user_pass.send_keys(password, Keys.TAB, Keys.ENTER)

        xpath_change_method_auth = '/html/body/div/div/div[2]/div[1]/div[2]/div/div[2]/div/button/span'
        self.wait_element(xpath_change_method_auth)
        self.driver.find_element_by_xpath(xpath_change_method_auth).click()

        xpath_onelogin = '/html/body/div/div/div[2]/div[1]/div[2]/div/div[2]/div[2]'
        self.wait_element(xpath_onelogin)
        self.driver.find_element_by_xpath(xpath_onelogin).click()

        xpath_resend_ntf = '/html/body/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div[2]/button[1]/span'
        for _ in range(2):
            try:
                self.wait_element(xpath_resend_ntf)
                self.driver.find_element_by_xpath(xpath_resend_ntf).click()
                time.sleep(5)
            except selenium.common.exceptions.TimeoutException:
                break

        xpath_skip_btn = '/html/body/div/main/div/div/p[2]/button'
        self.wait_element(xpath_skip_btn)
        self.driver.find_element_by_xpath(xpath_skip_btn).click()
        xpath_admin = '/html/body/div/main/div/div[2]/div/div/div/div[1]/a'
        self.wait_element(xpath_admin)
        self.driver.find_element_by_xpath(xpath_admin).click()
        window_name = self.driver.window_handles[0]
        self.driver.switch_to_window(window_name)
        self.driver.close()
        window_name = self.driver.window_handles[0]
        self.driver.switch_to_window(window_name)
        xpath_menu_bar = '/html/body/div/div/div[3]/div[1]/div[1]'
        self.wait_element(xpath_menu_bar)
        try:
            self.driver.find_element_by_xpath(xpath_menu_bar).click()
        except ElementClickInterceptedException:
            self.driver.find_element_by_xpath(xpath_menu_bar).click()

        live_map = 'https://beta-admin.glovoapp.com/livemap'
        self.driver.get(live_map)
        time.sleep(2)

        select_cities = self.driver.find_element_by_class_name('top-bar__cities')
        select_cities.click()

        click_on_ua = self.driver.find_element_by_xpath(
            '/html/body/div/div/div[3]/div[1]/div[3]/div[2]/section/section/div[2]/div[2]/div[1]/div[2]/div[45]/div[1]/span[2]/span').click()

        for div_num in range(1, 83):
            name_city = self.driver.find_element_by_xpath(
                f'/html/body/div/div/div[3]/div[1]/div[3]/div[2]/section/section/div[2]/div[2]/div[1]/div[2]/div[45]/div[2]/div[{div_num}]/div/span[2]/span/span[1]').text
            checkbox = self.driver.find_element_by_xpath(
                f'/html/body/div/div/div[3]/div[1]/div[3]/div[2]/section/section/div[2]/div[2]/div[1]/div[2]/div[45]/div[2]/div[{div_num}]/div/label/span/span'
            )
            if name_city in self._all_cities:
                checkbox.click()

        self.driver.find_element(By.XPATH, "//span[text()=' Save ']").click()

    def tracker(self, city: str) -> list:
        values = self._tracker_sheet.get_values(start='A2', end='D40')
        [value.pop(2) for value in values]
        for stat in values:
            if stat[0] == city:
                stat.pop(0)
                print(self.tracker.__name__, 'DONE')
                return stat

    def html(self, name_city: str) -> None:
        sheet = self._state_wks.worksheet('title', datetime.datetime.now(self.timezone).strftime("%d.%m"))
        num_row = len(sheet.get_all_records()) + 2

        courier = self.driver.find_element_by_xpath(
            '/html/body/div/div/div[3]/div[2]/section/div[2]/div[2]/div[3]/div/div/div[2]/div/div[1]/span').text
        orders = self.driver.find_element_by_xpath(
            '/html/body/div/div/div[3]/div[2]/section/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]/span').text
        status_live_map = self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[3]/div[2]/section/div[2]/div[2]/div[6]/div[1]/div[1]/span/strong').text
        start_time = self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[3]/div[2]/section/div[2]/div[2]/div[5]/div/div/div[2]/div/div[1]/span').text
        end_time = self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[3]/div[2]/section/div[2]/div[2]/div[5]/div/div/div[2]/div/div[2]/span').text

        lst_stat = [datetime.datetime.now(self.timezone).strftime("%d.%m - %H:%M:%S "), name_city, orders, courier,
                    f'{start_time} - {end_time}',
                    f'=IF(ISERROR(C{num_row}/D{num_row}), "0%", TEXT(C{num_row}/D{num_row}, "0%"))'
                    ]

        for value in self.tracker(name_city):
            lst_stat.append(value)
        lst_stat.insert(7, status_live_map)
        # print(lst_stat)
        sheet.update_row(num_row, lst_stat)
        print(self.html.__name__, 'DONE')

    def select_cities(self, name_city: str):

        cities = self.driver.find_elements_by_class_name('el-radio-button')
        start_time_xpath = '/html/body/div/div/div[3]/div[2]/section/div[2]/div[2]/div[5]/div/div/div[2]/div/div[1]/div/label'
        for city in cities:
            if city.text[:3] == name_city:
                self.wait_text('START TIME', start_time_xpath)
                city.click()

                time.sleep(1)
                self.driver.refresh()
                self.wait_text('START TIME', start_time_xpath)
                self.html(name_city)
                break

    def cities_until_10am(self):

        cities = ['KHA', 'KIE', 'KYI', 'ODS', 'LVI', 'RVN', 'CHE', 'DNP', 'POL', 'ODE', 'MKL']
        for city in cities:
            self.select_cities(city)
        print(self.cities_until_10am.__name__, 'DONE')

    def cities_after_10am(self):

        for city in self._all_cities:
            self.select_cities(city)

        print(self.cities_after_10am.__name__, 'DONE')

    def after_midnight(self):

        cities = ['ODS', 'KIE', 'KYI', 'LVI', 'DNP', 'KHA']

        for city in cities:
            self.select_cities(city)

        print(self.after_midnight.__name__, 'DONE')

    def run_all(self):
        time_now = datetime.datetime.now(self.timezone).hour
        if time_now >= 23 or (time_now >= 0 and time_now <= 7):
            self.after_midnight()
            time.sleep(360)
        elif time_now >= 10 and time_now <= 23:
            self.cities_after_10am()
        elif time_now >= 8 and time_now < 10:
            self.cities_until_10am()
            time.sleep(360)

    def del_sheet(self):
        day_14 = datetime.datetime.now(self.timezone) - datetime.timedelta(days=14)

        try:
            sheet = self._state_wks.worksheet('title', day_14.strftime("%d.%m"))
            self._state_wks.del_worksheet(sheet)
        except pygsheets.exceptions.WorksheetNotFound:
            pass

    def conditional_format(self):
        day_today = datetime.datetime.now(self.timezone)

        sheet = self._state_wks.worksheet('title', day_today.strftime("%d.%m"))
        sheet.add_conditional_formatting('G2', 'G9000', 'NUMBER_GREATER_THAN_EQ',
                                         {'backgroundColor': {'red': 0.96, 'green': 0.8, 'blue': 0.8}}, ['150%'])
        sheet.add_conditional_formatting('G2', 'G9000', 'NUMBER_GREATER_THAN_EQ',
                                         {'backgroundColor': {'red': 0.92, 'green': 0.6, 'blue': 0.6}}, ['175%'])
        sheet.add_conditional_formatting('G2', 'G9000', 'NUMBER_GREATER_THAN_EQ',
                                         {'backgroundColor': {'red': 0.88, 'green': 0.4, 'blue': 0.4}}, ['200%'])

    def add_sheet(self):

        sheets = self._state_wks.worksheets()

        date_today = datetime.datetime.now(self.timezone).strftime("%d.%m")

        if sheets[-1].title != date_today:
            self._state_wks.add_worksheet(date_today, rows=9000, cols=9)
            title = ['Time', 'City', 'Total orders', 'Total couriers', 'Slot start & end', 'Saturation',
                     'Tracker', 'Live map status',
                     'City Status']
            new_sheet = self._state_wks.worksheet('title', date_today)
            new_sheet.update_row(1, title)
            self.del_sheet()
            self.conditional_format()
        elif sheets[-1].title == date_today:
            return False
        print(self.add_sheet.__name__, 'DONE')


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c')
    parser.add_argument('-e')
    parser.add_argument('-p')
    parser.add_argument('--auth')
    args = parser.parse_args()
    code_arg = args.c
    email_arg = args.e
    password_arg = args.p
    auth = args.auth

    scraper = ScraperAdmin()
    if auth == '0':
        scraper.login_google(email_arg, password_arg, code_arg)
    if auth == '1':
        scraper.login_onelogin(email_arg, password_arg)

    while True:
        scraper.add_sheet()
        scraper.run_all()


run()
