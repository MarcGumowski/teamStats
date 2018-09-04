# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------

team_stats - scrape_stats
ver: 0.01

---------------------------------------------------------------------------------

Scrape stats from every game of CP Meyrin

---------------------------------------------------------------------------------
"""

import os
import numpy as np
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep

os.chdir('C:/Users/Gumistar/Documents/GitHub/teamStats')

team = 'CP de Meyrin'
url = 'https://www.sihf.ch/fr/game-center/regio-league/#/results/date/asc/page/0/2018/18/4/2401/05.10.2017-11.02.2018/105041'
# url = 'https://www.sihf.ch/fr/game-center/regio-league/#/results/date/asc/page/0/2019/18/4/2717/04.10.2018-10.02.2019'

browser = webdriver.Chrome(executable_path=r'E:/Applications/chromedriver/chromedriver.exe')
browser.get(url)
sleep(3)

# Game info
def get_game_link(browser):
    return [game.get_attribute('href') for game in browser.find_elements_by_xpath('//*[@id="results"]//table//td[10]//a')]
game_link = get_game_link(browser)

def get_game_date(browser):
    date = [game.text for game in browser.find_elements_by_xpath('//*[@id="results"]//table//td[contains(@class, "active")]//span')]
    return date[:int(len(date)/2)]
game_date = {'date': get_game_date(browser)}

def get_game_location(browser, team):
    home_team = [game.text for game in browser.find_elements_by_xpath('//*[@id="results"]//table//td[4]//span[contains(@class, "-team-name")]')]
    location = []
    for loc in home_team:
        if loc == team:
            location.append(1)
        else:
            location.append(0)
    return location
game_home = {'home': get_game_location(browser, team)}

def get_opponent(browser, team):
    team_a = [game.text for game in browser.find_elements_by_xpath('//table//td[4]//span[contains(@class, "-team-name")]')]
    team_b = [game.text for game in browser.find_elements_by_xpath('//table//td[5]//span[contains(@class, "-team-name")]')]
    teams = team_a + team_b
    return [opponent for opponent in teams if opponent not in team]
game_opponent = {'opponent': get_opponent(browser, team)}
game_team = {'team': team}
base_info = {**game_date, **game_team, **game_opponent, **game_home}
game_info = pd.DataFrame(base_info)


# Game details
def get_time(browser):
    return [time.text for time in browser.find_elements_by_xpath('//table//td[3]')]
def get_action_type(browser, td, class_td = ''):
    return [action.get_attribute('class') for action in browser.find_elements_by_xpath('//table//td[' + str(td) + '][contains(@class, "-icon")]//span')]
def get_info(browser, td, class_td = ''):
    return [info.text for info in browser.find_elements_by_xpath('//table//td[' + str(td) + '][contains(@class, ' + class_td + ')]')]

game_details = pd.DataFrame()
for game in game_link:
    browser.get(game)
    sleep(1)
    date = browser.find_elements_by_xpath('//div[@data-ng-if="game.league"]//p')[0].text
    date = {'date': re.search("([0-9]{2}\.[0-9]{2}\.[0-9]{4})", date).group(1)}
    position = browser.find_elements_by_xpath('//table//tr//th[contains(text(), "' + team + '")]')[0].get_attribute('class')
    if position == '':
        info_td = 5
        class_td = '""'
    else:
        info_td = 1
        class_td = '"' + position + '"'
    time = {'time': get_time(browser)}
    info = {'info': get_info(browser, info_td, class_td = class_td)}
    game_details_temp = pd.DataFrame({**date, **time, **info})
    game_details_temp = game_details_temp.loc[game_details_temp['info'] != '']
    game_details = game_details.append(game_details_temp)

# Merging by date
stats = game_details.merge(game_info, how = 'left', on = 'date')

# Cleaning - Regex to clean info


# id (cpm_opponent_date), cpm, opponent, date, home, time, action (penalty, score, assist), player, min, cpm_score, team_score
