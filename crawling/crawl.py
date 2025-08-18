####공지사항 크롤링하는 코드 ################
def get_latest_wr_id():
    url = "https://cse.knu.ac.kr/bbs/board.php?bo_table=sub5_1"
    response = requests.get(url)
    if response.status_code == 200:
        match = re.search(r'wr_id=(\d+)', response.text)
        if match:
            return int(match.group(1))
    return None


# 최신 wr_id를 가져와서 스크래핑할 URL 목록 생성
now_number = get_latest_wr_id()
base_url = "https://cse.knu.ac.kr/bbs/board.php?bo_table=sub5_1&wr_id="

# 기본 URL 목록 생성
urls = [f"{base_url}{number}" for number in range(now_number, 27726, -1)]

# 추가로 필요한 URL 목록
add_urls = [
    27510, 27047, 27614, 27246, 25900,
    27553, 25896, 25817, 25560, 27445,25804
]

# 추가 URL을 `urls` 리스트에 확장
urls.extend(f"{base_url}{wr_id}" for wr_id in add_urls)

# URL에서 제목, 날짜, 내용(본문 텍스트와 이미지 URL) 추출하는 공지사항 함수
def extract_text_and_date_from_url(urls):
    all_data = []

    def fetch_text_and_date(url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 제목 추출
            title_element = soup.find('span', class_='bo_v_tit')
            title = title_element.get_text(strip=True) if title_element else "Unknown Title"

            # 본문 텍스트와 이미지 URL을 분리하여 저장
            text_content = "Unknown Content"  # 텍스트 초기화
            image_content = []  # 이미지 URL을 담는 리스트 초기화

            # 본문 내용 추출
            paragraphs = soup.find('div', id='bo_v_con')
            if paragraphs:
                # paragraphs 내부에서 'p', 'div', 'li' 태그 텍스트 추출
                text_content = "\n".join([element.get_text(strip=True) for element in paragraphs.find_all(['p', 'div', 'li'])])
                #print(text_content)
                if text_content.strip() == "":
                    text_content = ""
                # 이미지 URL 추출
                for img in paragraphs.find_all('img'):
                    img_src = img.get('src')
                    if img_src:
                        image_content.append(img_src)

            # 날짜 추출
            date_element = soup.select_one("strong.if_date")  # 수정된 선택자
            date = date_element.get_text(strip=True) if date_element else "Unknown Date"

            # 제목이 Unknown Title이 아닐 때만 데이터 추가
            if title != "Unknown Title":
                return title, text_content, image_content, date, url  # 문서 제목, 본문 텍스트, 이미지 URL 리스트, 날짜, URL 반환
            else:
                return None, None, None, None, None  # 제목이 Unknown일 경우 None 반환
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return None, None, None, None, url

    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_text_and_date, urls)

    # 유효한 데이터만 추가
    all_data = [(title, text_content, image_content, date, url) for title, text_content, image_content, date, url in results if title is not None]
    return all_data

#### 크롤링한 공지사항 정보 document_data에 저장
document_data = extract_text_and_date_from_url(urls)
################################################################################################

# 텍스트 분리기 초기화
class CharacterTextSplitter:
    def __init__(self, chunk_size=850, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text):
        chunks = []
        if len(text) <= self.chunk_size:
            return [text]

        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk:
                chunks.append(chunk)
        return chunks

text_splitter = CharacterTextSplitter(chunk_size=850, chunk_overlap=100)

################################################################################################

# 텍스트 분리 및 URL과 날짜 매핑
texts = []
image_url=[]
titles = []
doc_urls = []
doc_dates = []
for title, doc, image, date, url in document_data:
    if isinstance(doc, str) and doc.strip():  # doc가 문자열인지 확인하고 비어있지 않은지 확인
        split_texts = text_splitter.split_text(doc)
        texts.extend(split_texts)
        titles.extend([title] * len(split_texts))  # 제목을 분리된 텍스트와 동일한 길이로 추가
        doc_urls.extend([url] * len(split_texts))
        doc_dates.extend([date] * len(split_texts))  # 분리된 각 텍스트에 동일한 날짜 적용

        # 이미지 URL도 저장
        if image:  # 이미지 URL이 비어 있지 않은 경우
            image_url.extend([image] * len(split_texts))  # 동일한 길이로 이미지 URL 추가
        else:  # 이미지 URL이 비어 있는 경우
            image_url.extend(["No content"] * len(split_texts))  # "No content" 추가

    elif image:  # doc가 비어 있고 이미지가 있는 경우
        # 텍스트는 "No content"로 추가
        texts.append("No content")
        titles.append(title)
        doc_urls.append(url)
        doc_dates.append(date)
        image_url.append(image)  # 이미지 URL 추가

    else:  # doc와 image가 모두 비어 있는 경우
        texts.append("No content")
        image_url.append("No content")  # 이미지도 "No content"로 추가
        titles.append(title)
        doc_urls.append(url)
        doc_dates.append(date)



