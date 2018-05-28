# -*- coding: utf-8 -*-
# @Date    : 2015-04-17 15:33:53
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert

driver = webdriver.Firefox()
driver.get("https://10.204.253.192")

driver.find_element_by_id("userid").send_keys("admin")
driver.find_element_by_id("password").send_keys("ddei")
driver.find_element_by_css_selector("li#login_btn span").click()

time.sleep(1)

driver.switch_to_default_content()
menu_admin = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "Admin"))
        )
menu_admin.click()

time.sleep(1)

sub_menu_va_settings = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "Navigation__GlobalSetting"))
        )
sub_menu_va_settings.click()

time.sleep(1)

driver.switch_to_default_content()
left_frame = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "left_page"))
        )
driver.switch_to_frame(left_frame)

time.sleep(1)

element = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "Navigation__Backup"))
        )
element.click()

time.sleep(1)

driver.switch_to_default_content()

middle_frame = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "middle_page"))
        )
driver.switch_to_frame(middle_frame)

time.sleep(1)

input_file = driver.find_element_by_xpath("//input[@type='file']")
input_file.send_keys("C:\Users\Administrator\Desktop\Config_Files_20150417_072351.dat")
time.sleep(1)
driver.find_element_by_xpath("//input[@name='backup_import']").click()
Alert(driver).accept()
time.sleep(60)
driver.close()