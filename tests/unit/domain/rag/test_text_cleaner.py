from app.domain.rag.text_cleaner import clean_context_noise


def test_clean_context_noise_removes_wiki_templates():
    raw_text = """Some content {{Infobox | role = CEO}}
    More content {{Navbox | topic = Tech}}
    Even more [[파일:image.jpg]]
    """
    cleaned = clean_context_noise(raw_text)

    # Infobox is kept (inner content) but wrapper removed?
    # Logic in clean_context_noise:
    # text = re.sub(r"\{\{(?!(?:Infobox|정보상자)).*?\}\}", "", text, flags=re.DOTALL)
    # This removes templates that are NOT Infobox.
    # So Infobox should remain AS IS.

    assert "Infobox" in cleaned
    assert "CEO" in cleaned
    assert "Navbox" not in cleaned
    assert "파일:image.jpg" not in cleaned
    assert "Some content" in cleaned


def test_clean_context_noise_removes_excessive_newlines():
    text = "Line 1\n\n\n\nLine 2"
    cleaned = clean_context_noise(text)
    assert cleaned == "Line 1\n\nLine 2"
