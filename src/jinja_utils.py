from datetime import datetime
from jinja2 import Environment, FileSystemLoader

def strftime(value, format_string):
    dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
    return dt.strftime(format_string)

def create_jinja2_environment():
    env = Environment(loader=FileSystemLoader("src/templates"), extensions=['jinja2.ext.i18n'])
    env.filters['strftime'] = strftime
    return env