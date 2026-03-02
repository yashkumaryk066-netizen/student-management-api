#!/bin/bash
expect << 'EOD'
spawn ssh -o StrictHostKeyChecking=no yashamishra@ssh.pythonanywhere.com
expect "password:"
send "Ysonm@12\r"
expect "yashamishra"
send "cd ~/student-management-api && source venv/bin/activate && pip install -r requirements.txt && python manage.py collectstatic --noinput && touch /var/www/yashamishra_pythonanywhere_com_wsgi.py && tail -n 100 /var/log/yashamishra.pythonanywhere.com.error.log > ~/error_dump.txt\r"
expect "yashamishra"
send "cat ~/error_dump.txt\r"
expect "yashamishra"
send "exit\r"
expect eof
EOD
