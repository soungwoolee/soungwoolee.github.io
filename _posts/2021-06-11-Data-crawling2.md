
# Web Scraping2( data crawling )

 
## 1. import library
크롤링 시 필요한 패키지를 설치하고 import 해보자.😃 selenium 은 웹을 제어하기 위한 패키지이다.
브라우저는 크롬으로 진행할 것이므로 자신의 크롬 버전에 맞는 **크롬 웹 드라이버**를 설치해야 한다. 아래의 링크에서 설치할 수 있다,
 https://sites.google.com/a/chromium.org/chromedriver/downloads 

 
![enter image description here](https://github.com/soungwoolee/soungwoolee.github.io/blob/master/images/rightclick.jpg?raw=true)

 나의 크롬 버전은 크롬 주소창에 "Chrome://version" 을 입력하면 알 수 있다. driver의 경로를 지정할 필요 없이 다운받은 webdriver를 복사해서 작업 디렉토리에도 붙여넣는 것을 추천한다.


    # inatall packages
    pip install selenium
    pip install requests
    pip install bs4
   

    from selenium import webdriver
    driver = webdriver.Chrome('./chromedriver.exe') # driver 를 크롬브라우저로 정의함
    from bs4 import BeautifulSoup
    import pandas as pd
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC # Explicitly wait 쓸 때 필요
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.alert import Alert # 알림 뜰 때 필요


    import warnings
    warnings.filterwarnings(action='ignore')
    import re # 정규식
    from tqdm import tqdm, notebook # jupyternotebook 전용 tqdm

   - 공공데이터 포털 URL : https://www.data.go.kr/tcs/dss/selectDataSetList.do?dType=FILE&keyword=&detailKeyword=&publicDataPk=&recmSe=&detailText=&relatedKeyword=&commaNotInData=&commaAndData=&commaOrData=&must_not=&tabId=&dataSetCoreTf=&coreDataNm=&sort=&relRadio=&orgFullName=&orgFilter=&org=&orgSearch=&currentPage=1&perPage=10&brm=&instt=&svcType=&kwrdArray=&extsn=&coreDataNmArray=&pblonsipScopeCode=

 
## 2. Scrape any Feature of a dataset

지난 포스팅에서 웹 크롤링의 뜻과 필요한 html 배경지식에 대해 간단히 알아보았다. 이제 실습 시간이다. 직접 [공공데이터포털](https://www.data.go.kr/index.do)에 접속해서 파일데이터 목록 중 가져오고 싶은 정보를 추출해보자.
- 상단 배너의 데이터 찾기 -> 데이터목록 -> 파일 데이터
위 순서대로 들어가면 파일데이터가 39000여개가 있는 것을 확인할 수 있다. 
#
    # 크롬창을 켠다
    driver = webdriver.Chrome('./chromedriver.exe')
    # get() 으로 원하는 웹사이트에 접속한다 , url 은 파일데이터 1page
    driver.get(url) 
    driver.maximize_window() # 창 최대화 (꼭 안해도 됨)
    driver.implicitly_wait(3) # 명령을 실행할 때까지 최대 3초를 대기함

 이제 원하는 페이지에 접근했다. 페이지 당 데이터셋 10개를 볼 수 있고, 등록된 정보는 데이터셋의 이름, 요약설명, 제공기관, 조회수 그리고 카테고리 등이 있다. 먼저 데이터 이름부터 가져와보자. 
그러기 위해서는 이 html 로 되어있는 이 페이지의 정보를 전부 받아와야 한다.
## Selenium vs Requests
페이지의 html source를 받아오는 방법은 크게 두가지가 있다.

### Requests 
먼저 Requests 는 웹페이지(html)를 읽어오기 위한 파이썬 패키지이다. 
`html = requests.get(url).text`
### Selenium
selenium 은 웹을 제어할 수 있는 파이썬 패키지로 웹 페이지를 자동화하는 것이 목적이다. 정의해놓은 selnium webdriver 로 page_source를 불러올 수 있다. 

    #(원하는 페이지에 접근한 상태에서)
    html = driver.page_source
### 비교
본 예시에서 request 이든 selenium이든 결과는 동일하다.
Request 는 웹페이지를 빠르게 읽어오고 정적 크롤링에 적합하다. 반면 Selenium은 웹 페이지를 자동화하는 것이 목적이다. request 에 비해 느리지만 동적 크롤링, 즉 크롤링 중 로그인을 하거나 클릭을 해야 할 경우 적합하다.

  ## Beutiful Soup
현재 받아온 html 은 **파이썬이 객체로 받아들일 수 없는 상태**이다. 이를 가능하게 해주는 것이 Beautiful Soup 패키지이다. Beautiful Soup 도 다른 패키지와 마찬가지로 크롤링에 필요한 필수 패키지이다. Beautiful soup 는 **추출한 정보 중 조건에 맞는 element를 수집하거나 element 의 속성과 텍스트**를 가져올 수 있다. 데이터 이름의 element 정보를 알기 위해 **개발자 창**을 켜보자!

 ![enter image description here](https://github.com/soungwoolee/soungwoolee.github.io/blob/master/images/f12.jpg?raw=true)
 
개발자 창에서 화살표 모양의 버튼을 찾아볼 수 있다. 이 단추를 클릭한 후 사이트의 데이터 이름을 다시 클릭하면 그 **개체가 html 상에서 어느 위치에 있는지 알 수 있다**. 반대로 이 버튼을 누르고 개발자 창에서 탐색하면 사이트에서 어느 개체에 해당하는지 알 수 있다.
이어서 개발자창의 해당 줄을 우클릭하면 element를 복사할 수 있다. 여러가지 항목을 copy 할 수 있지만 지금은 **Copy element** 를 눌러보자


![rightclick](https://github.com/soungwoolee/soungwoolee.github.io/blob/master/images/rightclick.jpg?raw=true)

복사한 element를 붙여넣기 하면 다음과 같이 span tag에  class 는 title로 구성되어 있고 시작 태그와 끝 태그 사이에 우리가 원하는 제목 텍스트가 있는 것을 확인할 수 있다.

    < span class="title">
		    부산광역시_사하구_특수의료장비현황
						    < /span>


이제 element를 알았으니 

    soup.find("tag", attrs = {"attribute":"argument"}) 

위와 같은 형식으로 해당 요소를 가져오면 된다.
soup.find() 는 조건에 맞는 첫번째 요소를 가져온다. 특성 값이 없는 경우 attrs = 부분을 생략하면 된다.


    import requests
    # 크롬창 open
    driver = webdriver.Chrome('./chromedriver.exe')
    # get() 으로 원하는 웹사이트에 접속한다 , url 은 파일데이터 1page
    url = 'https://www.data.go.kr/tcs/dss/selectDataSetList.do?dType=FILE&keyword=&detailKeyword=&publicDataPk=&recmSe=&detailText=&relatedKeyword=&commaNotInData=&commaAndData=&commaOrData=&must_not=&tabId=&dataSetCoreTf=&coreDataNm=&sort=&relRadio=&orgFullName=&orgFilter=&org=&orgSearch=&currentPage=1&perPage=10&brm=&instt=&svcType=&kwrdArray=&extsn=&coreDataNmArray=&pblonsipScopeCode='  
    req = requests.get(url)
    driver.implicitly_wait(3)
    
    # html 소스 가져오기
    html = req.text
    
    # BeautifulSoup 라이브러리를 통해 태그로 되어있는 html 을 파싱함 
    soup = BeautifulSoup(html, 'html.parser')
    time.sleep(0.5)
    driver.implicitly_wait(5)
    # name 에 데이터 이름의 조건 적용하기
    name = soup.find("span", attrs = {"class":"title"})
    name = name.get_text().strip() #soup 로 element 에 접근 후 get_text로 해당 element 의 text를 가져옴, stirp ->공백제거
    
    print('데이터 이름: ',name)
    
    #현재 열어놓은 크롬창 닫기
    driver.close()
    
    # 결과 (데이터 목록이 업데이트 되므로 동일한 코드로 해도 다른 데이터 제목이 출력될 것이다.) 
    데이터 이름:  경기도 양주시_지방세ARS간편납부시스템_납부금액통계

잘 추출된다. 그럼 **두번째 데이터 셋의 데이터 이름**은 어떻게 가져오는 것이 좋을까? 두번째 데이터 이름 부분에도 마찬가지로 우클릭 후 copy element 로 태그정보를 확인해보자

![rightclick2](https://github.com/soungwoolee/soungwoolee.github.io/blob/master/images/rightclick2.jpg?raw=true)

1번데이터와 2번데이터 모두 span 태그에 attribute 는 class 이고 argument 는 title로 동일하다. 따라서 **현재페이지에 있는 10개 데이터셋의 이름은 모두 동일한 특성으로 불러올 수 있을 것**이다. **find** 는 조건에 맞는 첫번째 요소만 가져오는 반면 **find_all 은 조건에 맞는 요소 전부에 접근**한다. 코드로 살펴보자.

    # find_all
    driver = webdriver.Chrome('./chromedriver.exe')
    # url , 파일데이터 1page
    url = 'https://www.data.go.kr/tcs/dss/selectDataSetList.do?dType=FILE&keyword=&detailKeyword=&publicDataPk=&recmSe=&detailText=&relatedKeyword=&commaNotInData=&commaAndData=&commaOrData=&must_not=&tabId=&dataSetCoreTf=&coreDataNm=&sort=&relRadio=&orgFullName=&orgFilter=&org=&orgSearch=&currentPage=1&perPage=10&brm=&instt=&svcType=&kwrdArray=&extsn=&coreDataNmArray=&pblonsipScopeCode='  
    req = requests.get(url)
    driver.implicitly_wait(3)
    html = req.text
    
    # BeautifulSoup 라이브러리를 통해 태그로 되어있는 html 을 파싱함 
    soup = BeautifulSoup(html, 'html.parser')
    time.sleep(0.5)
    driver.implicitly_wait(5)
    
    names = soup.find_all("span", attrs = {"class":"title"})
    print('조건에 맞는 요소 개수: ',len(names)) # 조건에 맞는 요소가 몇개인지 확인 
    
    #조건에 맞는 요소의 text 개별 출력
    for i in range(len(names)):
        print(i+1, 'th data')
        name = names[i].get_text().strip()
        print('데이터 이름: ',name)
        
    driver.close()
![(2021.06.11 기준 출력 결과)](https://github.com/soungwoolee/soungwoolee.github.io/blob/master/images/0611nameresult.jpg?raw=true)

( 작성 중 중간에 텀이 생겨서 데이터 목록에 변화가 생겼지만 잘 동작한다!)

위의 코드를 보면 **names 에는 조건에 맞는 '데이터 이름'의 source가 전부 저장**되어 있다. 요소를 잘 가져왔는지 간단히 확인하는 방법은
 

    print(len(names))

 으로 **조건에 맞는 요소의 수**를 확인해보는 것이다.

 '데이터 이름'의 경우 **해당값(조건에 맞는 요소의 수)이 '10' 이어야하는데 0 이거나 10 이상이라면 접근에 실패했다는 뜻**이므로 다른 방법으로 접근해야 한다. 
 다수의 source (여기선 names)에는 바로 get_text() 함수를 적용할 수 없어서 **for 문을 통해 name 을 따로 지정하고 text를 출력**했다.

Request 를 사용하지 않고 html을 받아와도 결과는 동일하다. 바뀐부분에 주목해보자.

    driver = webdriver.Chrome('./chromedriver.exe')
    url = 'https://www.data.go.kr/tcs/dss/selectDataSetList.do?dType=FILE&keyword=&detailKeyword=&publicDataPk=&recmSe=&detailText=&relatedKeyword=&commaNotInData=&commaAndData=&commaOrData=&must_not=&tabId=&dataSetCoreTf=&coreDataNm=&sort=&relRadio=&orgFullName=&orgFilter=&org=&orgSearch=&currentPage=1&perPage=10&brm=&instt=&svcType=&kwrdArray=&extsn=&coreDataNmArray=&pblonsipScopeCode='  
    
    #바뀐 부분
    driver.get(url)
    driver.implicitly_wait(3)
    html = driver.page_source
    
    soup = BeautifulSoup(html, 'html.parser')
    time.sleep(0.5)
    driver.implicitly_wait(5)
    names = soup.find_all("span", attrs = {"class":"title"})
    print('조건에 맞는 요소 개수: ',len(names))
    for i in range(len(names)):
        print(i+1, 'th data')
        name = names[i].get_text().strip()
        print('데이터 이름: ',name)
        
    driver.close()

현재까지의 데이터 수집 과정을 정리해보자

-   Requests 혹은 Selenium으로 html source를 받아온다
-   받아온 source를 beautiful.soup로 파이썬에서 활용할 수 있는 객체로 만든다.
-   find(find_all)로 조건에 맞는 element에 접근한다.

이 방법만 활용해도 대부분의 정보에 접근할 수 있다. 하지만 크롤링을 하다보면 soup로는 해결할 수 없는 다음과 같은 상황에 놓이게 된다.😥

-   실제로는 다른 정보인데 html에서  동일한 tag, attribue, argument를 지닌 경우
-   특정 개체를 클릭해야 하는 상황
-   element의 text가 아닌 특성을 가져오고 싶을 때

 soup 는 element의 text를 얻는데 특화되어 있어서 위의 상황에서는 별 쓸모가 없어진다. 이런 경우 selenium 으로 원하는 element를 찾아야 하는데 가장 간단한 방법이 **x path로 접근**하는 것이다.  다음 포스트에서 언급한 문제 상황을 어떻게 해결할지 알아보겠다. 👍😀


