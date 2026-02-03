from app.domain.value_objects.chunk_config import ChunkingConfig, ChunkingStrategy
import pytest
from pydantic import ValidationError

def test_chunk_config_default_values():
    config = ChunkingConfig()
    assert config.strategy == ChunkingStrategy.RECURSIVE
    assert config.chunk_size == 1000
    assert config.chunk_overlap == 200
    assert config.breakpoint_threshold_type == "percentile"

def test_chunk_config_semantic_defaults():
    config = ChunkingConfig(strategy=ChunkingStrategy.SEMANTIC)
    assert config.strategy == ChunkingStrategy.SEMANTIC
    assert config.breakpoint_threshold_amount == 90.0

def test_chunk_config_validation_invalid_strategy():
    with pytest.raises(ValidationError):
        ChunkingConfig(strategy="invalid_strategy")

def test_chunk_config_validation_invalid_types():
    with pytest.raises(ValidationError):
        ChunkingConfig(chunk_size="not_an_int")
