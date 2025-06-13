from Pyro5.nameserver import start_ns
import sys

ip = "127.0.0.1"
porta = 9090

if len(sys.argv) >= 3:
    ip = sys.argv[1]
    porta = int(sys.argv[2])

print(f"Iniciando Name Server Pyro5 em {ip}:{porta}...")

try:
    ns, daemon, _ = start_ns(host=ip, port=porta)
    print("Name Server iniciado com sucesso!")
    daemon.requestLoop()
except Exception as e:
    print(f"[ERRO] Não foi possível iniciar o Name Server: {e}")
