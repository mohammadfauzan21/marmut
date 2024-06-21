# create a virtual environment named 'venv' if it doesn't already exist
python3.9 -m venv venv

# activate the virtual environment
venv/bin/activate

# build_files.sh
pip install -r requirements.txt

# make migrations
python3.9 manage.py makemigrations
python3.9 manage.py migrate 
python manage.py collectstatic --noinput