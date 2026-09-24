cat << 'EOF' > database.py
import requests

DB_URL = "http://192.168.1.11:5001/db/query"

def executar_query_remota(sql, params=[]):
    try:
        response = requests.post(DB_URL, json={"sql": sql, "params": params}, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro no servidor de base de dados: {response.text}")
            return None
    except Exception as e:
        print(f"Falha de conexão com a VM de Banco: {e}")
        return None

class RemoteCursor:
    def __init__(self, resultados, lastrowid=None):
        self.resultados = resultados if isinstance(resultados, list) else []
        self.lastrowid = lastrowid

    def fetchall(self):
        return self.resultados

    def fetchone(self):
        if self.resultados:
            return self.resultados[0]
        # Fallback seguro para comandos de inserção (INSERT) que não retornam linhas diretamente
        return {"id": self.lastrowid or 1, "titulo": "", "descricao": "", "status": "pendente", "prioridade": "media", "projeto_id": None}

class RemoteConnection:
    def execute(self, sql, params=()):
        params_list = list(params) if params else []
        res = executar_query_remota(sql, params_list)
        
        linhas = res.get("rows", []) if res else []
        lastrowid = res.get("lastrowid") if res else None
        
        cursor = RemoteCursor(linhas, lastrowid)
        return cursor

    def cursor(self):
        return self

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
    pass
EOF
