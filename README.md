# 네이버 쇼핑 크롤링 프로젝트

네이버 쇼핑의 베스트 카테고리 상품 정보를 자동으로 크롤링하는 Python/Selenium 기반 웹 스크래핑 프로젝트입니다.

## 📋 프로젝트 개요

이 프로젝트는 네이버 쇼핑의 베스트 카테고리 페이지에서 상품 정보를 자동으로 수집하는 크롤링 도구입니다. PHP와 Python을 연동하여 웹 서비스로 구현되어 있으며, 여러 카테고리를 동시에 크롤링할 수 있습니다.

### 주요 기능
- 🔍 네이버 쇼핑 베스트 카테고리 상품 정보 추출
- 📊 상품 순위, 최저가 여부, 가격, 배송비 정보 수집
- 🚀 단일 URL 및 다중 URL 동시 크롤링 지원
- 🤖 자동 스크롤 및 봇 감지 회피 기능
- 🌐 PHP 웹 인터페이스를 통한 쉬운 사용

## 🛠️ 기술 스택

- **Python 3.x**
- **Selenium WebDriver**
- **Chrome WebDriver**
- **PHP 7.x+**
- **JSON 데이터 처리**

## 📦 설치 및 설정

### 1. 필수 요구사항
```bash
# Python 패키지 설치
pip install selenium
pip install webdriver-manager
pip install chromedriver-autoinstaller
pip install numpy

# Chrome 브라우저 설치 (최신 버전 권장)
```

### 2. 프로젝트 구조
```
naver_crawling/
├── app.php              # PHP 웹 인터페이스 (개선됨)
├── one_by_one.py        # 단일 URL 크롤링 스크립트 (리팩토링됨)
├── multi.py             # 다중 URL 크롤링 스크립트 (리팩토링됨)
├── crawler_base.py      # 공통 크롤링 기능 모듈 (신규)
├── chromedriver         # Chrome 드라이버 실행파일
└── README.md            # 프로젝트 문서
```

## 🚀 사용법

### 방법 1: PHP 웹 인터페이스 사용 (권장)

1. **웹 서버에서 실행**
```bash
php app.php
```

2. **API 엔드포인트**
   - **다중 URL 크롤링**: `GET/POST http://localhost/app.php?type=multi`
   - **단일 URL 크롤링**: `GET/POST http://localhost/app.php?type=single&url=네이버URL`
   
3. **POST 요청 예시**
```bash
# 다중 URL 크롤링
curl -X POST http://localhost/app.php?type=multi \
  -H "Content-Type: application/json" \
  -d '{
    "urls": {
      "50000003": "https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000003&categoryDemo=A00&categoryRootCategoryId=50000003&period=P1D&tr=nwbhi",
      "50000000": "https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000000&categoryDemo=A00&categoryRootCategoryId=50000000&period=P1D&tr=nwbhi"
    }
  }'

# 단일 URL 크롤링
curl -X POST http://localhost/app.php?type=single \
  -H "Content-Type: application/json" \
  -d '{"url": "https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000003&categoryDemo=A00&categoryRootCategoryId=50000003&period=P1D&tr=nwbhi"}'
```

### 방법 2: Python 직접 실행

#### 단일 URL 크롤링
```bash
python one_by_one.py '{"url": "https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000003&categoryDemo=A00&categoryRootCategoryId=50000003&period=P1D&tr=nwbhi"}'
```

#### 다중 URL 크롤링
```bash
python multi.py '{"50000003": "https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000003&categoryDemo=A00&categoryRootCategoryId=50000003&period=P1D&tr=nwbhi", "50000000": "https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000000&categoryDemo=A00&categoryRootCategoryId=50000000&period=P1D&tr=nwbhi"}'
```

## 📊 데이터 구조

### 응답 JSON 형식
```json
{
  "data": [
    {
      "sequence": "1",
      "productId": "product_12345",
      "isMaxLow": true,
      "lowPrice": "29900",
      "deliveryPrice": "2500"
    }
  ],
  "count": 50
}
```

### 필드 설명
- `sequence`: 상품 순위
- `productId`: 네이버 상품 고유 ID
- `isMaxLow`: 최저가 여부 (true/false)
- `lowPrice`: 최저 가격 (숫자만)
- `deliveryPrice`: 배송비 (숫자만)

## ⚙️ 설정 옵션

### Chrome 옵션 설정
```python
# 브라우저 옵션 커스터마이징
chrome_options.add_argument('--headless')  # 백그라운드 실행
chrome_options.add_argument('--window-size=1920,1080')  # 창 크기 설정
```

### 스크롤 설정
```python
SCROLL_PAUSE_TIME = np.random.randint(1,3)  # 스크롤 간격 (1-3초)
```

## 🔧 문제 해결

### 자주 발생하는 문제들

1. **Chrome 드라이버 오류**
   ```bash
   # 해결방법: chromedriver-autoinstaller가 자동으로 처리
   chromedriver_autoinstaller.install()
   ```

2. **네이버 봇 차단**
   - User-Agent 설정으로 해결
   - 랜덤 스크롤 간격으로 자연스러운 행동 모방

3. **요소 찾기 실패**
   - `WebDriverWait`로 요소 로딩 대기
   - 예외 처리로 안정성 확보

## 🔧 최근 개선 사항

### 코드 리팩토링 (2024)
- ✅ **모듈화**: 공통 기능을 `crawler_base.py`로 분리
- ✅ **에러 처리 강화**: 상세한 로깅 및 예외 처리 추가
- ✅ **코드 구조 개선**: 클래스 기반 설계로 가독성 향상
- ✅ **PHP API 개선**: RESTful API 형태로 재구성
- ✅ **봇 탐지 방지**: 더 강력한 탐지 회피 기능 추가
- ✅ **로깅 시스템**: 상세한 실행 로그 및 디버깅 정보 제공

### 주요 개선점
1. **코드 재사용성**: 중복 코드 제거 및 공통 모듈 분리
2. **안정성**: 강화된 예외 처리 및 오류 복구 메커니즘
3. **유지보수성**: 명확한 클래스 구조 및 문서화
4. **확장성**: 새로운 크롤링 기능 추가 용이
5. **API 개선**: 표준 HTTP 메서드 및 JSON 응답 지원

## 📝 주의사항

- ⚠️ 네이버 쇼핑의 이용약관을 준수하여 사용하세요
- 🚫 과도한 요청은 IP 차단의 원인이 될 수 있습니다
- 🔄 정기적인 업데이트로 사이트 구조 변경에 대응하세요
- 📊 수집된 데이터는 개인적인 용도로만 사용하세요
- 🛡️ 봇 탐지 방지를 위해 적절한 대기 시간을 설정하세요

