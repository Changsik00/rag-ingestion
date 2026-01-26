import pytest
from app.infrastructure.scrapers.cleaner import MarkdownCleaner

@pytest.fixture
def cleaner():
    return MarkdownCleaner()

def test_remove_wiki_footnotes(cleaner):
    """나무위키/위키피디아의 각주([1], [2]) 제거 테스트"""
    text = "이것은 예시 문장입니다.[1] 각주가 뒤에 붙어있죠.[10][23]"
    expected = "이것은 예시 문장입니다. 각주가 뒤에 붙어있죠."
    assert cleaner.clean(text) == expected

def test_remove_wiki_edit_buttons(cleaner):
    """본문 내 [편집], [삭제] 버튼 텍스트 제거 테스트"""
    text = "섹션 제목[편집]\n이곳의 내용을 삭제[삭제]할 수 있습니다."
    expected = "섹션 제목\n이곳의 내용을 삭제할 수 있습니다."
    assert cleaner.clean(text) == expected

def test_remove_wiki_syntax_fragments(cleaner):
    """[[내용]] 같은 위키 문법 파편 제거 테스트"""
    text = "[[파일:example.jpg|썸네일]] 본문 내용입니다. [[링크|설명]]"
    # 단순 텍스트 추출 시 남을 수 있는 껍데기 제거
    # 여기서는 [[ ]] 패턴 자체를 날리거나 적절히 처리함
    cleaned = cleaner.clean(text)
    assert "[[" not in cleaned
    assert "]]" not in cleaned

def test_remove_empty_links(cleaner):
    """비어있는 마크다운 링크 []() 제거 테스트"""
    text = "정상 링크 [Google](https://google.com)와 빈 링크 []()가 섞여있음"
    expected = "정상 링크 [Google](https://google.com)와 빈 링크 가 섞여있음"
    assert cleaner.clean(text) == expected

def test_remove_navboxes_and_empty_tables(cleaner):
    """네비게이션 박스나 빈 표 제거 테스트"""
    text = """
# 본문 제목
| | |
|---|---|
| | |

여기는 실제 본문입니다.
    """
    cleaned = cleaner.clean(text)
    assert "|---|---|" not in cleaned
    assert "여기는 실제 본문입니다." in cleaned

def test_remove_repeated_special_chars(cleaner):
    """의미 없는 특수문자 반복 제거 테스트"""
    text = "중요한 내용!!!!!!!!! *********** ##########"
    cleaned = cleaner.clean(text)
    # 반복 횟수를 줄이거나 제거
    assert "!!!!" not in cleaned
    assert "****" not in cleaned

def test_remove_invisible_chars(cleaner):
    """비가시 제어 문자 제거 테스트"""
    text = "본문\u200b내용\u200c입니다."
    expected = "본문내용입니다."
    assert cleaner.clean(text) == expected

def test_comprehensive_clean(cleaner):
    """복합적인 오염 물질 제거 테스트 (나무위키 스타일)"""
    text = """
== 개요 ==[편집]
나무위키의 문서 구조입니다.[1]
[[파일:tree.png]]
| | |
|---|---|
이런 표는 필요 없습니다.
!@#$%^&*()
끝.[2]
    """
    cleaned = cleaner.clean(text)
    assert "[편집]" not in cleaned
    assert "[1]" not in cleaned
    assert "[2]" not in cleaned
    assert "[[파일" not in cleaned
    assert "|---|---|" not in cleaned
    assert "나무위키의 문서 구조입니다." in cleaned
