# import os
import time
import numpy as np
# import subprocess
import sys
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# selenium 드라이버를 크롬버젼에 맞춰 다운로드하고 경로를 찾을 필요 없이 자동적으로 업데이트 되
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller

class CrawlingNaverShopList:
  ''' 기본 크롬 브라우저 설정 '''
  def __init__(self,url):
    chromedriver_autoinstaller.install()  # chromedriver 자동 다운로드
    portNum = "9515"
    # os.startfile(f"runChromeDebug{portNum}.bat")  # 디버그 모드로 chrome 실행
    # self.process = subprocess.Popen(['start', f"runChromeDebug{portNum}.bat"], shell=True)

    # subprocess.Popen(r'C:/Program Files/Google/Chrome/Application/chrome.exe --remote-debugging-port=9222')
    # 디버거 크롬 동작
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9515")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # chrome_options.add_argument('--headless')  # 브라우저를 띄우지 않고 실행
    chrome_options.add_argument("--no-sandbox"); # OS security model
    chrome_options.add_argument('disable-gpu') # 하드웨어 가속 안함
    chrome_options.add_argument('--start-fullscreen') # 전체화면
    self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options) # port=portNum
    self.driver.get(url)
  
  def init_(self):
    self.scroll_page()
    HTMLCONTENTS = self.get_scrap_html()
    return HTMLCONTENTS

  ''' html 스크래핑(정보를 추출) '''
  def get_scrap_html(self):
    try:
      # temperature = driver.find_element_by_xpath('//*[@id="main_pack"]/section[1]/div[1]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[2]/strong').text
      element = WebDriverWait(self.driver,3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]')))
      element = element.find_element(By.CLASS_NAME,"category_panel")
      ul = element.find_element(By.TAG_NAME,"ul")
      # ul = element.find_element(By.TAG_NAME,"ul").get_attribute('innerHTML')
      li_all = ul.find_elements(By.TAG_NAME,"li")

      return_data = []
      for li in li_all:
        text_elements = li.find_element(By.XPATH, "a[1]/div[2]/div[1]") # 텍스트 div box
        # 최저가 여부
        if "최저" in text_elements.text:
          is_max_low = True
        else:
          is_max_low = False
        
        try:
          span_element = text_elements.find_element(By.TAG_NAME,"span")
          svg_element = text_elements.find_element(By.TAG_NAME,"svg")
        except:
          span_element = ""
          svg_element = ""

        # 네이버 최저값
        price_text = text_elements.find_element(By.TAG_NAME,"strong").text
        if "," in price_text:
          price_text = price_text.replace(",","")

        # 배송비
        delivery_text = ""
        if span_element and svg_element:
          delivery_text = span_element.get_attribute('innerHTML').split('</svg>')[1]
          if "원" in delivery_text:
            delivery_text = delivery_text.replace("원","")
          if "," in delivery_text:
            delivery_text = delivery_text.replace(",","")

        return_data.append({
          'productId':li.get_attribute("id"),  # 네이버 상품 id
          'isMaxLow':is_max_low,  # 최저가 여부
          'lowPrice':price_text,  # 네이버 최저값
          'deliveryPrice':delivery_text,  # 배송비
        })
      return json.dumps({"data":return_data,"count":len(li_all)})
    except:
      return {'code':404}
    finally:
      self.driver.quit()

  ''' scroll action '''
  def scroll_page(self):
    # scroll pause 시간
    SCROLL_PAUSE_TIME = np.random.randint(1,3)

    # scroll 높이
    last_height = self.driver.execute_script("return document.body.scrollHeight")

    while True:
      self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

      # 봇으로 감지되지 않도록 임의의 PAUSE TIME 설정
      time.sleep(SCROLL_PAUSE_TIME)
      new_height = self.driver.execute_script("return document.body.scrollHeight")
      if new_height == last_height:
        break
      last_height = new_height
    
     
POST_VALUE = sys.argv[1]
dict_data = json.loads(POST_VALUE)
try:
  if dict_data['url']:
    CrawlingClass = CrawlingNaverShopList(dict_data['url'])
    data = CrawlingClass.init_()
    print(data)
except:
  print('error')
