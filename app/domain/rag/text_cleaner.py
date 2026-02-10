import re

def clean_context_noise(text: str) -> str:
    """
    [Spec 037] RAG 컨텍스트 노이즈 제거.
    Wikipedia Navbox, Infobox, 파일 링크 등 답변 생성에 방해되는 요소를 제거합니다.
    """
    if not text:
        return ""

    # 1. Wikipedia Infobox (Keep content for role/title/etc.)
    # We remove generic templates but try to preserve Infobox data by hiding the wrapper but keeping internal lines
    # Or more simply, avoid greedy match for just anything {{...}}.
    # Here we ignore Navbox and Cite but keep Infobox.
    pattern_wiki_table = r"\{\|.*?\|\}"
    text = re.sub(pattern_wiki_table, "", text, flags=re.DOTALL)  # Wiki Tables

    # Remove Navbox, Cite, and other noise templates, but EXEMPT Infobox
    # Using a lookahead to avoid matching {{Infobox
    pattern_templates = r"\{\{(?!(?:Infobox|정보상자)).*?\}\}"
    text = re.sub(pattern_templates, "", text, flags=re.DOTALL)

    # 2. Wikipedia File/Image links
    text = re.sub(r"\[\[파일:.*?\]\]", "", text)
    text = re.sub(r"\[\[File:.*?\]\]", "", text)

    # 3. Excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 4. Empty markdown tables (e.g. | | |)
    text = re.sub(r"\|[\s\|-]+\|\n", "", text)

    return text.strip()
