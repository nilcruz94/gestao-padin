from flask import Flask, render_template, redirect, url_for, request, flash
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
import calendar
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///folgas.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo User (Funcionario e Administrador)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    registro = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    senha = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # "funcionario" ou "administrador"
    
    # Banco de horas em minutos
    banco_horas = db.Column(db.Integer, default=0, nullable=False)

    # Relacionamento com Agendamento
    agendamentos = db.relationship('Agendamento', backref='user_funcionario', lazy=True)

# Modelo Agendamento
class Agendamento(db.Model):
    __tablename__ = 'agendamento'
    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(100), nullable=False)
    tipo_folga = db.Column(db.String(50))  # Coluna tipo_folga
    data_referencia = db.Column(db.Date)  # Coluna data_referencia
    horas = db.Column(db.Integer, nullable=True)  # Coluna para horas
    minutos = db.Column(db.Integer, nullable=True)  # Coluna para minutos

    # Relacionamento com o modelo User
    funcionario = db.relationship('User', backref='agendamentos_funcionario', lazy=True)  # Alteração aqui

# Modelo de Folga (relacionamento com User)
class Folga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="Pendente")  # "Pendente", "Deferida"
    funcionario = db.relationship('User', backref=db.backref('folgas', lazy=True))

# Modelo de Banco de Horas (relacionamento com User)
class BancoDeHoras(db.Model):
    __tablename__ = 'banco_de_horas'

    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    horas = db.Column(db.Integer, nullable=False)  
    minutos = db.Column(db.Integer, nullable=False)  
    total_minutos = db.Column(db.Integer, default=0)  
    data_realizacao = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default="Horas a Serem Deferidas")
    data_criacao = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    motivo = db.Column(db.String(40), nullable=True)
    usufruido = db.Column(db.Boolean, default=False)  # NOVO CAMPO

    funcionario = db.relationship('User', backref='banco_de_horas')

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
    flash("Você saiu do sistema. Para acessá-lo, faça login novamente.", "success")
    return redirect(url_for('login'))


# Página Principal (Index)
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

# Rota Minahs Justificativas (Index)
@app.route('/minhas_justificativas')
@login_required
def minhas_justificativas():
    agendamentos = Agendamento.query.filter_by(funcionario_id=current_user.id).all()
    print(f"Agendamentos: {agendamentos}")  # Adicione isso para verificar os dados
    return render_template('minhas_justificativas.html', agendamentos=agendamentos)

