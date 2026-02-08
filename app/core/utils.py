import re


def normalize_entity_name(name: str) -> str:
    """
    엔티티 명칭 정규화:
    1. 공백 제거 (어쩌다 어른 -> 어쩌다어른)
    2. 소문자 변환
    3. 특수문자 제거 (일부 보존 가능)
    """
    if not name:
        return ""
    # 공백 제거 및 소문화
    normalized = re.sub(r"\s+", "", name).lower()
    return normalized


def get_canonical_name(name: str, aliases: list[str] = None) -> str:
    """
    별칭 목록이 있을 경우 가장 적절한 대표 명칭을 결정하거나
    정규화된 이름을 반환합니다.
    """
    return normalize_entity_name(name)
