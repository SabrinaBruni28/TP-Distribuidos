# 🧙‍♂️ Caldeirão
**Um sistema distribuído de Marketplace de Poções Mágicas**

## 💻 Como Executar

### ▶️ Execução Separada (um processo por máquina)

1. **Acessar a pasta** mais externa do repositório.

2. **Criar ambiente virtual** (executar **uma vez**):
   ```bash
   make criar_ambiente
   ```

3. **Ativar ambiente virtual** (sempre que necessário):
   ```bash
   source .venv/bin/activate
   ```
   > Você saberá que o ambiente está ativo quando o terminal mostrar algo como:
   ```
   (.venv) $
   ```
   > Para desativar o ambiente depois:
   ```
   deactivate
   ```

4. **Instalar bibliotecas** (executar **uma vez**):
   ```bash
   make instalar_bibliotecas
   ```
5. **Iniciar o name server**:
   ```bash
   make nameServer
   ```

6. **Executar o processo desejado**:
   ```bash
   make {processo}
   ```
   Onde `{processo}` pode ser:
   - `cliente`
   - `servidorAP`
   - `servidorBD`

   Para executar o cliente com IP e Porta personalizados:
   ```bash
   make cliente IP="ip" PORTA=porta
   ```
   Para executar o servidor de Aplicação ou de Banco de Dados com IP e Porta personalizados:
   ```bash
   make {processo} IP="ip" PORTA=porta HOST=host
   ```
   > Por padrão: IP = `"127.0.0.1"`, PORTA = `9090`

   > O IP a a PORTA são referetes ao name server e o HOST é referente ao ip da máquina que está sendo executado.
---

### 🧪 Execução Conjunta (na mesma máquina com terminais diferentes)

1. **Acessar a pasta** mais externa do repositório.

2. **Criar ambiente virtual** (executar **uma vez**):
   ```bash
   make criar_ambiente
   ```

3. **Ativar ambiente virtual** (sempre que necessário):
   ```bash
   source .venv/bin/activate
   ```

4. **Instalar bibliotecas** (executar **uma vez**):
   ```bash
   make instalar_bibliotecas
   ```

5. **Abrir quatro terminais** (ainda no diretório raiz) e executar:

   - **Name Server**:
     ```bash
     make nameServer
     ```

   - **Servidor de Banco de Dados** (opcionalmente com IP e porta):
     ```bash
     make servidorBD
     ```

   - **Servidor de Aplicação** (opcionalmente com IP e porta):
     ```bash
     make servidorAP
     ```

   - **Cliente** (opcionalmente com IP e porta):
     ```bash
     make cliente
     ```
