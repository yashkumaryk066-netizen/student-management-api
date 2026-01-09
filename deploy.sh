git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch /var/www/yashamishra_pythonanywhere_com_wsgi.py
