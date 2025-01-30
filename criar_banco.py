from app import app, db

@app.route('/criar_banco')
def criar_banco():
    db.create_all()  # Cria todas as tabelas do banco de dados
    return "Banco de dados criado com sucesso!"