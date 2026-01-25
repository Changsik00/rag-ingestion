import re
from app.infrastructure.rag.nodes import RAGNodes

def test_clean_context_noise_removes_wiki_templates():
    nodes = RAGNodes(None, None, None, None, None, None)
    
    raw_text = """Some content {{Infobox | role = CEO}}
    More content {{Navbox | topic = Tech}}
    Even more [[파일:image.jpg]]
    """
    cleaned = nodes._clean_context_noise(raw_text)
    
    assert "Infobox" in cleaned
    assert "CEO" in cleaned
    assert "Navbox" not in cleaned
    assert "파일:image.jpg" not in cleaned
    assert "Some content" in cleaned

def test_clean_context_noise_removes_excessive_newlines():
    nodes = RAGNodes(None, None, None, None, None, None)
    text = "Line 1\n\n\n\nLine 2"
    cleaned = nodes._clean_context_noise(text)
    assert cleaned == "Line 1\n\nLine 2"
