from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import calendar
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///folgas.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Modelo de Usuário (Funcionario e Administrador)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    registro = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    senha = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # "funcionario" ou "administrador"

# Definição de Agendamento de Folga
class Agendamento(db.Model):
    __tablename__ = 'agendamento'

    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(100), nullable=False)  # Nova coluna 'motivo' para armazenar o motivo da folga

    # Relacionamento com User
    funcionario = db.relationship('User', backref=db.backref('agendamentos', lazy=True))


# Modelo de Folga (relacionamento com User)
class Folga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="Pendente")  # "Pendente", "Deferida"

    funcionario = db.relationship('User', backref=db.backref('folgas', lazy=True))


# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos', 'danger')
    return render_template('login.html')


# Rota de Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Página Principal (Index)
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


# Rota de Agendamento de Folga
@app.route('/agendar', methods=['GET', 'POST'])
@login_required
def agendar():
    if request.method == 'POST':
        nome = current_user.nome  # Captura o nome do usuário logado
        registro = current_user.registro  # Captura o registro do usuário logado
        data_folga = datetime.datetime.strptime(request.form['data'], '%Y-%m-%d').date()  # Converte a data para o formato correto
        motivo = request.form['motivo']  # Captura o motivo escolhido pelo usuário

        # Criação do agendamento de folga
        agendamento = Agendamento(
            funcionario_id=current_user.id,  # Associa o agendamento ao funcionário logado
            data=data_folga,  # Data da folga
            motivo=motivo,  # Motivo da folga
            status='em_espera'  # O status é definido como 'em_espera' por padrão
        )
        # Adiciona o agendamento ao banco de dados e faz o commit
        db.session.add(agendamento)
        db.session.commit()

        # Exibe a mensagem de sucesso para o usuário
        flash('Folga agendada com sucesso', 'success')
        return redirect(url_for('calendario'))  # Redireciona para a página do calendário

    return render_template('agendar.html')  # Exibe o formulário de agendamento


# Calendário de Folgas
@app.route('/calendario', defaults={'year': 2025, 'month': 1}, methods=['GET', 'POST'])
@app.route('/calendario/<int:year>/<int:month>', methods=['GET', 'POST'])
@login_required
def calendario(year, month):
    # Intervalo de 10 anos a partir de 2025
    inicio_ano = 2025
    fim_ano = inicio_ano + 9  # 10 anos

    # Ajuste para garantir que o mês está entre 1 e 12
    while month < 1:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1

    # Calcular o mês e ano anteriores
    prev_month = 12 if month == 1 else month - 1
    prev_year = year if month > 1 else year - 1

    # Calcular o próximo mês e ano
    next_month = 1 if month == 12 else month + 1
    next_year = year if month < 12 else year + 1

    # Obter o primeiro e o último dia do mês
    try:
        first_day_of_month = datetime.date(year, month, 1)
        last_day_of_month = datetime.date(year, month, calendar.monthrange(year, month)[1])
    except ValueError as e:
        return f"Erro ao calcular datas: {e}", 400

    # Consulta dos agendamentos
    agendamentos = Agendamento.query.filter(
        Agendamento.data >= first_day_of_month,
        Agendamento.data <= last_day_of_month
    ).all()

    # Organizar os agendamentos por data
    folgas_por_data = {}
    for agendamento in agendamentos:
        if agendamento.data not in folgas_por_data:
            folgas_por_data[agendamento.data] = []
        folgas_por_data[agendamento.data].append(agendamento)

    return render_template(
        'calendario.html',
        year=year,
        month=month,
        prev_month=prev_month,
        next_month=next_month,
        prev_year=prev_year,
        next_year=next_year,
        folgas_por_data=folgas_por_data,
        days_in_month=calendar.monthrange(year, month)[1],
        calendar=calendar,
        datetime=datetime,
        inicio_ano=inicio_ano,
        fim_ano=fim_ano
    )

