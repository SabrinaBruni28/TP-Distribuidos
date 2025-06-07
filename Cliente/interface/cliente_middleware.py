import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import Pyro5.api
import Pyro5.errors

class UnixMiddlewareClient:
    def __init__(self, ip="localhost", porta=5000):
        nome = "Caldeirao:servicos.servidor"

        try:
            ns = Pyro5.api.locate_ns(host=ip, port=porta)
        except Pyro5.errors.NamingError:
            print(f"❌ Erro: não foi possível localizar o Name Server em {ip}:{porta}.")
            return
        except Exception as e:
            print("❌ Erro locate:", e)
            self.uri = None
            return

        try:
            self.uri = ns.lookup(nome)
        except Pyro5.errors.NamingError:
            print(f"❌ Erro: nome '{nome}' não está registrado no Name Server.")
            self.uri = None
            return
        except Exception as e:
            print("❌ Erro lookup:", e)
            self.uri = None
            return

        print("🔎 Middleware encontrado:", self.uri)

    def close(self, proxy):
        if proxy:
            proxy._pyroRelease()
            print("🔌 Conexão encerrada com o middleware.")
        else:
            print("⚠️ Nenhuma conexão ativa para encerrar.")
    
    def get_proxy(self, timeout=15):  # timeout em segundos
        if not self.uri:
            return None
        proxy = Pyro5.api.Proxy(self.uri)
        proxy._pyroTimeout = timeout  # ⏱️ define o timeout
        proxy._pyroBind()  # garante conexão
        print(f"✅ Conexão criada com o middleware (timeout={timeout}s)")
        return proxy

    def chamar_middleware(self, nome_funcao, *args, **kwargs):
        proxy = self.get_proxy()
        if not proxy:
            print("❌ Middleware indisponível.")
            return None

        try:
            funcao_remota = getattr(proxy, nome_funcao)
            resposta = funcao_remota(*args, **kwargs)
            print("📬 Resposta:", resposta)
            return resposta
        except Exception as e:
            print(f"❌ Erro ao chamar '{nome_funcao}':", e)
            return None
        finally:
            self.close(proxy)

