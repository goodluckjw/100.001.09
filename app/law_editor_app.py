import streamlit as st
from law_processor import get_law_list_from_api, get_law_content, find_articles_with_query, generate_amendment

st.set_page_config(page_title="📘 부칙 개정 도우미 100.001.09", page_icon="📘", layout="centered")

st.title("📘 부칙 개정 도우미 (100.001.09 버전)")

search_word = st.text_input("🔍 찾을 단어", placeholder="예: 지방법원")
replace_word = st.text_input("📝 바꿀 단어", placeholder="예: 지역법원")

search_button = st.button("검색 시작")

if search_button and search_word and replace_word:
    with st.spinner("법령 검색 및 개정문 생성 중..."):
        laws = get_law_list_from_api(search_word)
        if not laws:
            st.warning("검색 결과가 없습니다.")
        else:
            st.success(f"{len(laws)}개의 법률을 찾았습니다.")
            for idx, law in enumerate(laws, 1):
                st.markdown(f"### {idx}. {law['법령명']}")
                root = get_law_content(law["법령일련번호"])
                if root is not None:
                    articles = find_articles_with_query(root, search_word)
                    for article in articles:
                        st.markdown("---")
                        for item in article["포함항목"]:
                            st.write(f"- {item}")
                    amendment = generate_amendment(law["법령명"], search_word, replace_word, articles)
                    if amendment:
                        st.info(amendment)
                else:
                    st.error("법령 본문을 불러오는 데 실패했습니다.")
