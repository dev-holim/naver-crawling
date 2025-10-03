<?php
/**
 * 네이버 쇼핑 크롤링 웹 인터페이스
 * 
 * 이 파일은 네이버 쇼핑의 베스트 카테고리 상품 정보를 크롤링하는
 * Python 스크립트를 실행하는 웹 인터페이스입니다.
 */

// 오류 표시 설정
error_reporting(E_ALL);
ini_set('display_errors', 1);

// 헤더 설정
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// OPTIONS 요청 처리 (CORS preflight)
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

/**
 * 크롤링 설정
 */
class NaverCrawlingConfig {
    
    /**
     * 단일 URL 크롤링 설정
     */
    public static function getSingleUrlConfig() {
        return [
            'url' => 'https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000003&categoryDemo=A00&categoryRootCategoryId=50000003&period=P1D&tr=nwbhi'
        ];
    }
    
    /**
     * 다중 URL 크롤링 설정
     */
    public static function getMultiUrlConfig() {
        return [
            '50000003' => 'https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000003&categoryDemo=A00&categoryRootCategoryId=50000003&period=P1D&tr=nwbhi',
            '50000000' => 'https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000000&categoryDemo=A00&categoryRootCategoryId=50000000&period=P1D&tr=nwbhi',
        ];
    }
}

/**
 * 크롤링 실행 클래스
 */
class NaverCrawlingExecutor {
    
    private $pythonCommand;
    private $scriptPath;
    
    public function __construct() {
        // Python 명령어 설정 (환경에 따라 조정 필요)
        $this->pythonCommand = 'python3'; // 또는 'python'
        $this->scriptPath = __DIR__;
    }
    
    /**
     * 단일 URL 크롤링 실행
     */
    public function executeSingleUrl($url = null) {
        try {
            $crawlData = $url ? ['url' => $url] : NaverCrawlingConfig::getSingleUrlConfig();
            $encodedData = json_encode($crawlData, JSON_UNESCAPED_UNICODE);
            
            $command = sprintf(
                '%s %s/one_by_one.py %s',
                $this->pythonCommand,
                $this->scriptPath,
                escapeshellarg($encodedData)
            );
            
            return $this->executeCommand($command);
            
        } catch (Exception $e) {
            return $this->createErrorResponse(500, '단일 URL 크롤링 실행 중 오류: ' . $e->getMessage());
        }
    }
    
    /**
     * 다중 URL 크롤링 실행
     */
    public function executeMultiUrl($urls = null) {
        try {
            $crawlData = $urls ?: NaverCrawlingConfig::getMultiUrlConfig();
            $encodedData = json_encode($crawlData, JSON_UNESCAPED_UNICODE);
            
            $command = sprintf(
                '%s %s/multi.py %s',
                $this->pythonCommand,
                $this->scriptPath,
                escapeshellarg($encodedData)
            );
            
            return $this->executeCommand($command);
            
        } catch (Exception $e) {
            return $this->createErrorResponse(500, '다중 URL 크롤링 실행 중 오류: ' . $e->getMessage());
        }
    }
    
    /**
     * 명령어 실행
     */
    private function executeCommand($command) {
        $output = [];
        $returnCode = 0;
        
        exec($command, $output, $returnCode);
        
        if ($returnCode !== 0) {
            return $this->createErrorResponse(500, 'Python 스크립트 실행 실패 (코드: ' . $returnCode . ')');
        }
        
        if (empty($output)) {
            return $this->createErrorResponse(404, '크롤링 결과가 없습니다');
        }
        
        $result = json_decode($output[0], true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            return $this->createErrorResponse(500, 'JSON 파싱 오류: ' . json_last_error_msg());
        }
        
        return [
            'success' => true,
            'data' => $result,
            'timestamp' => date('Y-m-d H:i:s')
        ];
    }
    
    /**
     * 오류 응답 생성
     */
    private function createErrorResponse($code, $message) {
        http_response_code($code);
        return [
            'success' => false,
            'error' => $message,
            'timestamp' => date('Y-m-d H:i:s')
        ];
    }
}

/**
 * 메인 실행 로직
 */
try {
    $executor = new NaverCrawlingExecutor();
    $response = null;
    
    // 요청 방식에 따른 처리
    $requestMethod = $_SERVER['REQUEST_METHOD'];
    $requestData = null;
    
    // POST 데이터 읽기
    if ($requestMethod === 'POST') {
        $input = file_get_contents('php://input');
        if (!empty($input)) {
            $requestData = json_decode($input, true);
        }
    }
    
    // URL 파라미터에서 크롤링 타입 확인
    $crawlType = $_GET['type'] ?? 'multi';
    
    switch ($crawlType) {
        case 'single':
            $url = $_GET['url'] ?? $requestData['url'] ?? null;
            $response = $executor->executeSingleUrl($url);
            break;
            
        case 'multi':
        default:
            $urls = $_GET['urls'] ?? $requestData['urls'] ?? null;
            $response = $executor->executeMultiUrl($urls);
            break;
    }
    
    // 응답 출력
    echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => '서버 오류: ' . $e->getMessage(),
        'timestamp' => date('Y-m-d H:i:s')
    ], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
}

?>