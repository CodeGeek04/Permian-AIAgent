import time
import os
import re
import sys

import yaml
import html2text

from bs4 import BeautifulSoup
from bs4.element import NavigableString
from bs4.element import Tag

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.relative_locator import locate_with

def init_driver():
    # skipping login
    user_data_dir = "./user_data" 

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    # chrome_options.add_argument("--headless")

    chromedriver_path = "./chromedriver"
    service = Service(chromedriver_path)

    driver = webdriver.Chrome(options=chrome_options)

    url = "https://www.kapwing.com/63fff8c43495720011cba47a/studio/editor"
    driver.get(url)

    time.sleep(10)

    return driver


""" Defining 4 casual APIs here, named by usage. """


def add_caption(driver, text):
    driver.find_element(By.XPATH, "//main[@id='root']/div/div/div[3]/div/div/div/div/div/div[4]/div").click()
    driver.find_element(By.XPATH, "//div[@id='mediaSidebarControls']/div/div/div[2]/div[3]/div/button").click()
    driver.find_element(By.XPATH, "//main[@id='root']/div/div/div[3]/div/div[4]/div/div/div/div/div/div[2]/div[4]/textarea").click()
    driver.find_element(By.XPATH, "//main[@id='root']/div/div/div[3]/div/div[4]/div/div/div/div/div/div[2]/div[4]/textarea").clear()

    driver.find_element(By.XPATH, "//main[@id='root']/div/div/div[3]/div/div[4]/div/div/div/div/div/div[2]/div[4]/textarea").send_keys(text)    
    driver.find_element(By.XPATH, "//div[@id='canvas']/div[4]/div[2]").click()
    time.sleep(5)


def change_caption_color(driver, color):
    driver.find_element(By.XPATH, "//main[@id='root']/div/div/div[3]/div/div/div/div/div/div[4]/div").click()
    driver.find_element(By.XPATH, "//div[@id='mediaSidebarControls']/div/div/div[2]/div[3]/div[2]/div/div/div/div[2]/div/div/textarea").click()
    driver.find_element(By.XPATH, "//main[@id='root']/div/div/div[3]/div/div[4]/div/div/div/div/div/div/div[3]/div/div[2]/div[4]/div").click()
    driver.find_element(By.XPATH, "//input[@value='#ffffff']").click()
    # driver.find_element(By.XPATH, "//input[@value='#']").clear()
    driver.find_element(By.XPATH, f"//input[@value='{color}']").send_keys(color)
    driver.find_element(By.XPATH, "//main[@id='root']/div/div[4]/div[2]/div/div[2]/div[2]/div[4]/div").click()
    time.sleep(5)


def add_happy_emoji():
    driver.find_element(By.XPATH, "//main[@id='root']/div/div/div[3]/div/div/div/div/div/div[7]/div").click()
    driver.get("https://www.kapwing.com/63fff8c43495720011cba47a/studio/editor/elements")
    # driver.find_element(By.XPATH, "//div[@id='mediaSidebarControls']/div/div/div[2]/div[2]/div[2]/div[2]/div/span[2]").click()
    driver.find_element(By.XPATH, "//input[@value='']").click().send_keys("happy")
    driver.find_element(By.XPATH, "//img[@alt='library/new/beaming-face-with-smiling-eyes.png thumbnail']").click()
    time.sleep(5)


def lock_layer():
    driver.find_element(By.XPATH, "//main[@id='root']/div/div/div[3]/div/div/div/div/div/div[2]/div").click()
    driver.get("https://www.kapwing.com/63fff8c43495720011cba47a/studio/editor/layers")
    driver.find_element(By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='preview_architecture video'])[1]/following::*[name()='svg'][1]").click()
    time.sleep(5)




if __name__ == "__main__":
    driver = init_driver()
    query = input("API:")
    exec(query)
    # add_caption(driver, "The Art of Loving.")
    # change_caption_color(driver, '#FFCC80')