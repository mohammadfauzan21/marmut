# create a virtual environment named 'venv' if it doesn't already exist
python3.9 -m venv env

# activate the virtual environment
env/Scripts/activate

# build_files.sh
python3.9 -m pip install -r requirements.txt

# make migrations
python3.9 manage.py makemigrations
python3.9 manage.py migrate 
python3.9 manage.py collectstatic