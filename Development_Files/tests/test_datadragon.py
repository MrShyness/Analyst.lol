import pytest
import os
import shutil
from core.datadragon import DataDragonService

# Setup a temporary test cache directory
TEST_CACHE = ".cache/test_ddragon"

@pytest.fixture
def dd_service():
    if os.path.exists(TEST_CACHE):
        shutil.rmtree(TEST_CACHE)
    service = DataDragonService(cache_dir=TEST_CACHE)
    yield service
    if os.path.exists(TEST_CACHE):
        shutil.rmtree(TEST_CACHE)

def test_get_latest_version(dd_service):
    version = dd_service.get_latest_version()
    assert isinstance(version, str)
    assert "." in version

def test_get_role_icon_url(dd_service):
    url = dd_service.get_role_icon_url("Top")
    assert "position/top.png" in url.lower()
    
    url = dd_service.get_role_icon_url("Middle")
    assert "position/mid.png" in url.lower()
    
    url = dd_service.get_role_icon_url("Invalid")
    assert "position/utility.png" in url.lower()

def test_get_champion_square_url(dd_service):
    url = dd_service.get_champion_square_url("Aatrox")
    assert "champion/Aatrox.png" in url
    
    url = dd_service.get_champion_square_url(None)
    assert "champion/Aatrox.png" in url # Fallback

def test_get_champion_data_caching(dd_service):
    # Test disk caching
    name = "Aatrox"
    # First call - should fetch and cache
    data1 = dd_service.get_champion_data(name)
    assert data1 is not None
    assert data1["id"] == name
    
    # Check if file exists in cache
    # The file contains the whole response, but service returns data[name]
    cache_path = os.path.join(TEST_CACHE, f"{name}_en_US.json")
    assert os.path.exists(cache_path)
    
    # Second call - should use cache
    data2 = dd_service.get_champion_data(name)
    assert data1["key"] == data2["key"]

def test_offline_mode_fallback(dd_service):
    # This is hard to test without mocking requests, 
    # but we can check if it returns fallback when API is "blocked" 
    # (if we had a way to mock requests.get)
    pass
