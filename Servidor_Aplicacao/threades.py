import threading

class CommandThread(threading.Thread):
    def __init__(self, comando):
        super().__init__()
        self.comando = comando

    def run(self):
        print("Thread iniciada.")
        self.comando()
        print("Thread finalizada.")