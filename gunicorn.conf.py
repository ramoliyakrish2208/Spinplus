# Gunicorn Production Server Configuration for Spin & Win SaaS
import multiprocessing

bind = "127.0.0.1:8000"
workers = 2
threads = 2
timeout = 60
keepalive = 5

accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

capture_output = True
enable_stdio_inheritance = True
