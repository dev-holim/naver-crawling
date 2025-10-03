import sys
import json
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from crawler_base import BaseNaverCrawler

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NaverShopCrawler(BaseNaverCrawler):
    """네이버 쇼핑 베스트 카테고리 크롤러 (단일 URL)"""
    
    def crawl_url(self, url):
        """
        URL에서 상품 정보 크롤링
        
        Args:
            url (str): 크롤링할 네이버 쇼핑 URL
            
        Returns:
            dict: 크롤링 결과
        """
        try:
            logger.info(f"크롤링 시작: {url}")
            self.driver.get(url)
            
            # 페이지 로딩 대기
            self._wait_for_page_load()
            
            # 스크롤하여 모든 상품 로드
            self._scroll_to_load_all()
            
            # 상품 정보 추출
            products = self._extract_product_data()
            
            result = {
                "code": 200,
                "data": products,
                "count": len(products),
                "url": url
            }
            
            logger.info(f"크롤링 완료: {len(products)}개 상품 수집")
            return result
            
        except Exception as e:
            logger.error(f"크롤링 실패: {e}")
            return {"code": 404, "error": str(e)}
    
    def _extract_product_data(self):
        """상품 데이터 추출 (one_by_one.py 전용)"""
        try:
            # 컨테이너 요소 찾기
            container = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="container"]'))
            )
            
            category_panel = container.find_element(By.CLASS_NAME, "category_panel")
            product_list = category_panel.find_element(By.TAG_NAME, "ul")
            product_items = product_list.find_elements(By.TAG_NAME, "li")
            
            products = []
            
            for li in product_items:
                try:
                    product_data = self._extract_single_product(li)
                    if product_data:
                        products.append(product_data)
                except Exception as e:
                    logger.warning(f"상품 데이터 추출 실패: {e}")
                    continue
            
            return products
            
        except TimeoutException:
            logger.error("상품 목록 요소를 찾을 수 없습니다")
            return []
        except Exception as e:
            logger.error(f"상품 데이터 추출 중 오류: {e}")
            return []

def main():
    """메인 실행 함수"""
    try:
        # 명령행 인수에서 JSON 데이터 읽기
        if len(sys.argv) < 2:
            logger.error("URL 데이터가 제공되지 않았습니다")
            print(json.dumps({"code": 400, "error": "URL 데이터가 필요합니다"}))
            return
        
        post_value = sys.argv[1]
        dict_data = json.loads(post_value)
        
        if 'url' not in dict_data:
            logger.error("URL이 제공되지 않았습니다")
            print(json.dumps({"code": 400, "error": "URL이 필요합니다"}))
            return
        
        url = dict_data['url']
        
        # 크롤러 생성 및 실행
        crawler = NaverShopCrawler(headless=False)
        
        try:
            result = crawler.crawl_url(url)
            print(json.dumps(result, ensure_ascii=False))
        finally:
            crawler.close()
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 오류: {e}")
        print(json.dumps({"code": 400, "error": "잘못된 JSON 형식입니다"}))
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        print(json.dumps({"code": 500, "error": str(e)}))

if __name__ == "__main__":
    main()
