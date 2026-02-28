#!/usr/bin/env python3

print("="*70)
print("🎯 ACTUAL vs FRONTEND API URL MAPPING")
print("="*70)

mapping = [
    {
        'module': 'ROI Analytics',
        'frontend_calling': '/api/roi/',
        'actual_backend': '/api/analytics/roi/',
        'fix': 'Update frontend URL'
    },
    {
        'module': 'LMS Materials',
        'frontend_calling': '/api/lms/materials/',
        'actual_backend': '/api/lms/materials/',
        'fix': '✅ Already Correct'
    },
    {
        'module': 'Assignments',
        'frontend_calling': '/api/lms/assignments/',
        'actual_backend': '/api/lms/assignments/',
        'fix': '✅ Already Correct'
    },
    {
        'module': 'AI Leads',
        'frontend_calling': '/api/ai/leads/',
        'actual_backend': '/api/leads/',
        'fix': 'Update frontend URL'
    },
    {
        'module': 'Substitutes',
        'frontend_calling': '/api/hr/substitutes/',
        'actual_backend': '/api/substitutes/',
        'fix': 'Update frontend URL'
    },
    {
        'module': 'Student Diary',
        'frontend_calling': '/api/students/diary/',
        'actual_backend': '/api/diary/',
        'fix': 'Update frontend URL'
    },
    {
        'module': 'Inventory',
        'frontend_calling': '/api/inventory/',
        'actual_backend': '/api/inventory/',
        'fix': '✅ Already Correct'
    },
]

print("\n📊 URL Mismatch Analysis:\n")
for m in mapping:
    status = "🔴 MISMATCH" if m['fix'] != '✅ Already Correct' else "🟢 MATCH"
    print(f"{status} {m['module']}")
    print(f"   Frontend calls: {m['frontend_calling']}")
    print(f"   Backend serves: {m['actual_backend']}")
    print(f"   Action: {m['fix']}\n")

print("="*70)
print("✅ SOLUTION: Update 4 frontend URLs to match backend")
print("="*70)
