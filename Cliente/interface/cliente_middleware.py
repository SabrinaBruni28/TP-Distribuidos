import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import Pyro5.api
import Pyro5.errors

class UnixMiddlewareClient:
    def __init__(self, ip="localhost", porta=5000):
        self.nome = "Caldeirao:servicos.servidor"
        self.ip = ip
        self.porta = porta
        self.find_uri()

    def find_uri(self):
        try:
            ns = Pyro5.api.locate_ns(host=self.ip, port=self.porta)
        except Pyro5.errors.NamingError:
            print(f"❌ Erro: não foi possível localizar o Name Server em {self.ip}:{self.porta}.")
            return
        except Exception as e:
            print("❌ Erro locate:", e)
            self.uri = None
            return

        try:
            self.uri = ns.lookup(self.nome)
        except Pyro5.errors.NamingError:
            print(f"❌ Erro: nome '{self.nome}' não está registrado no Name Server.")
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
            print("🔌 Conexão encerrada com o middleware.\n")
        else:
            print("⚠️ Nenhuma conexão ativa para encerrar.\n")
    
    def __get_proxy(self, timeout=15):  # timeout em segundos
        if not self.uri:
            return None
        proxy = Pyro5.api.Proxy(self.uri)
        proxy._pyroTimeout = timeout  # ⏱️ define o timeout
        proxy._pyroBind()  # garante conexão
        print(f"✅ Conexão criada com o middleware (timeout={timeout}s)")
        return proxy
    
    def get_proxy(self):
        if not self.uri:
            print("⚠️ URI do middleware não está disponível.")
            return None

        for _ in range(3):
            try:
                proxy = self.__get_proxy()
                return proxy
            except Pyro5.errors.CommunicationError:
                print("🔄 Conexão recusada. Tentando atualizar URI no Name Server...")
                self.find_uri()
            except Pyro5.errors.PyroError as e:
                print("❌ Erro Pyro ao criar proxy:", e)
                return None
            except Exception as e:
                print("❌ Erro inesperado ao criar proxy:", e)
                return None

    def chamar_middleware(self, nome_funcao, *args, **kwargs):
        proxy = self.get_proxy()
        if not proxy:
            print("❌ Middleware indisponível.")
            return None

        try:
            funcao_remota = getattr(proxy, nome_funcao)
            print("⚙️  Função:", nome_funcao)
            
            resposta = funcao_remota(*args, **kwargs)
            #print("📬 Resposta:", resposta)
            return resposta
        except Exception as e:
            print(f"❌ Erro ao chamar '{nome_funcao}':", e)
            return None
        finally:
            self.close(proxy)

