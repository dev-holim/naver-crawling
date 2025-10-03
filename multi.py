import time
import sys
import json
import logging
from crawler_base import BaseNaverCrawler
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiNaverShopCrawler(BaseNaverCrawler):
    """다중 URL 네이버 쇼핑 크롤러"""
    
    def crawl_multiple_urls(self, url_dict):
        """
        여러 URL에서 상품 정보 크롤링
        
        Args:
            url_dict (dict): {카테고리ID: URL} 형태의 딕셔너리
            
        Returns:
            list: 각 카테고리별 크롤링 결과
        """
        results = []
        
        for category_id, url in url_dict.items():
            try:
                logger.info(f"카테고리 {category_id} 크롤링 시작: {url}")
                
                # 페이지 이동
                self.driver.get(url)
                
                # 페이지 로딩 대기
                self._wait_for_page_load()
                
                # 상품 데이터 추출
                products = self._extract_product_data()
                
                # 결과 저장
                category_result = {
                    "code": 200,
                    "data": products,
                    "count": len(products),
                    "categoryId": category_id,
                    "url": url
                }
                
                results.append({category_id: category_result})
                logger.info(f"카테고리 {category_id} 크롤링 완료: {len(products)}개 상품")
                
                # 요청 간 대기 (봇 탐지 방지)
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"카테고리 {category_id} 크롤링 실패: {e}")
                error_result = {
                    "code": 404,
                    "error": str(e),
                    "categoryId": category_id,
                    "url": url
                }
                results.append({category_id: error_result})
        
        return results
    
    def _extract_product_data(self):
        """상품 데이터 추출 (multi.py 전용 - 순서 정보 포함)"""
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
                    product_data = self._extract_single_product_with_sequence(li)
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
    
    def _extract_single_product_with_sequence(self, li_element):
        """단일 상품 데이터 추출 (순서 정보 포함)"""
        try:
            # 상품 ID
            product_id = li_element.get_attribute("id")
            
            # 순서 정보
            try:
                sequence_element = li_element.find_element(By.XPATH, "a[1]/div[1]/div[1]/span[1]")
                sequence = sequence_element.text
            except:
                sequence = ""
            
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
            except:
                pass
            
            return {
                "sequence": sequence,
                "productId": product_id,
                "isMaxLow": is_max_low,
                "lowPrice": price_text,
                "deliveryPrice": delivery_price
            }
            
        except Exception as e:
            logger.warning(f"상품 정보 추출 실패: {e}")
            return None

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
        
        if not dict_data or len(dict_data) == 0:
            logger.error("URL 데이터가 비어있습니다")
            print(json.dumps({"code": 400, "error": "URL 데이터가 비어있습니다"}))
            return
        
        # 크롤러 생성 및 실행
        crawler = MultiNaverShopCrawler(headless=False)
        
        try:
            results = crawler.crawl_multiple_urls(dict_data)
            print(json.dumps(results, ensure_ascii=False))
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