# Rota Agendar
# Rota de Agendamento de Banco de Horas
@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        tipo_folga = request.form['tipo_folga']  # Tipo de folga (Simples, Banco de Horas, AB)
        data_folga = request.form['data']  # Data da folga
        motivo = request.form['motivo']  # Motivo da folga
        data_referencia = request.form.get('data_referencia')  # Obtém o valor de data_referencia
        
        # Se o tipo de folga for 'AB', vamos usar "AB" tanto em tipo_folga quanto em motivo
        if tipo_folga == 'AB':
            motivo = 'AB'  # Se for AB, coloca "Abonada" no campo motivo
            tipo_folga = 'AB'  # Define o tipo de folga como 'AB'
        
        # Converte a data de folga para o formato datetime
        try:
            data_folga = datetime.datetime.strptime(data_folga, '%Y-%m-%d').date()
        except ValueError:
            flash("Data inválida.", "danger")
            return redirect(url_for('agendar'))  # Redireciona para evitar o acúmulo de flash

        # Pega a data de referência, se fornecida (apenas para banco de horas)
        if tipo_folga == 'BH' and data_referencia:
            try:
                # Converte a data de referência para o formato datetime
                data_referencia = datetime.datetime.strptime(data_referencia, '%Y-%m-%d').date()
            except ValueError:
                flash("Data de referência inválida.", "danger")
                return redirect(url_for('agendar'))  # Redireciona para evitar o acúmulo de flash
        else:
            # Se não for tipo 'BH', a data de referência será None
            data_referencia = None

        try:
            horas = int(request.form['quantidade_horas']) if request.form['quantidade_horas'].strip() else 0
            minutos = int(request.form['quantidade_minutos']) if request.form['quantidade_minutos'].strip() else 0
        except ValueError:
            flash("Horas ou minutos inválidos.", "danger")
            return redirect(url_for('agendar'))  # Redireciona para evitar o acúmulo de flash

        
        # Converte as horas para minutos
        total_minutos = (horas * 60) + minutos
        
        # Verifica se o usuário tem horas suficientes no banco de horas
        usuario = User.query.get(current_user.id)  # Pega o usuário logado
        if usuario.banco_horas < total_minutos:
            flash("Você não possui horas suficientes no banco de horas para este agendamento.", "danger")
            return redirect(url_for('index'))

        # Criação do novo agendamento com tanto o motivo quanto o tipo de folga
        novo_agendamento = Agendamento(
            funcionario_id=current_user.id,  # Assumindo que o usuário está logado
            status='em_espera',  # Status inicial (agendamento em espera)
            data=data_folga,
            motivo=motivo,  # O 'motivo' agora está sendo setado corretamente
            tipo_folga=tipo_folga,  # 'tipo_folga' também recebe o valor
            data_referencia=data_referencia,  # Salva a data de referência apenas para banco de horas (BH)
            horas=horas,  # Salva as horas
            minutos=minutos  # Salva os minutos
        )

        # Adiciona o agendamento ao banco de dados sem descontar as horas
        try:
            db.session.add(novo_agendamento)
            db.session.commit()
            flash("Agendamento realizado com sucesso. A folga aguarda deferimento.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar agendamento: {str(e)}", "danger")
        
        # Após o processamento, exibe a mensagem de sucesso e redireciona para a página inicial
        return redirect(url_for('index'))  # Redireciona para a página inicial, com a mensagem de sucesso

    return render_template('agendar.html')

# Rota de Calendário de Folgas
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

# Rota Deletar Agendamento
@app.route('/delete_agendamento/<int:id>', methods=['POST'])
@login_required
def delete_agendamento(id):

    # Busca o agendamento pelo ID
    agendamento = Agendamento.query.get_or_404(id)

    # Verifica se o agendamento pertence ao funcionário logado
    if agendamento.funcionario_id == current_user.id:
        db.session.delete(agendamento)
        db.session.commit()
        flash('Agendamento excluído com sucesso.', 'success')
    else:
        flash('Você não tem permissão para excluir este agendamento.', 'danger')

    return redirect(url_for('minhas_justificativas'))


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
    if current_user.tipo == 'administrador':
        # Exibir folgas de todos os funcionários com status pendente ou em espera
        folgas = Agendamento.query.filter(Agendamento.status.in_(['em_espera', 'pendente'])).all()
    else:
        # Exibir apenas folgas do próprio funcionário com status pendente ou em espera
        folgas = Agendamento.query.filter(
            Agendamento.funcionario_id == current_user.id, 
            Agendamento.status.in_(['em_espera', 'pendente'])
        ).all()

    if request.method == 'POST':
        folga_id = request.form['folga_id']
        novo_status = request.form['status']
        folga = Agendamento.query.get(folga_id)

        if folga:
            # Verifica se a folga é do tipo "Banco de Horas"
            if folga.motivo == 'BH' and novo_status == 'deferido':
                # Se for Banco de Horas, vamos registrar as horas usufruídas e descontar
                total_minutos = (folga.horas * 60) + folga.minutos  # Total em minutos da folga
                usuario = User.query.get(folga.funcionario_id)  # Recupera o usuário

                # Verifica se o usuário tem horas suficientes no banco de horas
                if usuario.banco_horas >= total_minutos:
                    usuario.banco_horas -= total_minutos  # Subtrai do banco de horas

                    # Registra na tabela BancoDeHoras
                    novo_banco_horas = BancoDeHoras(
                        funcionario_id=usuario.id,
                        horas=folga.horas,
                        minutos=folga.minutos,
                        total_minutos=total_minutos,
                        data_realizacao=folga.data,
                        motivo=folga.motivo,  # Armazena o motivo da folga (Banco de Horas)
                        status="Deferida",
                        data_criacao=datetime.datetime.utcnow(),
                    )
                    db.session.add(novo_banco_horas)  # Adiciona o registro de Banco de Horas
                else:
                    flash("O funcionário não tem horas suficientes no banco de horas para este agendamento.", "danger")
                    return redirect(url_for('deferir_folgas'))  # Redireciona de volta para a página de deferimento

            # Atualiza o status da folga para o status desejado
            folga.status = novo_status
            db.session.commit()
            flash(f"A folga de {folga.funcionario.nome} foi {novo_status} com sucesso!", "success" if novo_status == 'deferido' else "danger")
        else:
            flash("Agendamento não encontrado.", "danger")

        # Atualiza os registros sem redirecionar
        if current_user.tipo == 'administrador':
            folgas = Agendamento.query.filter(Agendamento.status.in_(['em_espera', 'pendente'])).all()
        else:
            folgas = Agendamento.query.filter(
                Agendamento.funcionario_id == current_user.id, 
                Agendamento.status.in_(['em_espera', 'pendente'])
            ).all()

    return render_template('deferir_folgas.html', folgas=folgas)

