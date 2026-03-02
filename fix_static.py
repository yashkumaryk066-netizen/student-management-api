import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Connecting to pythonanywhere...")
    client.connect('ssh.pythonanywhere.com', username='yashamishra', password='Ysonm@12', timeout=30)
    print("Connected!")
    
    # Check what is in the staticfiles dir
    stdin, stdout, stderr = client.exec_command("ls -la /home/yashamishra/student-management-api/staticfiles/css/")
    out = stdout.read().decode()
    print("--- CSS DIR ---")
    print(out)
    
    # Setup WSGI for whitenoise properly if missing
    wsgi_fix = """
echo "import os
import sys

path = '/home/yashamishra/student-management-api'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'manufatures.settings'

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
application = get_wsgi_application()
application = WhiteNoise(application, root='/home/yashamishra/student-management-api/staticfiles')
" > /var/www/yashamishra_pythonanywhere_com_wsgi.py
"""
    stdin, stdout, stderr = client.exec_command(wsgi_fix)
    print("WSGI rewrite completed.")
    
    # Running collectstatic to make sure
    stdin, stdout, stderr = client.exec_command("cd ~/student-management-api && source venv/bin/activate && python manage.py collectstatic --noinput")
    print("Collectstatic stderr:", stderr.read().decode())
    
    # Reload server
    stdin, stdout, stderr = client.exec_command("touch /var/www/yashamishra_pythonanywhere_com_wsgi.py")
    print("Restarted server.")
    
except Exception as e:
    print("Failed.", e)
finally:
    client.close()
