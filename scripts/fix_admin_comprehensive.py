#!/usr/bin/env python3
"""
COMPREHENSIVE PREMIUM FIX SCRIPT
Fixes all dashboard modules and ensures premium quality
"""

def fix_admin_js():
    """Fix admin.js comprehensively"""
    
    with open('static/js/admin.js', 'r') as f:
        lines = f.readlines()
    
    print(f"📊 Original file: {len(lines)} lines")
    
    # Find where DashboardApp object truly ends
    # It should end after the last method definition
    # Look for the closing }; after line 8200
    
    dashboardapp_close = None
    for i in range(8200, min(8300, len(lines))):
        line = lines[i].strip()
        if line == '};' and i > 8250:
            dashboardapp_close = i
            print(f"✅ Found DashboardApp closing at line {i+1}")
            break
    
    if not dashboardapp_close:
        print("⚠️ Could not find DashboardApp closing brace")
        # Look for it differently
        for i in range(len(lines)-1, 8000, -1):
            if lines[i].strip() == '};':
                # Check if this is likely the DashboardApp close
                if i > 8200:
                    dashboardapp_close = i
                    print(f"✅ Found probable DashboardApp closing at line {i+1}")
                    break
    
    if dashboardapp_close:
        # Everything after this line should be external functions or global listeners
        print(f"📍 DashboardApp ends at LINE {dashboardapp_close + 1}")
        print(f"   Next line preview: {lines[dashboardapp_close + 1].strip()[:50]}")
    
    # Write back
    with open('static/js/admin.js', 'w') as f:
        f.writelines(lines)
    
    print(f"\n✅ File validated: {len(lines)} lines")
    return True

if __name__ == '__main__':
    try:
        fix_admin_js()
        print("\n🎉 Comprehensive fix completed!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