# Rota de Histórico de Folgas
@app.route('/historico', methods=['GET'])
@login_required
def historico():
    # Contabiliza as folgas por tipo, considerando tanto agendamentos quanto folgas já deferidas
    folgas_contabilizadas = {
        'AB': 0,  # Abonada
        'BH': 0,  # Banco de Horas
        'DS': 0,  # Doação de Sangue
        'TRE': 0,  # TRE
        'FS': 0   # Falta Simples
    }
    # Contabiliza as folgas de agendamentos
    agendamentos = Agendamento.query.filter_by(funcionario_id=current_user.id).all()
    for agendamento in agendamentos:
        if agendamento.motivo in folgas_contabilizadas:
            folgas_contabilizadas[agendamento.motivo] += 1

    # Contabiliza as folgas que já foram deferidas
    folgas = Folga.query.filter_by(funcionario_id=current_user.id).all()
    for folga in folgas:
        if folga.motivo in folgas_contabilizadas:
            folgas_contabilizadas[folga.motivo] += 1

    # Passa os dados para o template
    return render_template('historico.html', folgas_contabilizadas=folgas_contabilizadas)

# Rota de Cadastro de Banco de Horas
@app.route('/banco_horas/cadastrar', methods=['GET', 'POST']) 
@login_required
def cadastrar_horas():
    if request.method == 'POST':
        # Recebe os dados do formulário
        nome = request.form['nome']
        registro = request.form['registro']
        quantidade_horas = int(request.form['quantidade_horas'])
        quantidade_minutos = int(request.form['quantidade_minutos'])
        data_realizacao = request.form['data_realizacao']
        motivo = request.form['motivo']  

        # Converte a data para o formato datetime
        try:
            data_realizacao = datetime.datetime.strptime(data_realizacao, '%Y-%m-%d').date()
        except ValueError:
            flash("Data inválida.", "danger")
            return redirect(url_for('cadastrar_horas'))

        # Calcula o total de minutos
        total_minutos = (quantidade_horas * 60) + quantidade_minutos

        # Criar novo registro no banco de horas (com status 'em espera')
        novo_banco_horas = BancoDeHoras(
            funcionario_id=current_user.id,
            horas=quantidade_horas,
            minutos=quantidade_minutos,
            total_minutos=total_minutos,
            data_realizacao=data_realizacao,
            motivo=motivo,
            status='Horas a Serem Deferidas'  # Garante que as horas começam em espera
        )

        try:
            db.session.add(novo_banco_horas)
            db.session.commit()
            flash("Banco de horas cadastrado com sucesso! Aguardando deferimento.", "success")
            return redirect(url_for('consultar_horas'))  
        
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao cadastrar banco de horas: {str(e)}", "danger")

    return render_template('cadastrar_horas.html', nome=current_user.nome, registro=current_user.registro)

