# 🧙‍♂️ Caldeirão
**Um sistema distribuído de Marketplace de Poções Mágicas**

## 💻 Como Executar

### ▶️ Execução Separada (um processo por máquina)

1. **Acesse a pasta** correspondente ao processo: `Cliente`, `ServidorAp` ou `ServidorBD`.

2. **Criar ambiente virtual** (executar **uma vez**):
   ```bash
   make criar_ambiente
   ```

3. **Ativar ambiente virtual** (sempre que necessário):
   ```bash
   make ativar_ambiente
   ```
   > Você saberá que o ambiente está ativo quando o terminal mostrar algo como:
   ```
   (.venv) $
   ```

4. **Instalar bibliotecas** (executar **uma vez**):
   ```bash
   make instalar_bibliotecas
   ```

5. **Executar o processo desejado**:
   ```bash
   make {processo}
   ```
   Onde `{processo}` pode ser:
   - `cliente`
   - `servidorAp`
   - `servidorBD`

   Para executar o **cliente** com IP e Porta personalizados:
   ```bash
   make cliente IP="ip" PORTA=porta
   ```
   > Por padrão: IP = `"localhost"` e PORTA = `5000`

---

### 🧪 Execução Conjunta (na mesma máquina com terminais diferentes)

1. **Estar no diretório raiz**, fora das pastas dos processos.

2. **Criar ambiente virtual** (executar **uma vez**):
   ```bash
   make criar_ambiente
   ```

3. **Ativar ambiente virtual** (sempre que necessário):
   ```bash
   make ativar_ambiente
   ```

4. **Instalar bibliotecas** (executar **uma vez**):
   ```bash
   make instalar_bibliotecas
   ```

5. **Abrir três terminais** (um para cada processo, ainda no diretório raiz) e executar:

   - **Servidor de Banco de Dados**:
     ```bash
     make servidorBD
     ```

   - **Servidor de Aplicação**:
     ```bash
     make servidorAp
     ```

   - **Cliente** (opcionalmente com IP e porta):
     ```bash
     make cliente
     ```
     ou
     ```bash
     make cliente IP="ip" PORTA=porta
     ```
