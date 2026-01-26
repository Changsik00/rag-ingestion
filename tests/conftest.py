import pytest
import os

def pytest_addoption(parser):
    parser.addoption(
        "--run-expensive", action="store_true", default=False, help="run expensive tests (e.g. Firecrawl)"
    )

def pytest_configure(config):
    config.addinivalue_line("markers", "expensive: mark test as expensive to run")

def pytest_collection_modifyitems(config, items):
    # Check for both CLI flag and environment variable
    run_expensive = config.getoption("--run-expensive") or os.getenv("RUN_EXPENSIVE_TESTS") == "true"
    
    if run_expensive:
        return
    
    skip_expensive = pytest.mark.skip(reason="expensive test (use --run-expensive or RUN_EXPENSIVE_TESTS=true to run)")
    for item in items:
        if "expensive" in item.keywords:
            item.add_marker(skip_expensive)
