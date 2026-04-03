import paramiko
from decouple import config
import os

host = 'ssh.pythonanywhere.com'
user = config('PYTHONANYWHERE_SSH_USERNAME', default='yashamishra')
password = config('PYTHONANYWHERE_SSH_PASSWORD', default='')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Connecting...")
    client.connect(host, username=user, password=password, timeout=10)
    print("Connected.")
    
    print("Executing command to get logs...")
    stdin, stdout, stderr = client.exec_command("tail -n 100 /var/log/yashamishra.pythonanywhere.com.error.log")
    
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    
    print("\n--- OUTPUT ---")
    print(out)
    if err:
        print("\n--- ERROR ---")
        print(err)
        
    print("Running deployment script...")
    deploy_cmd = "cd ~/student-management-api && source venv/bin/activate && pip install -r requirements.txt && python manage.py collectstatic --noinput && touch /var/www/yashamishra_pythonanywhere_com_wsgi.py"
    stdin, stdout, stderr = client.exec_command(deploy_cmd)
    
    print("\n--- DEPLOY OUTPUT ---")
    print(stdout.read().decode('utf-8'))
    if stderr.read():
        print("\n--- DEPLOY ERROR ---")
        print(stderr.read().decode('utf-8'))
        
except Exception as e:
    print("Failed.", e)
finally:
    client.close()
