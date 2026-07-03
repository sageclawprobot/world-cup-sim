#!/usr/bin/env python3
"""
Simple test runner for World Cup Simulator
Runs test modules without requiring pytest
"""
import sys
import subprocess
from pathlib import Path


def main():
    """Run all test files."""
    project_root = Path(__file__).parent
    src_dir = project_root / 'src'
    
    print("🧪 World Cup Simulator - Test Suite")
    print("=" * 60)
    print()
    
    test_files = [
        'test_models.py',
        'test_predictor.py',
        'test_api_client.py',
        'test_visualizer.py'
    ]
    
    results = {}
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        test_path = src_dir / test_file
        if not test_path.exists():
            print(f"⚠️  {test_file} not found")
            continue
        
        print(f"📋 Running {test_file}...")
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_path)],
                cwd=str(src_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ {test_file} - PASSED")
                results[test_file] = "PASSED"
                # Count tests from output
                if "passed" in result.stdout:
                    passed = result.stdout.count("PASSED")
                    total_passed += passed if passed > 0 else 1
            else:
                print(f"❌ {test_file} - FAILED")
                print(result.stdout)
                print(result.stderr)
                results[test_file] = "FAILED"
                total_failed += 1
        except subprocess.TimeoutExpired:
            print(f"⏱️  {test_file} - TIMEOUT")
            results[test_file] = "TIMEOUT"
            total_failed += 1
        except Exception as e:
            print(f"⚠️  {test_file} - ERROR: {e}")
            results[test_file] = "ERROR"
            total_failed += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_file, status in results.items():
        symbol = "✅" if status == "PASSED" else "❌"
        print(f"{symbol} {test_file:30} {status}")
    
    print()
    print(f"Total: {total_passed + total_failed} tests")
    
    if total_failed == 0:
        print("✨ All tests passed!")
        return 0
    else:
        print(f"❌ {total_failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
