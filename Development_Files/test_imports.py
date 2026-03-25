#!/usr/bin/env python3
"""
Final import test for Guide.Analyst v2.0 implementation
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test all critical imports and functionality"""
    print("🔍 Testing imports...")
    
    # Test core modules
    try:
        from core.datadragon import dd_service
        print("✅ dd_service imported")
    except Exception as e:
        print(f"❌ dd_service import failed: {e}")
        return False
    
    try:
        from core.riot_api import get_role_icon_url
        print("✅ get_role_icon_url imported")
    except Exception as e:
        print(f"❌ get_role_icon_url import failed: {e}")
        return False
    
    # Test view modules
    try:
        from views.team_builder import build_team_builder, _analyze_synergy, CHAMPION_POOL
        print("✅ team_builder imported")
    except Exception as e:
        print(f"❌ team_builder import failed: {e}")
        return False
    
    try:
        from views.agentic_console import build_agentic_console
        print("✅ agentic_console imported")
    except Exception as e:
        print(f"❌ agentic_console import failed: {e}")
        return False
    
    try:
        from views.summoner_search import build_summoner_search
        print("✅ summoner_search imported")
    except Exception as e:
        print(f"❌ summoner_search import failed: {e}")
        return False
    
    try:
        from views.analytics import build_analytics
        print("✅ analytics imported")
    except Exception as e:
        print(f"❌ analytics import failed: {e}")
        return False
    
    try:
        from views.pro_players import build_pro_players, _player_hover
        print("✅ pro_players imported")
    except Exception as e:
        print(f"❌ pro_players import failed: {e}")
        return False
    
    # Test functionality
    print("\n🧪 Testing functionality...")
    
    try:
        # Test synergy engine
        r = _analyze_synergy({'Top':'Malphite','Jungle':'Vi','Mid':'Orianna','Bot':'Jinx','Support':'Lulu'})
        assert r['pct'] > 70, f'Synergy score troppo basso: {r["pct"]}'
        print("✅ Synergy engine working")
    except Exception as e:
        print(f"❌ Synergy engine failed: {e}")
        return False
    
    try:
        # Test champion pool
        assert len(CHAMPION_POOL) > 100, 'Pool campioni insufficiente'
        print("✅ Champion pool sufficient")
    except Exception as e:
        print(f"❌ Champion pool failed: {e}")
        return False
    
    try:
        # Test role icon URL
        url = dd_service.get_role_icon_url('Mid')
        assert 'Middle' in url, f'URL ruolo Mid errato: {url}'
        url = dd_service.get_role_icon_url('Bot')
        assert 'Bottom' in url, f'URL ruolo Bot errato: {url}'
        print("✅ Role icon URLs working")
    except Exception as e:
        print(f"❌ Role icon URLs failed: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