######################################################################################################
########################### 지금까지 공지사항 정보 ###################################################
######################################################################################################


######   정교수진의 정보 받아오는 코드 ##########

def extract_professor_info_from_urls(urls):
    all_data = []

    def fetch_professor_info(url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # 교수 정보가 담긴 요소들 선택
            professor_elements = soup.find("div", id="dr").find_all("li")

            for professor in professor_elements:
                # 이미지 URL 추출
                image_element = professor.find("div", class_="dr_img").find("img")
                image_content = image_element["src"] if image_element else "Unknown Image URL"

                # 이름 추출
                name_element = professor.find("div", class_="dr_txt").find("h3")
                title = name_element.get_text(strip=True) if name_element else "Unknown Name"

                # 연락처와 이메일 추출 후 하나의 텍스트로 결합
                contact_info = professor.find("div", class_="dr_txt").find_all("dd")
                contact_number = contact_info[0].get_text(strip=True) if len(contact_info) > 0 else "Unknown Contact Number"
                email = contact_info[1].get_text(strip=True) if len(contact_info) > 1 else "Unknown Email"
                text_content = f"{title}, {contact_number}, {email}"

                # 날짜와 URL 설정
                date = "작성일24-01-01 00:00"

                prof_url_element = professor.find("a")
                prof_url = prof_url_element["href"] if prof_url_element else "Unknown URL"

                # 각 교수의 정보를 all_data에 추가
                all_data.append((title, text_content, image_content, date, prof_url))

        except Exception as e:
            print(f"Error processing {url}: {e}")

    # ThreadPoolExecutor를 이용하여 병렬 크롤링
    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_professor_info, urls)

    return all_data


######   초빙교수진의 정보 받아오는 코드 ##########

