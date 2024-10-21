python -m venv ../python/venv

cd ../python

call venv\Scripts\activate.bat

pip install -r requirements.txt

call venv\Scripts\deactivate.bat

pause