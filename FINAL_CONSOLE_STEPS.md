# 🚀 Final Console Steps (PythonAnywhere)

You asked what to do in the console. Here is the exact checklist to finalize the deployment.

### 1. Update Environment Variables
I have already added the Eazypay settings to your `.env` file with default values. You need to edit them with your **Real Keys**.

Run this command in the console:
```bash
nano .env
```
*   Use arrow keys to go to the bottom.
*   Change `EAZYPAY_MERCHANT_ID` to your actual Bank Merchant ID.
*   Change `EAZYPAY_ENCRYPTION_KEY` to your actual 128-bit Key.
*   Press `Ctrl+X`, then `Y`, then `Enter` to save.

### 2. Verify Deployment
I have already ran the build script, but to be 100% sure everything is synced, run this one last time:
```bash
bash DEPLOY_NOW.sh
```
*   This ensures all `pip` requirements are installed and database migrations are applied.

### 3. Create Superuser (If not done)
If you haven't created an admin account yet:
```bash
python manage.py createsuperuser
```
*   Follow the prompts to set a username and password.

### 4. Reload Web App (CRITICAL)
*   **Go to the "Web" tab** on your PythonAnywhere dashboard (not the console).
*   Click the big green **"Reload"** button.

### 5. Test Live
*   Visit: `https://yashamishra.pythonanywhere.com/`
*   Login as a Student.
*   Go to **Fee Status**.
*   Click **"Pay Now"** (It will now take you to the Bank Page).
