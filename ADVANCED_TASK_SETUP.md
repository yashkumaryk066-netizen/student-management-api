# 🤖 Advanced Automation System Setup

I have created a robust, production-grade maintenance engine for your ERP.

Instead of running a simple python command, user `daily_maintenance.sh`.
This script automatically:
1.  **Activates Environment:** Safely loads all dependencies.
2.  **Runs Smart Reminders:** Sends alerts at 7 days, 3 days, 1 day, and Expiry.
3.  **Logs Activity:** Saves a detailed history to `daily_automation.log` (Professional Auditing).
4.  **Security Cleanup:** Auto-deletes expired login sessions to prevent hijack risks.

## 🚀 How to Enable (One-Time Setup)

1.  Go to your **PythonAnywhere Dashboard**.
2.  Click on the **Tasks** tab.
3.  **Schedule:** Set the time to `06:00 UTC` (or your preferred morning time).
4.  **Command:** Paste strictly this line:

```bash
/home/yashamishra/student-management-api/daily_maintenance.sh
```

5.  Click **Create**.

---

### ✅ That's it!
Your system will now:
*   Auto-wake up every morning.
*   Scan all client subscriptions.
*   Email/Notify users about expiry.
*   Lock expired accounts.
*   Log everything for you to check later.
