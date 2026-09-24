from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Certifique-se de que aponta para o ficheiro correto da base de dados
DB_NAME = "tarefas.db"

@app.route('/db/query', methods=['POST'])
def db_query():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
        
    sql = data.get('sql', '')
    params = data.get('params', [])
    
    if not sql:
        return jsonify({"error": "Query vazia"}), 400

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Executa a query enviada pela VM de Back-end
        cursor.execute(sql, params)
        
        sql_lower = sql.strip().lower()
        if sql_lower.startswith("select"):
            rows = cursor.fetchall()
            cols = [description[0] for description in cursor.description] if cursor.description else []
            result = {"rows": rows, "columns": cols}
        else:
            conn.commit()
            result = {
                "lastrowid": cursor.lastrowid, 
                "rowcount": cursor.rowcount,
                "rows": [],
                "columns": []
            }
            
        conn.close()
        return jsonify(result)
        
    except Exception as e:
        print(f"Erro na execução da query: {e}")
        return jsonify({"error": str(e), "rows": [], "columns": []}), 500

if __name__ == '__main__':
    # Arranca o servidor na porta 5001, acessível por outras VMs
    app.run(host='0.0.0.0', port=5001, debug=True)
