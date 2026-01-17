"""
Contract tests for Scraper interface implementations.
"""
import pytest
from app.domain.interfaces.scraper import ScraperInterface
from app.infrastructure.scrapers.basic import BasicWebScraper


@pytest.fixture(params=[
    BasicWebScraper,
])
def scraper_class(request):
    """All ScraperInterface implementation classes"""
    return request.param



class TestScraperContract:
    """Contract tests for Scraper interface"""

    def test_has_scrape_method(self, scraper_class):
        """All scraper classes must have a scrape method"""
        assert hasattr(scraper_class, 'scrape')
        assert callable(getattr(scraper_class, 'scrape'))

    def test_scrape_method_signature(self, scraper_class):
        """scrape method should accept url parameter"""
        import inspect
        
        sig = inspect.signature(scraper_class.scrape)
        params = list(sig.parameters.values())
        
        # Should have 'self' and 'url' parameters
        assert len(params) == 2, f"{scraper_class.__name__}.scrape should have 2 parameters (self, url)"
        
        param_names = [p.name for p in params]
        assert 'self' in param_names
        assert 'url' in param_names


class TestScraperConstructorConsistency:
    """Tests to verify constructor consistency across Scraper implementations"""

    def test_basic_web_scraper_constructor(self):
        """BasicWebScraper should initialize without parameters"""
        scraper = BasicWebScraper()
        
        # BasicWebScraper initializes successfully
        assert scraper is not None

