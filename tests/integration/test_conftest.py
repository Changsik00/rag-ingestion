import pytest
import socket
from unittest.mock import patch, MagicMock

@pytest.mark.integration
def test_infrastructure_check_fixture(check_infrastructure):
    """
    check_infrastructure 픽스처가 정상적으로 동작하는지 검증합니다.
    주의: 이 테스트는 check_infrastructure 픽스처가 구현된 후에만 통과해야 합니다.
    지금은 TDD 단계이므로 픽스처가 없어서 실패(FixtureLookupError)하거나,
    구현 후에는 실제 포트가 열려있으므로 통과해야 합니다.
    """
    assert check_infrastructure is True
