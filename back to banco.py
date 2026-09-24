import requests

# Endereço da VM de Base de Dados
DB_URL = "http://192.168.1.11:5001/db/query"

def executar_query_remota(sql, params=[]):
    try:
        response = requests.post(DB_URL, json={"sql": sql, "params": params})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro no servidor de base de dados: {response.text}")
            return None
    except Exception as e:
        print(f"Falha de conexão com a VM de Banco: {e}")
        return None

# Função de compatibilidade exigida pelo app.py antigo
class RemoteCursor:
    def __init__(self):
        self.lastrowid = None

    def execute(self, sql, params=()):
        # Converte parâmetros para lista se forem tuplos
        res = executar_query_remota(sql, list(params))
        if res and "lastrowid" in res:
            self.lastrowid = res["lastrowid"]
        return res

    def fetchall(self):
        # Esta função simula o fetchall para consultas SELECT
        # No nosso modelo atual, as queries já retornam o resultado na chamada POST
        return []

class RemoteConnection:
    def cursor(self):
        return RemoteCursor()

    def commit(self):
        pass

    def close(self):
        pass

class get_connection:
    def __enter__(self):
        return RemoteConnection()
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def init_db():
    # A inicialização e criação de tabelas é tratada na VM de Banco de Dados
    pass
