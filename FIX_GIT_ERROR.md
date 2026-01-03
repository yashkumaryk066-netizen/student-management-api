# 🚨 Fix for "Local Changes" Error

The error `Aborting` happened because there are changes on the server that clash with the new code. We need to force the update.

### ✅ Run these 2 commands in your console:

1.  **Discard local changes (Reset):**
    ```bash
    git reset --hard HEAD
    ```
    *(This fixes the "overwritten by merge" error)*

2.  **Pull the new code:**
    ```bash
    git pull origin main
    ```

3.  **Go to Web Tab -> Reload**

Now your site will work!
