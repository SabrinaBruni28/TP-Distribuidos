import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import Pyro5.api

class UnixMiddlewareClient:
    def __init__(self, ip, porta):
        nome = ""
        uri = f"PYRO:{nome}@{ip}:{porta}"
        self.middleware = Pyro5.api.Proxy(uri)
        print("Conexão criada com o middleware: ", uri)

    def close(self):
        self.middleware._pyroRelease()
        print("Conexão encerrada com o middleware.")
