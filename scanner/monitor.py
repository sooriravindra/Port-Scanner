from celery import Celery
from constants import *

app = Celery(APP_NAME,backend=BACKEND,broker=BROKER)
workers_list = []

def my_monitor(app):
    state = app.events.State()

    def worker_online(event):
        print("Worker online event")
        print("Hostname: ",event["hostname"])
        workers_list.append(event["hostname"])
        
    def worker_offline(event):
        print("Worker offline event")
        print("Hostname: ",event["hostname"])
        workers_list.remove(event["hostname"])
    
    def task_started(event):
        print("Task started event")
        print("Task Id: ",event["uuid"])
        print("Hostname: ",event["hostname"])

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
                'worker-online': worker_online,
                'worker-offline': worker_offline,
                'task-started': task_started,
                '*': state.event,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)

my_monitor(app)