import socket
import threading

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, addr):
        super().__init__()
        self.client_socket = client_socket
        self.addr = addr
        self.running = True
        self.lock = threading.Lock()

    def run(self):
        print(f"Cliente conectado: {self.addr}")
        try:
            while self.running:  # Loop principal mantém conexão aberta
                data = self.client_socket.recv(1024).decode()
                
                if not data:  # Cliente fechou conexão
                    break

                print(f"[{self.addr}] Comando: {data}")

                # Comando de encerramento explícito
                if data.lower() == "sair":
                    self.client_socket.sendall("Conexão encerrada".encode())
                    break

                # Dispara thread para processar comando SEM quebrar loop
                self.decisor(data)
                
        except Exception as e:
            print(f"Erro com {self.addr}: {e}")
        finally:
            self.encerrar()

    def decisor(self, data):
        match data:
            case "cadastrar":
                threading.Thread(target=self.processar_cadastro).start()
            case "login":
                threading.Thread(target=self.processar_cadastro).start()
            case _:
                with self.lock:
                    self.client_socket.sendall("Comando inválido".encode())


    def processar_cadastro(self):
        try:
            # Simular processamento demorado
            resposta = "{'status':'cadastro_ok'}"
            
            with self.lock:
                self.client_socket.sendall(resposta.encode())
            
            print(f"[{self.addr}] Cadastro processado")

        except Exception as e:
            print(f"Erro no cadastro: {e}")

    def processar_login(self):
        try:
            # Simular processamento demorado
            resposta = "{'status':'login_ok'}"
            
            with self.lock:
                self.client_socket.sendall(resposta.encode())
            
            print(f"[{self.addr}] Login processado")

        except Exception as e:
            print(f"Erro no login: {e}")

    def encerrar(self):
        if self.running:
            self.running = False
            self.client_socket.close()
            print(f"Conexão com {self.addr} encerrada")

def servidor(ip, port):
    # Aqui estou criando um objeto socket, nesse caso para o servidor
    # e, usando with, crio um bloco protegido
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((ip, port)) # vincula ao host e à porta
        server.listen(3) # modo escuta
        print(f"Servidor ativo em {ip}:{port}")

        while True:
            # Aceita a conexão
            client_socket, addr = server.accept()
            # Começa uma nova thread para lidar com o cliente
            ClientHandler(client_socket, addr).start()

servidor('', 5000)