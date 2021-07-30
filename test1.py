import threading
from time import sleep
event = threading.Event()
def info():
    print('%s is ready to do.' % (threading.currentThread().name))
    event.wait()
    print('%s is running.' % (threading.currentThread().name))
threading.Thread(target=info,name=('小白')).start()
threading.Thread(target=info,name=('小黑')).start()
sleep(2)
print('%s is running.' % (threading.currentThread().name))
event.set()
