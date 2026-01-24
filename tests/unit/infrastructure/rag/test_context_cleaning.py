import re
from app.infrastructure.rag.nodes import RAGNodes

def test_clean_context_noise_removes_wiki_templates():
    nodes = RAGNodes(None, None, None, None, None, None)
    
    # Wiki Table and Template
    raw_text = """{| class="wikitable"
|-
! Header
|}
Some content {{Template}}
More content [[파일:image.jpg]]
"""
    cleaned = nodes._clean_context_noise(raw_text)
    
    assert "wikitable" not in cleaned
    assert "Template" not in cleaned
    assert "파일:image.jpg" not in cleaned
    assert "Some content" in cleaned
    assert "More content" in cleaned

def test_clean_context_noise_removes_excessive_newlines():
    nodes = RAGNodes(None, None, None, None, None, None)
    text = "Line 1\n\n\n\nLine 2"
    cleaned = nodes._clean_context_noise(text)
    assert cleaned == "Line 1\n\nLine 2"
