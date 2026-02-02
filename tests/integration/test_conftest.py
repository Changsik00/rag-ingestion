import pytest
from unittest.mock import MagicMock, patch

@pytest.mark.integration
def test_infrastructure_check_fixture(check_infrastructure):
    """
    check_infrastructure 픽스처가 True를 반환하는지 확인합니다.
    실제 인프라가 켜져 있다면 Pass, 꺼져 있다면 Skip 됩니다.
    """
    assert check_infrastructure is True

@pytest.mark.integration
def test_seed_test_data_fixture(seed_test_data):
    """
    seed_test_data 픽스처가 딕셔너리를 반환하는지 확인합니다.
    """
    assert isinstance(seed_test_data, dict)
