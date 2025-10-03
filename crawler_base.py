"""
네이버 쇼핑 크롤러 공통 기능 모듈
"""
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseNaverCrawler:
    """네이버 크롤러 기본 클래스"""
    
    def __init__(self, headless=False):
        """
        기본 크롤러 초기화
        
        Args:
            headless (bool): 헤드리스 모드 실행 여부
        """
        self.driver = None
        self.headless = headless
        self._setup_driver()
    
    def _setup_driver(self):
        """Chrome 드라이버 설정"""
        try:
            # chromedriver 자동 설치
            chromedriver_autoinstaller.install()
            
            # Chrome 옵션 설정
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            if self.headless:
                chrome_options.add_argument('--headless')
            else:
                chrome_options.add_argument('--start-fullscreen')
            
            # 드라이버 생성
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 봇 탐지 방지를 위한 스크립트 실행
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome 드라이버 초기화 완료")
            
        except Exception as e:
            logger.error(f"드라이버 초기화 실패: {e}")
            raise
    
    def _wait_for_page_load(self, timeout=10):
        """페이지 로딩 대기"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="container"]'))
            )
            logger.info("페이지 로딩 완료")
        except TimeoutException:
            logger.warning("페이지 로딩 타임아웃")
    
    def _scroll_to_load_all(self):
        """페이지 끝까지 스크롤하여 모든 상품 로드"""
        logger.info("스크롤 시작")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        max_scrolls = 10  # 무한 스크롤 방지
        
        while scroll_count < max_scrolls:
            # 페이지 끝으로 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # 랜덤 대기 시간 (1-2초)
            time.sleep(1)
            
            # 새로운 높이 확인
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
                
            last_height = new_height
            scroll_count += 1
        
        logger.info(f"스크롤 완료 ({scroll_count}회)")
    
    def _extract_single_product(self, li_element):
        """단일 상품 데이터 추출"""
        try:
            # 상품 ID
            product_id = li_element.get_attribute("id")
            
            # 텍스트 요소
            text_elements = li_element.find_element(By.XPATH, "a[1]/div[2]/div[1]")
            
            # 최저가 여부 확인
            is_max_low = "최저" in text_elements.text
            
            # 가격 정보
            price_element = text_elements.find_element(By.TAG_NAME, "strong")
            price_text = price_element.text.replace(",", "")
            
            # 배송비 정보
            delivery_price = ""
            try:
                span_element = text_elements.find_element(By.TAG_NAME, "span")
                svg_element = text_elements.find_element(By.TAG_NAME, "svg")
                
                if span_element and svg_element:
                    delivery_html = span_element.get_attribute('innerHTML')
                    if '</svg>' in delivery_html:
                        delivery_text = delivery_html.split('</svg>')[1]
                        delivery_price = delivery_text.replace("원", "").replace(",", "")
            except NoSuchElementException:
                pass
            
            return {
                "productId": product_id,
                "isMaxLow": is_max_low,
                "lowPrice": price_text,
                "deliveryPrice": delivery_price
            }
            
        except Exception as e:
            logger.warning(f"상품 정보 추출 실패: {e}")
            return None
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            logger.info("드라이버 종료")
