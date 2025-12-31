# 🔄 PythonAnywhere Reload Instructions

## How to Reload Your Web App on PythonAnywhere

### Method 1: Using Web Interface (RECOMMENDED)

1. **Login to PythonAnywhere**:
   - Go to: https://www.pythonanywhere.com/login/
   - Username: yashamishra
   
2. **Navigate to Web App**:
   - Click "Web" tab in top menu
   - Or go directly to: https://www.pythonanywhere.com/user/yashamishra/webapps/

3. **Reload the App**:
   - Find the big green button that says **"Reload yashamishra.pythonanywhere.com"**
   - Click it!
   - Wait 20-30 seconds for reload to complete

### Method 2: Using API (From Terminal)

```bash
# Set your API token (get from Account page)
API_TOKEN="your_api_token_here"

# Reload the web app
curl -X POST \
  -H "Authorization: Token $API_TOKEN" \
  https://www.pythonanywhere.com/api/v0/user/yashamishra/webapps/yashamishra.pythonanywhere.com/reload/
```

## Verify Static Files Mapping

While on the Web App page, scroll down to **"Static files"** section.

Should show:
```
URL                  Directory
/static/             /home/tele/manufatures/staticfiles
```

If not configured, click "Enter URL" and "Enter path" to add it.

## After Reload - Testing

1. **Clear Browser Cache**:
   - Chrome/Edge: Ctrl + Shift + Delete
   - Or use Incognito/Private mode

2. **Test the Site**:
   - Main page: https://yashamishra.pythonanywhere.com/
   - Animation CSS: https://yashamishra.pythonanywhere.com/static/css/animations.css
   - Animation JS: https://yashamishra.pythonanywhere.com/static/js/animations.js

3. **Check for Animations**:
   - Welcome popup should appear after 2 seconds
   - Particles should be floating in background
   - Floating module cards visible
   - 3D hover effects on cards

## Troubleshooting

### If animations still not showing:

1. **Hard Refresh**: Ctrl + Shift + R (or Cmd + Shift + R on Mac)

2. **Check Browser Console** (F12):
   - Look for 404 errors on animations.css or animations.js
   - Check for JavaScript errors

3. **Verify Static Files**:
   ```bash
   ls -la /home/tele/manufatures/staticfiles/css/animations.css
   ls -la /home/tele/manufatures/staticfiles/js/animations.js
   ```

4. **Re-collect Static Files**:
   ```bash
   cd /home/tele/manufatures
   source venv/bin/activate  
   python manage.py collectstatic --noinput --clear
   ```
   Then reload web app again!

## Quick Checklist

- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Static files mapping configured in PythonAnywhere
- [ ] Web app reloaded (green button clicked)
- [ ] Waited 30 seconds
- [ ] Cleared browser cache / Used incognito
- [ ] Tested https://yashamishra.pythonanywhere.com/

## Common Issues

**Issue**: "Static files not found (404)"
**Solution**: Check static files mapping in PythonAnywhere Web tab

**Issue**: "Old version still showing"
**Solution**: Hard refresh browser (Ctrl + Shift + R) or use incognito

**Issue**: "Animations not working"
**Solution**: Check browser console for JavaScript errors, ensure animations.js loaded

---

**Current Status**:
- ✅ Static files collected: 179 files
- ✅ animation.css created: 5,926 bytes
- ✅ animations.js created: 4,329 bytes
- ⏳ Waiting for PythonAnywhere reload

**Last Deployed**: December 31, 2025 14:48 IST
