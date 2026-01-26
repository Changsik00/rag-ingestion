import re


class MarkdownCleaner:
    def __init__(self):
        # 1. 나무위키/위키피디아 각주 ([1], [2], [10])
        self.footnote_pattern = re.compile(r"\[\d+\]")

        # 2. 위키 편집/삭제 버튼 ([편집], [삭제])
        self.button_pattern = re.compile(r"\[편집\]|\[삭제\]")

        # 3. 위키 문법 파편 ([ [내용] ], [ [파일:...] ])
        self.wiki_link_pattern = re.compile(r"\[\[.*?\]\]")

        # 4. 비어있는 마크다운 링크 ([]())
        self.empty_link_pattern = re.compile(r"\[\s*\]\(\s*\)")

        # 5. 비가시 제어 문자 (Zero-width spaces 등)
        self.invisible_char_pattern = re.compile(r"[\u200b\u200c\u200d\ufeff]")

        # 6. 의미 없는 특수문자 반복 (!!!, ***, ###) - 3회 이상 반복 시 단축
        self.repeat_punct_pattern = re.compile(r"([!?.#*])\1{2,}")

        # 7. 빈 표 (정보 없이 틀만 있는 경우)
        # 예: | | | \n |---|---| \n | | |
        self.empty_table_row = r"\|\s*(?:\s*\|\s*)*"
        self.table_separator = r"\|(?:\s*:?---*:?\s*\|)+"
        self.empty_table_pattern = re.compile(
            rf"^\s*{self.empty_table_row}\s*\n\s*{self.table_separator}\s*(?:\n\s*{self.empty_table_row}\s*)*",
            re.MULTILINE,
        )

    def clean(self, text: str) -> str:
        if not text:
            return ""

        # 각주 제거
        text = self.footnote_pattern.sub("", text)

        # 버튼 제거
        text = self.button_pattern.sub("", text)

        # 위키 문법 파편 제거
        text = self.wiki_link_pattern.sub("", text)

        # 비어있는 링크 제거
        text = self.empty_link_pattern.sub("", text)

        # 비가시 문자 제거
        text = self.invisible_char_pattern.sub("", text)

        # 특수문자 반복 단축
        text = self.repeat_punct_pattern.sub(r"\1", text)

        # 빈 표 제거
        text = self.empty_table_pattern.sub("", text)

        # 다중 공백 및 빈 줄 정리
        text = re.sub(r"\n\s*\n", "\n\n", text)
        text = re.sub(r" +", " ", text)

        return text.strip()
