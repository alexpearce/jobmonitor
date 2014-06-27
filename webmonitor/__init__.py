from flask import (
    # Creating app instances
    Flask
)

# Define the app and load its configuration from config.py
app = Flask(__name__)
app.config.from_object('webmonitor.config')

from webmonitor import views
