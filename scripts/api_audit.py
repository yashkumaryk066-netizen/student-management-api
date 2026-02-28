#!/usr/bin/env python3
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from django.urls import get_resolver
import re

print("="*70)
print("🔍 API ENDPOINT AUDIT")
print("="*70)

# Get all URL patterns
resolver = get_resolver()
patterns = []

def extract_patterns(urlpatterns, prefix=''):
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            extract_patterns(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            path = prefix + str(pattern.pattern)
            if '/api/' in path:
                patterns.append(path)

extract_patterns(resolver.url_patterns)

print(f"\n📊 Total API Endpoints: {len(patterns)}")
print("\n✅ EXISTING APIs:")
for p in sorted(set(patterns))[:30]:
    print(f"   {p}")

# Check for specific missing APIs
missing = []
required_apis = [
    '/api/roi/',
    '/api/lms/materials/',
    '/api/lms/assignments/',
    '/api/ai/leads/',
    '/api/hr/substitutes/',
    '/api/students/diary/',
    '/api/inventory/',
]

print("\n🔍 CHECKING REQUIRED APIs:")
for api in required_apis:
    exists = any(api.replace('/', '').replace('-', '') in p.replace('/', '').replace('-', '') for p in patterns)
    status = "✅ EXISTS" if exists else "❌ MISSING"
    print(f"   {api:<30} {status}")
    if not exists:
        missing.append(api)

print(f"\n❌ MISSING APIs: {len(missing)}")
for m in missing:
    print(f"   - {m}")