# Rota de Registro (para Novo Usuário)
from email_validator import validate_email, EmailNotValidError

# Rota de Registro (para Novo Usuário)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        registro = request.form['registro']
        email = request.form['email']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar_senha']
        tipo = request.form['tipo']

        # Verifica se as senhas coincidem
        if senha != confirmar_senha:
            flash('As senhas não coincidem', 'danger')
            return render_template('register.html')

        # Verifica se o e-mail é válido
        try:
            validate_email(email)
        except EmailNotValidError as e:
            flash(f'E-mail inválido: {str(e)}', 'danger')
            return render_template('register.html')

        # Verifica se o e-mail já está cadastrado
        if User.query.filter_by(email=email).first():
            flash('Este e-mail já está em uso', 'danger')
            return render_template('register.html')

        # Criptografa a senha usando pbkdf2:sha256 (método compatível)
        senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')

        # Criação do novo usuário
        new_user = User(nome=nome, registro=registro, email=email, senha=senha_hash, tipo=tipo)
        db.session.add(new_user)
        db.session.commit()

        flash('Usuário registrado com sucesso. Faça login para continuar.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Rota de Criação de Admin
@app.route('/criar_admin')
def criar_admin():
    admin_email = 'nilcr94@gmail.com'
    admin_nome = 'Nilson Cruz'
    admin_registro = '43546'
    admin_senha = generate_password_hash('neto1536', method='pbkdf2:sha256')
    admin_tipo = 'administrador'

    admin = User.query.filter_by(email=admin_email).first()

    if not admin:
        novo_admin = User(nome=admin_nome, registro=admin_registro, email=admin_email, senha=admin_senha, tipo=admin_tipo)
        db.session.add(novo_admin)
        db.session.commit()
        return 'Conta administrador criada com sucesso!'
    else:
        return 'A conta administrador já existe.'


# Rota de Deferimento de Folgas  
@app.route('/deferir_folgas', methods=['GET', 'POST'])
@login_required
def deferir_folgas():
    if current_user.tipo != 'administrador':  # Verifica se o usuário é um administrador
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('index'))  # Redireciona para a página inicial

    # Consulta as folgas com status 'em_espera'
    folgas_em_espera = Agendamento.query.filter_by(status='em_espera').all()

    if request.method == 'POST':
        # Processa a atualização do status da folga (Deferir ou Indeferir)
        folga_id = request.form.get('folga_id')
        status = request.form.get('status')

        agendamento = Agendamento.query.get(folga_id)
        if agendamento:
            agendamento.status = status
            db.session.commit()
            flash(f'Folga {agendamento.funcionario.nome} atualizada para {status}.', 'success')

        return redirect(url_for('deferir_folgas'))  # Redireciona de volta para a página de deferimento

    # Passa as folgas pendentes para o template
    return render_template('deferir_folgas.html', folgas_em_espera=folgas_em_espera)

# Rota de Histórico de Folgas
@app.route('/historico', methods=['GET'])
@login_required
def historico():
    # Consulta as folgas do funcionário logado
    folgas = Folga.query.filter_by(funcionario_id=current_user.id).all()

    # Contabiliza as folgas por tipo
    folgas_contabilizadas = {
        'AB': 0,  # Abonada
        'BH': 0,  # Banco de Horas
        'DS': 0,  # Doação de Sangue
        'TRE': 0,  # TRE
        'FS': 0   # Falta Simples
    }

    # Conta as folgas por tipo
    for folga in folgas:
        if folga.motivo in folgas_contabilizadas:
            folgas_contabilizadas[folga.motivo] += 1

    # Passa os dados para o template
    return render_template('historico.html', folgas_contabilizadas=folgas_contabilizadas)


# Inicialização do Banco de Dados
@app.route('/criar_banco')
def criar_banco():
    db.create_all()
    return "Banco de dados criado com sucesso!"


# Login Manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run(debug=True)
