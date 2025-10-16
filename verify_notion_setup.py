#!/usr/bin/env python3
"""
Verification script for Notion project type implementation.
Run this script to verify that the Notion project type is properly installed.
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported."""
    try:
        from projects_types.notion_type import NotionProjectType
        from projects_types import TYPE_REGISTRY
        print("✓ Imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_registration():
    """Test that NotionProjectType is registered."""
    try:
        from projects_types import TYPE_REGISTRY
        if "notion" in TYPE_REGISTRY:
            print("✓ Notion type registered in TYPE_REGISTRY")
            return True
        else:
            print("✗ Notion type not found in TYPE_REGISTRY")
            return False
    except Exception as e:
        print(f"✗ Registration test failed: {e}")
        return False


def test_configuration():
    """Test that configuration file exists."""
    config_path = Path("projects_types_configs/notion.yaml")
    if config_path.exists():
        print(f"✓ Configuration file exists: {config_path}")
        return True
    else:
        print(f"✗ Configuration file not found: {config_path}")
        return False


def test_templates():
    """Test that all required templates exist."""
    templates = [
        "templates/notion_list.html",
        "templates/notion_project.html",
        "templates/notion_page.html",
        "templates/notion_database.html",
    ]
    all_exist = True
    for template in templates:
        path = Path(template)
        if path.exists():
            print(f"✓ Template exists: {template}")
        else:
            print(f"✗ Template missing: {template}")
            all_exist = False
    return all_exist


def test_notion_type_functionality():
    """Test basic NotionProjectType functionality."""
    try:
        from flask import Flask
        from projects_types.notion_type import NotionProjectType
        
        app = Flask(__name__)
        config = {
            'type': 'notion',
            'identifier': 'notion',
            'projects_dir': 'projects/notion',
            'default_emoji': '📓'
        }
        
        notion_type = NotionProjectType(app, config)
        
        # Test required methods
        assert hasattr(notion_type, 'list_projects'), 'Missing list_projects method'
        assert hasattr(notion_type, 'register_routes'), 'Missing register_routes method'
        assert hasattr(notion_type, '_parse_csv_file'), 'Missing _parse_csv_file method'
        assert hasattr(notion_type, '_build_file_tree'), 'Missing _build_file_tree method'
        
        print("✓ NotionProjectType functionality tests passed")
        return True
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        return False


def test_app_integration():
    """Test that the app loads with Notion type."""
    try:
        from app import app, project_types
        
        if 'notion' in project_types:
            print("✓ Notion type loaded in application")
            return True
        else:
            print("✗ Notion type not loaded in application")
            return False
    except Exception as e:
        print(f"✗ App integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Notion Project Type Verification")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Registration", test_registration),
        ("Configuration", test_configuration),
        ("Templates", test_templates),
        ("Functionality", test_notion_type_functionality),
        ("App Integration", test_app_integration),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        results.append(test_func())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Notion project type is ready to use.")
        print("\nTo use it:")
        print("1. Export a Notion workspace (Markdown & CSV format)")
        print("2. Place it in projects/notion/<project_name>/")
        print("3. Run: python app.py")
        print("4. Visit: http://localhost:5000/notion")
        return 0
    else:
        print("✗ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