# Rota de Principal Banco de Horas    
@app.route('/banco_horas')
@login_required
def banco_horas():
    # Verifique se o usuário é um administrador
    is_admin = current_user.tipo == 'administrador'
    return render_template('menu_banco_horas.html', is_admin=is_admin)

# Rota de Consulta de Horas
@app.route('/consultar_horas')
def consultar_horas():
    print(f"Usuário: {current_user}")  # Para verificar se o usuário está autenticado
    print(f"Banco de Horas: {getattr(current_user, 'banco_horas', 'NÃO DEFINIDO')}")  # Depuração
    
    registros = BancoDeHoras.query.filter_by(funcionario_id=current_user.id).all()
    
    horas_deferidas = 0
    minutos_deferidos = 0
    horas_em_espera = 0
    minutos_em_espera = 0
    
    for registro in registros:
        if registro.status == 'Deferido':
            horas_deferidas += registro.horas
            minutos_deferidos += registro.minutos
        elif registro.status == 'Horas a Serem Deferidas':
            horas_em_espera += registro.horas
            minutos_em_espera += registro.minutos
    
    horas_deferidas += minutos_deferidos // 60
    minutos_deferidos = minutos_deferidos % 60
    
    horas_em_espera += minutos_em_espera // 60
    minutos_em_espera = minutos_em_espera % 60

    horas_usufruidas = horas_deferidas + horas_em_espera
    minutos_usufruidos = minutos_deferidos + minutos_em_espera

    horas_usufruidas += minutos_usufruidos // 60
    minutos_usufruidos = minutos_usufruidos % 60

    # 🟢 Obtendo as horas a usufruir diretamente do usuário
    horas_a_usufruir = current_user.banco_horas // 60
    minutos_a_usufruir = current_user.banco_horas % 60

    return render_template('consultar_horas.html', 
                           registros=registros,
                           horas_deferidas=horas_deferidas,
                           minutos_deferidos=minutos_deferidos,
                           horas_em_espera=horas_em_espera,
                           minutos_em_espera=minutos_em_espera,
                           horas_usufruidas=horas_usufruidas,
                           minutos_usufruidos=minutos_usufruidos,
                           horas_a_usufruir=horas_a_usufruir,
                           minutos_a_usufruir=minutos_a_usufruir)

# Rota de Deferimento de Horas
@app.route('/banco_horas/deferir', methods=['GET', 'POST'])
@login_required
def deferir_horas():
    # Verifica se há registros com status 'Horas a Serem Deferidas' para deferir
    registros = BancoDeHoras.query.filter_by(status='Horas a Serem Deferidas').all()

    if request.method == 'POST':
        registro_id = request.form.get('registro_id')
        action = request.form.get('action')

        banco_horas = BancoDeHoras.query.filter_by(id=registro_id).first()

        if not banco_horas:
            flash("Registro não encontrado.", "danger")
            return redirect(url_for('deferir_horas'))

        if action == 'deferir':
            banco_horas.status = 'Deferido'

            # Adiciona as horas ao banco_horas do usuário apenas quando deferido
            funcionario = User.query.get(banco_horas.funcionario_id)
            if funcionario:
                funcionario.banco_horas += banco_horas.total_minutos  # Adiciona os minutos ao saldo do funcionário
            
            flash(f"Banco de horas de {banco_horas.funcionario.nome} deferido com sucesso!", "success")

        elif action == 'indeferir':
            banco_horas.status = 'Indeferido'
            flash(f"Banco de horas de {banco_horas.funcionario.nome} indeferido.", "danger")

        try:
            db.session.commit()
            # Atualiza a lista de registros, reconsultando o banco
            registros = BancoDeHoras.query.filter_by(status='Horas a Serem Deferidas').all()
            return render_template('deferir_horas.html', registros=registros)  # Renderiza a página com os novos registros
        
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar status: {str(e)}", "danger")
            return redirect(url_for('deferir_horas'))

    return render_template('deferir_horas.html', registros=registros)


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
