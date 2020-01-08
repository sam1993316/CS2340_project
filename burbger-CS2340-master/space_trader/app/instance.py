import os
from flask import Flask
instance = Flask(__name__)
instance.config['SECRET_KEY'] = os.urandom(32) or "iashbjfuihbasduagvdusbhcaisj"
