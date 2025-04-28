import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
import re
import os
import unicodedata
from collections import defaultdict

# 환경변수에서 OC 불러오기
OC = os.getenv("OC", "chetera")
BASE = "http://www.law.go.kr"

# 법령목록 가져오기
def get_law_list_from_api(query):
    exact_query = f'"{query}"'
    encoded_query = quote(exact_query)
    page = 1
    laws = []
    while True:
        url = f"{BASE}/DRF/lawSearch.do?OC={OC}&target=law&type=XML&display=100&page={page}&search=2&knd=A0002&query={encoded_query}"
        res = requests.get(url, timeout=10)
        res.encoding = 'utf-8'
        if res.status_code != 200:
            break
        root = ET.fromstring(res.content)
        law_elements = root.findall("law")
        if not law_elements:
            break
        for law_elem in law_elements:
            law_name = law_elem.findtext("법령명한글")
            mst = law_elem.findtext("법령일련번호")
            link = law_elem.findtext("법령상세링크")
            laws.append({
                "법령명": law_name,
                "법령일련번호": mst,
                "법령상세링크": link
            })
        page += 1
    return laws

# 법령 본문 가져오기
def get_law_content(mst):
    url = f"{BASE}/DRF/lawService.do?OC={OC}&target=law&type=XML&mst={mst}"
    res = requests.get(url, timeout=10)
    res.encoding = 'utf-8'
    if res.status_code != 200:
        return None
    return ET.fromstring(res.content)

# 검색어 포함 조문 탐색
def find_articles_with_query(root, query):
    results = []
    for jo in root.findall(".//조문"):
        jo_title = jo.findtext("조문제목") or ""
        jo_text = jo.findtext("조문내용") or ""

        matches = []

        if query in jo_title or query in jo_text:
            matches.append(jo_title + " " + jo_text)

        for hang in jo.findall(".//항"):
            hang_text = hang.findtext("항내용") or ""
            if query in hang_text:
                matches.append(hang_text)
            for ho in hang.findall(".//호"):
                ho_text = ho.findtext("호내용") or ""
                if query in ho_text:
                    matches.append(ho_text)
                for mok in ho.findall(".//목"):
                    mok_text = mok.findtext("목내용") or ""
                    if query in mok_text:
                        matches.append(mok_text)

        if matches:
            results.append({
                "조문제목": jo_title,
                "조문내용": jo_text,
                "포함항목": matches
            })
    return results

# 개정문 생성
def generate_amendment(law_name, query, replace_word, articles):
    targets = []
    for article in articles:
        for content in article["포함항목"]:
            targets.append(content)
    if not targets:
        return ""

    unique_targets = list(set(targets))
    full_target_desc = ", ".join(unique_targets)

    amendment = f"{law_name} 중 \"{query}\"를 \"{replace_word}\"로 한다."
    return amendment