def extract_professor_info_from_urls_2(urls):
    all_data = []

    def fetch_professor_info(url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # 교수 정보가 담긴 요소들 선택
            professor_elements = soup.find("div", id="Student").find_all("li")

            for professor in professor_elements:
                # 이미지 URL 추출
                image_element = professor.find("div", class_="img").find("img")
                image_content = image_element["src"] if image_element else "Unknown Image URL"

                # 이름 추출
                name_element = professor.find("div", class_="cnt").find("div", class_="name")
                title = name_element.get_text(strip=True) if name_element else "Unknown Name"

                # 연락처와 이메일 추출
                contact_place = professor.find("div", class_="dep").get_text(strip=True) if professor.find("div", class_="dep") else "Unknown Contact Place"
                email_element = professor.find("dl", class_="email").find("dd").find("a")
                email = email_element.get_text(strip=True) if email_element else "Unknown Email"

                # 텍스트 내용 조합
                text_content = f"성함(이름):{title}, 연구실(장소):{contact_place}, 이메일:{email}"

                # 날짜와 URL 설정
                date = "작성일24-01-01 00:00"
                prof_url = url

                # 각 교수의 정보를 all_data에 추가
                all_data.append((title, text_content, image_content, date, prof_url))

        except Exception as e:
            print(f"Error processing {url}: {e}")

    # ThreadPoolExecutor를 이용하여 병렬 크롤링
    with ThreadPoolExecutor() as executor:
        executor.map(fetch_professor_info, urls)

    return all_data

######   직원의 정보 받아오는 코드 ##########

def extract_professor_info_from_urls_3(urls):
    all_data = []

    def fetch_professor_info(url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # 교수 정보가 담긴 요소들 선택
            professor_elements = soup.find("div", id="Student").find_all("li")

            for professor in professor_elements:
                # 이미지 URL 추출
                image_element = professor.find("div", class_="img").find("img")
                image_content = image_element["src"] if image_element else "Unknown Image URL"

                # 이름 추출
                name_element = professor.find("div", class_="cnt").find("h1")
                title = name_element.get_text(strip=True) if name_element else "Unknown Name"

                # 연락처 추출
                contact_number_element = professor.find("span", class_="period")
                contact_number = contact_number_element.get_text(strip=True) if contact_number_element else "Unknown Contact Number"

                # 연구실 위치 추출
                contact_info = professor.find_all("dl", class_="dep")
                contact_place = contact_info[0].find("dd").get_text(strip=True) if len(contact_info) > 0 else "Unknown Contact Place"

                # 이메일 추출
                email = contact_info[1].find("dd").find("a").get_text(strip=True) if len(contact_info) > 1 else "Unknown Email"

                # 담당 업무 추출
                role = contact_info[2].find("dd").get_text(strip=True) if len(contact_info) > 2 else "Unknown Role"

                # 텍스트 내용 조합
                text_content = f"성함(이름):{title}, 연락처(전화번호):{contact_number}, 사무실(장소):{contact_place}, 이메일:{email}, 담당업무:{role}"

                # 날짜와 URL 설정
                date = "작성일24-01-01 00:00"
                prof_url = url

                # 각 교수의 정보를 all_data에 추가
                all_data.append((title, text_content, image_content, date, prof_url))

        except Exception as e:
            print(f"Error processing {url}: {e}")

    # ThreadPoolExecutor를 이용하여 병렬 크롤링
    with ThreadPoolExecutor() as executor:
        executor.map(fetch_professor_info, urls)

    return all_data



# 교수진 페이지 URL 목록
urls2 = [
    "https://cse.knu.ac.kr/bbs/board.php?bo_table=sub2_1&lang=kor",
]

urls3 = [
    "https://cse.knu.ac.kr/bbs/board.php?bo_table=sub2_2&lang=kor",
]

urls4 = [
    "https://cse.knu.ac.kr/bbs/board.php?bo_table=sub2_5&lang=kor",
]


# URL에서 문서와 날짜 추출

prof_data = extract_professor_info_from_urls(urls2)
prof_data_2 = extract_professor_info_from_urls_2(urls3)
prof_data_3 = extract_professor_info_from_urls_3(urls4)



combined_prof_data = prof_data + prof_data_2 + prof_data_3



# 교수 정보 크롤링 데이터 분리 및 저장
professor_texts = []
professor_image_urls = []
professor_titles = []
professor_doc_urls = []
professor_doc_dates = []

# prof_data는 extract_professor_info_from_urls 함수의 반환값
for title, doc, image, date, url in combined_prof_data :
    if isinstance(doc, str) and doc.strip():  # 교수 정보가 문자열로 있고 비어있지 않을 때
        split_texts = text_splitter.split_text(doc)
        professor_texts.extend(split_texts)
        professor_titles.extend([title] * len(split_texts))  # 교수 이름을 분리된 텍스트와 동일한 길이로 추가
        professor_doc_urls.extend([url] * len(split_texts))
        professor_doc_dates.extend([date] * len(split_texts))  # 분리된 각 텍스트에 동일한 날짜 적용

        # 이미지 URL도 저장
        if image:  # 이미지 URL이 비어 있지 않은 경우
            professor_image_urls.extend([image] * len(split_texts))  # 동일한 길이로 이미지 URL 추가
        else:
            professor_image_urls.extend(["No content"] * len(split_texts))  # "No content" 추가

    elif image:  # doc가 비어 있고 이미지가 있는 경우
        professor_texts.append("No content")
        professor_titles.append(title)
        professor_doc_urls.append(url)
        professor_doc_dates.append(date)
        professor_image_urls.append(image)  # 이미지 URL 추가

    else:  # doc와 image가 모두 비어 있는 경우
        professor_texts.append("No content")
        professor_image_urls.append("No content")  # 이미지도 "No content"로 추가
        professor_titles.append(title)
        professor_doc_urls.append(url)
        professor_doc_dates.append(date)

# 교수 정보 데이터를 기존 데이터와 합치기
texts.extend(professor_texts)
image_url.extend(professor_image_urls)
titles.extend(professor_titles)
doc_urls.extend(professor_doc_urls)
doc_dates.extend(professor_doc_dates)


######################################################################################################
###########################교수 및 직원정보임 위는  ##################################################
######################################################################################################



####### 취업정보를 받아오는 코드 #######

def get_latest_wr_id_1():
    url = "https://cse.knu.ac.kr/bbs/board.php?bo_table=sub5_3_b"
    response = requests.get(url)
    if response.status_code == 200:
        # re.findall을 사용하여 모든 wr_id 값을 찾아 리스트로 반환
        match = re.findall(r'wr_id=(\d+)', response.text)
        if match:
        # wr_ids 리스트에 있는 모든 wr_id 값을 출력
          max_wr_id = max(int(wr_id) for wr_id in match)
          return max_wr_id
    return None


now_company_number=get_latest_wr_id_1()

company_urls=[]
for number in range(now_company_number,1149,-1):
  company_urls.append("https://cse.knu.ac.kr/bbs/board.php?bo_table=sub5_3_b&wr_id="+str(number))


def extract_company_from_url(urls):
    all_data = []

    def fetch_text_and_date(url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 제목 추출
            title_element = soup.find('span', class_='bo_v_tit')
            title = title_element.get_text(strip=True) if title_element else "Unknown Title"

            # 본문 텍스트와 이미지 URL을 분리하여 저장
            text_content = "Unknown Content"  # 텍스트 초기화
            image_content = []  # 이미지 URL을 담는 리스트 초기화

            # 본문 내용 추출
            paragraphs = soup.find('div', id='bo_v_con')
            if paragraphs:
                # paragraphs 내부에서 'p', 'div', 'li' 태그 텍스트 추출
                text_content = "\n".join([element.get_text(strip=True) for element in paragraphs.find_all(['p', 'div', 'li'])])
                #print(text_content)
                if text_content.strip() == "":
                    text_content = ""
                # 이미지 URL 추출
                for img in paragraphs.find_all('img'):
                    img_src = img.get('src')
                    if img_src:
                        image_content.append(img_src)

            # 날짜 추출
            date_element = soup.select_one("strong.if_date")  # 수정된 선택자
            date = date_element.get_text(strip=True) if date_element else "Unknown Date"

            # 제목이 Unknown Title이 아닐 때만 데이터 추가
            if title != "Unknown Title":
                return title, text_content, image_content, date, url  # 문서 제목, 본문 텍스트, 이미지 URL 리스트, 날짜, URL 반환
            else:
                return None, None, None, None, None  # 제목이 Unknown일 경우 None 반환
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return None, None, None, None, url

    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_text_and_date, urls)

    # 유효한 데이터만 추가
    all_data = [(title, text_content, image_content, date, url) for title, text_content, image_content, date, url in results if title is not None]
    return all_data

company_data= extract_company_from_url(company_urls)



for title, doc, image, date, url in company_data:
    if isinstance(doc, str) and doc.strip():  # doc가 문자열인지 확인하고 비어있지 않은지 확인
        split_texts = text_splitter.split_text(doc)
        texts.extend(split_texts)
        titles.extend([title] * len(split_texts))  # 제목을 분리된 텍스트와 동일한 길이로 추가
        doc_urls.extend([url] * len(split_texts))
        doc_dates.extend([date] * len(split_texts))  # 분리된 각 텍스트에 동일한 날짜 적용

        # 이미지 URL도 저장
        if image:  # 이미지 URL이 비어 있지 않은 경우
            image_url.extend([image] * len(split_texts))  # 동일한 길이로 이미지 URL 추가
        else:  # 이미지 URL이 비어 있는 경우
            image_url.extend(["No content"] * len(split_texts))  # "No content" 추가

    elif image:  # doc가 비어 있고 이미지가 있는 경우
        # 텍스트는 "No content"로 추가
        texts.append("No content")
        titles.append(title)
        doc_urls.append(url)
        doc_dates.append(date)
        image_url.append(image)  # 이미지 URL 추가

    else:  # doc와 image가 모두 비어 있는 경우
        texts.append("No content")
        image_url.append("No content")  # 이미지도 "No content"로 추가
        titles.append(title)
        doc_urls.append(url)
        doc_dates.append(date)



######################################################################################################
###########################취업정보임 위는  ##########################################################
######################################################################################################



def get_latest_wr_id_2():
    url = "https://cse.knu.ac.kr/bbs/board.php?bo_table=sub5_4"
    response = requests.get(url)
    if response.status_code == 200:
        # re.findall을 사용하여 모든 wr_id 값을 찾아 리스트로 반환
        match = re.findall(r'wr_id=(\d+)', response.text)
        if match:
        # wr_ids 리스트에 있는 모든 wr_id 값을 출력
          max_wr_id = max(int(wr_id) for wr_id in match)
          return max_wr_id
    return None


now_seminar_number=get_latest_wr_id_2()

seminar_urls=[]
for number in range(now_seminar_number,246,-1):
  seminar_urls.append("https://cse.knu.ac.kr/bbs/board.php?bo_table=sub5_4&wr_id="+str(number))


def extract_seminar_from_url(urls):
    all_data = []

    def fetch_text_and_date(url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 제목 추출
            title_element = soup.find('span', class_='bo_v_tit')
            title = title_element.get_text(strip=True) if title_element else "Unknown Title"

            # 본문 텍스트와 이미지 URL을 분리하여 저장
            text_content = "Unknown Content"  # 텍스트 초기화
            image_content = []  # 이미지 URL을 담는 리스트 초기화

            # 본문 내용 추출
            paragraphs = soup.find('div', id='bo_v_con')
            if paragraphs:
                # paragraphs 내부에서 'p', 'div', 'li' 태그 텍스트 추출
                text_content = "\n".join([element.get_text(strip=True) for element in paragraphs.find_all(['p', 'div', 'li'])])
                #print(text_content)
                if text_content.strip() == "":
                    text_content = ""
                # 이미지 URL 추출
                for img in paragraphs.find_all('img'):
                    img_src = img.get('src')
                    if img_src:
                        image_content.append(img_src)

            # 날짜 추출
            date_element = soup.select_one("strong.if_date")  # 수정된 선택자
            date = date_element.get_text(strip=True) if date_element else "Unknown Date"

            # 제목이 Unknown Title이 아닐 때만 데이터 추가
            if title != "Unknown Title":
                return title, text_content, image_content, date, url  # 문서 제목, 본문 텍스트, 이미지 URL 리스트, 날짜, URL 반환
            else:
                return None, None, None, None, None  # 제목이 Unknown일 경우 None 반환
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return None, None, None, None, url

    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_text_and_date, urls)

    # 유효한 데이터만 추가
    all_data = [(title, text_content, image_content, date, url) for title, text_content, image_content, date, url in results if title is not None]
    return all_data

seminar_data= extract_seminar_from_url(seminar_urls)



for title, doc, image, date, url in seminar_data:
    if isinstance(doc, str) and doc.strip():  # doc가 문자열인지 확인하고 비어있지 않은지 확인
        split_texts = text_splitter.split_text(doc)
        texts.extend(split_texts)
        titles.extend([title] * len(split_texts))  # 제목을 분리된 텍스트와 동일한 길이로 추가
        doc_urls.extend([url] * len(split_texts))
        doc_dates.extend([date] * len(split_texts))  # 분리된 각 텍스트에 동일한 날짜 적용

        # 이미지 URL도 저장
        if image:  # 이미지 URL이 비어 있지 않은 경우
            image_url.extend([image] * len(split_texts))  # 동일한 길이로 이미지 URL 추가
        else:  # 이미지 URL이 비어 있는 경우
            image_url.extend(["No content"] * len(split_texts))  # "No content" 추가

    elif image:  # doc가 비어 있고 이미지가 있는 경우
        # 텍스트는 "No content"로 추가
        texts.append("No content")
        titles.append(title)
        doc_urls.append(url)
        doc_dates.append(date)
        image_url.append(image)  # 이미지 URL 추가

    else:  # doc와 image가 모두 비어 있는 경우
        texts.append("No content")
        image_url.append("No content")  # 이미지도 "No content"로 추가
        titles.append(title)
        doc_urls.append(url)
        doc_dates.append(date)



######################################################################################################
############################세미나임 위는  ##########################################################
######################################################################################################
