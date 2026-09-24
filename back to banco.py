cat  'EOF'  database.py
import requests

# Endereço da VM de Base de Dados
DB_URL = http192.168.1.115001dbquery

def executar_query_remota(sql, params=[])
    try
        response = requests.post(DB_URL, json={sql sql, params params})
        if response.status_code == 200
            return response.json()
        else
            print(fErro no servidor de base de dados {response.text})
            return None
    except Exception as e
        print(fFalha de conexão com a VM de Banco {e})
        return None

def init_db()
    # A inicialização e criação de tabelas já é tratada na VM de Banco de Dados
    pass
EOF