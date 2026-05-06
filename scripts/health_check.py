"""
Health Check Script
Run: python scripts/health_check.py

Server health verify करतो.
"""

import requests
import sys


def check_health(base_url="http://localhost:8661"):
    print(f"Checking: {base_url}")
    
    checks = []
    
    # 1. Health endpoint
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        if r.status_code == 200:
            checks.append(("Health endpoint", True, "OK"))
        else:
            checks.append(("Health endpoint", False, f"Status {r.status_code}"))
    except Exception as e:
        checks.append(("Health endpoint", False, str(e)))
    
    # 2. API docs
    try:
        r = requests.get(f"{base_url}/docs", timeout=5)
        checks.append(("API docs", r.status_code == 200, f"Status {r.status_code}"))
    except Exception as e:
        checks.append(("API docs", False, str(e)))
    
    # 3. Auth endpoint exists
    try:
        r = requests.post(f"{base_url}/api/auth/login",
                         json={"email": "test", "password": "test"},
                         timeout=5)
        checks.append(("Auth endpoint", r.status_code in [200, 401, 422], f"Status {r.status_code}"))
    except Exception as e:
        checks.append(("Auth endpoint", False, str(e)))
    
    # Print results
    print("\n" + "=" * 40)
    all_ok = True
    for name, ok, msg in checks:
        status = "✅" if ok else "❌"
        print(f"{status} {name}: {msg}")
        if not ok:
            all_ok = False
    
    print("=" * 40)
    if all_ok:
        print("✅ All checks passed!")
    else:
        print("❌ Some checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8661"
    check_health(url)
