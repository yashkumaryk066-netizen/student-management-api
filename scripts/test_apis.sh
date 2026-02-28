#!/bin/bash

# API Health Check Script
echo "🔍 Testing Critical APIs..."
echo ""

TOKEN=""

# Test 1: Profile API
echo "1️⃣ Testing Profile API..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8001/api/profile/
echo ""

# Test 2: Students API
echo "2️⃣ Testing Students API..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8001/api/students/
echo ""

# Test 3: Dashboard Stats
echo "3️⃣ Testing Dashboard Stats..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8001/api/dashboard/stats/
echo ""

# Test 4: Payments API
echo "4️⃣ Testing Payments API..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8001/api/payments/
echo ""

# Test 5: Attendance API
echo "5️⃣ Testing Attendance API..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8001/api/attendence/
echo ""

# Test 6: Library API
echo "6️⃣ Testing Library API..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8001/api/library/books/
echo ""

# Test 7: Exams API
echo "7️⃣ Testing Exams API..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8001/api/exams/
echo ""

# Test 8: Live Classes API
echo "8️⃣ Testing Live Classes API..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8001/api/live-classes/
echo ""

echo "✅ API Health Check Complete!"
echo "Note: 401 = Authentication required (expected)"
echo "Note: 404 = Endpoint not found (needs fixing)"
echo "Note: 500 = Server error (critical issue)"
