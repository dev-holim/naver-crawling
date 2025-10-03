<?php
// one_by_one.py
// $CrawlData = [
//   'url' => 'https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000003&categoryDemo=A00&categoryRootCategoryId=50000003&period=P1D&tr=nwbhi',
// ];


// multi.py
$CrawlData = [
  '50000003' => 'https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000003&categoryDemo=A00&categoryRootCategoryId=50000003&period=P1D&tr=nwbhi',
  '50000000' => 'https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000000&categoryDemo=A00&categoryRootCategoryId=50000000&period=P1D&tr=nwbhi',
];


$EncodeCrawlData = json_encode($CrawlData);

$command = "py ./multi.py " . $EncodeCrawlData;
$command = str_replace('"','\"',$command);
exec($command,$output);
if(!empty($output[0])){
  $outputArr = json_decode($output[0],true);
}else{
  $outputArr = [];
}

var_dump($outputArr);


?>