import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Connecting to ssh.pythonanywhere.com...")
    client.connect('ssh.pythonanywhere.com', username='yashamishra', password='Ysonm@12', timeout=30)
    
    # Check if inside tarpit
    stdin, stdout, stderr = client.exec_command("echo 'Connected!'")
    print(stdout.read().decode().strip())
    
    # Just touch WSGI to reload before anything else, maybe memory issue
    print("Reloading...")
    stdin, stdout, stderr = client.exec_command("touch /var/www/yashamishra_pythonanywhere_com_wsgi.py")
    print(stdout.read().decode())
    
    # Read the error log
    print("Reading tail of error logs...")
    stdin, stdout, stderr = client.exec_command("tail -n 100 /var/log/yashamishra.pythonanywhere.com.error.log")
    logs = stdout.read().decode()
    if logs:
        print(logs)
    else:
        print("Error reading log:", stderr.read().decode())
        
except Exception as e:
    print("Failed to deploy:", e)
finally:
    client.close()
