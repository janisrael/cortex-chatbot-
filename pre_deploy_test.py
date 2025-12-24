#!/usr/bin/env python3
"""
Pre-Deployment Test Script
Validates imports, dependencies, and basic functionality before CI/CD deployment.
Run this before pushing to main branch to catch issues early.

Usage:
    python3 pre_deploy_test.py
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def test_import(module_name, description=None):
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        if description:
            print_success(f"{description}: {module_name}")
        else:
            print_success(f"Import: {module_name}")
        return True
    except ImportError as e:
        if description:
            print_error(f"{description}: {module_name} - {str(e)}")
        else:
            print_error(f"Import: {module_name} - {str(e)}")
        return False
    except Exception as e:
        if description:
            print_error(f"{description}: {module_name} - Unexpected error: {str(e)}")
        else:
            print_error(f"Import: {module_name} - Unexpected error: {str(e)}")
        return False

def test_critical_imports():
    """Test critical imports that must work"""
    print_info("\n=== Testing Critical Imports ===")
    
    critical_imports = [
        ("flask", "Flask"),
        ("flask_login", "Flask-Login"),
        ("langchain_core", "LangChain Core"),
        ("langchain_openai", "LangChain OpenAI"),
        ("langchain_community", "LangChain Community"),
        ("chromadb", "ChromaDB"),
        ("sentence_transformers", "Sentence Transformers"),
        ("openai", "OpenAI"),
    ]
    
    results = []
    for module, desc in critical_imports:
        result = test_import(module, desc)
        results.append(result)
    
    return all(results)

def test_application_imports():
    """Test application-specific imports"""
    print_info("\n=== Testing Application Imports ===")
    
    app_imports = [
        ("app", "Main application"),
        ("blueprints", "Blueprints"),
        ("services.chatbot_service", "Chatbot Service"),
        ("services.llm_service", "LLM Service"),
        ("services.knowledge_service", "Knowledge Service"),
        ("models.user", "User Model"),
        ("models.api_key", "API Key Model"),
    ]
    
    results = []
    for module, desc in app_imports:
        result = test_import(module, desc)
        results.append(result)
    
    return all(results)

def test_langchain_compatibility():
    """Test LangChain version compatibility"""
    print_info("\n=== Testing LangChain Compatibility ===")
    
    try:
        from langchain_core import __version__ as core_version
        print_success(f"langchain-core version: {core_version}")
        
        from langchain_openai import __version__ as openai_version
        print_success(f"langchain-openai version: {openai_version}")
        
        # Test critical imports from langchain_openai
        from langchain_openai import ChatOpenAI
        print_success("ChatOpenAI import successful")
        
        return True
    except ImportError as e:
        print_error(f"LangChain compatibility issue: {str(e)}")
        return False
    except Exception as e:
        print_error(f"LangChain compatibility test failed: {str(e)}")
        return False

def test_syntax():
    """Test Python syntax of key files"""
    print_info("\n=== Testing Python Syntax ===")
    
    key_files = [
        "app.py",
        "blueprints/__init__.py",
        "blueprints/api.py",
        "services/chatbot_service.py",
        "services/llm_service.py",
    ]
    
    results = []
    for file_path in key_files:
        if not os.path.exists(file_path):
            print_warning(f"File not found: {file_path}")
            continue
        
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            compile(code, file_path, 'exec')
            print_success(f"Syntax OK: {file_path}")
            results.append(True)
        except SyntaxError as e:
            print_error(f"Syntax error in {file_path}: {str(e)}")
            results.append(False)
        except Exception as e:
            print_error(f"Error checking {file_path}: {str(e)}")
            results.append(False)
    
    return all(results) if results else True

def test_requirements():
    """Test if requirements can be installed"""
    print_info("\n=== Testing Requirements ===")
    
    if not os.path.exists("requirements-prod.txt"):
        print_error("requirements-prod.txt not found")
        return False
    
    try:
        with open("requirements-prod.txt", 'r') as f:
            content = f.read()
        
        if not content.strip():
            print_error("requirements-prod.txt is empty")
            return False
        
        # Check for critical packages
        critical_packages = [
            "Flask",
            "langchain",
            "langchain-core",
            "langchain-openai",
            "chromadb",
        ]
        
        missing = []
        for pkg in critical_packages:
            if pkg.lower() not in content.lower():
                missing.append(pkg)
        
        if missing:
            print_warning(f"Potentially missing packages: {', '.join(missing)}")
        else:
            print_success("All critical packages found in requirements-prod.txt")
        
        return True
    except Exception as e:
        print_error(f"Error checking requirements: {str(e)}")
        return False

def main():
    """Run all pre-deployment tests"""
    print(f"{BLUE}{'='*60}")
    print("PRE-DEPLOYMENT TEST SUITE")
    print("="*60 + RESET)
    
    results = {
        "Critical Imports": test_critical_imports(),
        "Application Imports": test_application_imports(),
        "LangChain Compatibility": test_langchain_compatibility(),
        "Python Syntax": test_syntax(),
        "Requirements": test_requirements(),
    }
    
    print(f"\n{BLUE}{'='*60}")
    print("TEST RESULTS SUMMARY")
    print("="*60 + RESET)
    
    all_passed = True
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
            all_passed = False
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    if all_passed:
        print_success("ALL TESTS PASSED - Safe to deploy!")
        return 0
    else:
        print_error("SOME TESTS FAILED - Fix issues before deploying!")
        print_warning("Do NOT push to main branch until all tests pass.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
