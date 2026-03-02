import paramiko

host = 'ssh.pythonanywhere.com'
user = 'yashamishra'
password = 'Ysonm@12'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Connecting to {host}...")
    client.connect(host, username=user, password=password)
    print("Connected.")
    
    commands = [
        "cd ~/student-management-api",
        "source venv/bin/activate",
        "python manage.py collectstatic --noinput",
        "touch /var/www/yashamishra_pythonanywhere_com_wsgi.py",
        "tail -n 50 /var/log/yashamishra.pythonanywhere.com.error.log"
    ]
    
    command = " && ".join(commands)
    print(f"Executing: {command}")
    
    stdin, stdout, stderr = client.exec_command(command)
    
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    
    print("\n--- STDOUT ---")
    print(out)
    
    print("\n--- STDERR ---")
    print(err)
    
finally:
    client.close()
