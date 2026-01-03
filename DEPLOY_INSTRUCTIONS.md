# Deployment Instructions

This project is fully ready for deployment.

## Option 1: PythonAnywhere (Recommended)

1.  **Upload Code**:
    *   Pull your code into PythonAnywhere assuming you are using git:
        ```bash
        git pull origin main
        ```

2.  **Environment Setup**:
    *   Open a Bash console.
    *   Create a virtual environment (if not exists):
        ```bash
        mkvirtualenv --python=/usr/bin/python3.10 my-virtualenv
        ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Environment Variables**:
    *   Create a `.env` file in your project root `/home/yourusername/manufatures/.env`.
    *   Copy content from `.env.example` and fill in real values.
    *   **Crucial**: Add `EAZYPAY_MERCHANT_ID`, `EAZYPAY_ENCRYPTION_KEY`, etc. for payments.

4.  **Static Files**:
    *   Run: `python manage.py collectstatic`

5.  **Web Tab Configuration**:
    *   **Source code**: `/home/yourusername/manufatures`
    *   **Working directory**: `/home/yourusername/manufatures`
    *   **WSGI configuration file**: Update it to import your project `manufatures.wsgi`.
    *   **Virtualenv**: `/home/yourusername/.virtualenvs/my-virtualenv`
    *   **Static files**:
        *   URL: `/static/`
        *   Directory: `/home/yourusername/manufatures/staticfiles`

---

## Option 2: VPS / Generic Linux (Ubuntu/Debian)

1.  Run the build script:
    ```bash
    ./build.sh
    ```
2.  Use `gunicorn` to serve the app:
    ```bash
    gunicorn manufatures.wsgi --bind 0.0.0.0:8000
    ```
3.  Use Nginx as a reverse proxy to port 8000.
