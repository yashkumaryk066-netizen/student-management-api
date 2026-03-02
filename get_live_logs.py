import paramiko
import sys

host = 'ssh.pythonanywhere.com'
user = 'yashamishra'
password = 'Ysonm@12'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Connecting to {host}...")
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
        
except Exception as e:
    print("Failed.", e)
finally:
    client.close()
