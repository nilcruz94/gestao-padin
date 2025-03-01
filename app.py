from flask import Flask, session, render_template, redirect, url_for, request, flash
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
import calendar
import datetime  # Mantém o módulo inteiro
from datetime import timedelta  # Importa só o timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://folgas_user:BLS6AMWRXX0vuFBM6q7oHKKwJChaK8dk@dpg-cuece7hopnds738g0usg-a.virginia-postgres.render.com/folgas_3tqr'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
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
    senha = db.Column(db.String(256), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'funcionario' ou 'administrador'
    status = db.Column(db.String(20), default='pendente')  # 'pendente', 'aprovado', 'rejeitado'
<<<<<<< HEAD

    # TREs
    tre_total = db.Column(db.Integer, default=0, nullable=False)  # TREs disponíveis
    tre_usufruidas = db.Column(db.Integer, default=0, nullable=False)  # TREs já utilizadas
=======
    # Adicionando os campos para TRE
    tre_total = db.Column(db.Integer, default=0)  # TREs a usufruir
    tre_usufruidas = db.Column(db.Integer, default=0)  # TREs já utilizadas
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)
    
    # Banco de horas em minutos
    banco_horas = db.Column(db.Integer, default=0, nullable=False)

    # Novos campos
    celular = db.Column(db.String(20), nullable=True)  # Aceita formato internacional +55 11 99999-9999
    data_nascimento = db.Column(db.Date, nullable=True)  # Armazena a data de nascimento

    # Relacionamento com Agendamento
    agendamentos = db.relationship('Agendamento', backref='user_funcionario', lazy=True)

class Agendamento(db.Model):
    __tablename__ = 'agendamento'
    
    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'pendente', 'deferido', 'indeferido'
    data = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(100), nullable=False)
<<<<<<< HEAD
    tipo_folga = db.Column(db.String(50))  # 'TRE', 'Férias', etc.
    data_referencia = db.Column(db.Date)  # Data base para cálculo, se necessário
    horas = db.Column(db.Integer, nullable=True)  
    minutos = db.Column(db.Integer, nullable=True)
    # Novos campos
    substituicao = db.Column(db.String(3), nullable=False, default="Não")  # "Sim" ou "Não"
    nome_substituto = db.Column(db.String(255), nullable=True)  # Nome do substituto (se houver)

    # Relacionamento com User
    funcionario = db.relationship('User', backref='agendamentos_funcionario', lazy=True)

    def is_tre_deferido(self):
        """Verifica se o agendamento é um TRE deferido."""
        return self.tipo_folga == "TRE" and self.status == "deferido"
=======
    tipo_folga = db.Column(db.String(50))  # Coluna tipo_folga
    data_referencia = db.Column(db.Date)  # Coluna data_referencia
    horas = db.Column(db.Integer, nullable=True)  # Coluna para horas
    minutos = db.Column(db.Integer, nullable=True)  # Coluna para minutos
    substituicao = db.Column(db.String(3), nullable=False, default="Não")  # 'Sim' ou 'Não'
    nome_substituto = db.Column(db.String(255), nullable=True)  # Nome do substituto (se houver)

    # Relacionamento com o modelo User
    funcionario = db.relationship('User', backref='agendamentos_funcionario', lazy=True)
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)

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

class EsquecimentoPonto(db.Model):
    __tablename__ = 'esquecimento_ponto'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    registro = db.Column(db.String(150), nullable=False)
    data_esquecimento = db.Column(db.Date, nullable=False)
    hora_primeira_entrada = db.Column(db.Time, nullable=True)
    hora_primeira_saida = db.Column(db.Time, nullable=True)
    hora_segunda_entrada = db.Column(db.Time, nullable=True)
    hora_segunda_saida = db.Column(db.Time, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relacionamento com User
    usuario = db.relationship('User', backref=db.backref('esquecimentos_ponto', lazy=True))

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        # Verifica se o usuário existe e a senha está correta
        if user and check_password_hash(user.senha, senha):
            # Verifica o status do usuário
            if user.status == 'pendente':
                flash('Seu registro está pendente de aprovação. Por favor, aguarde a confirmação do administrador.', 'warning')
                return render_template('login.html')
            elif user.status == 'rejeitado':  # Bloqueia acesso caso o status seja "rejeitado"
                flash('Seu acesso foi recusado. Contate um administrador.', 'danger')
                return render_template('login.html')
            
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos', 'danger')
    
    return render_template('login.html')

# Rota de Recuperar Senha
@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form['email']
        registro = request.form['registro']
        usuario = User.query.filter_by(email=email, registro=registro).first()
        
        if usuario:
            session['user_id'] = usuario.id  # Armazena temporariamente o ID do usuário
            return redirect(url_for('redefinir_senha'))
        else:
            flash('Usuário não encontrado. Verifique os dados e tente novamente.', 'danger')
    
    return render_template('recuperar_senha.html')

# Rota de Redefinir Senha
@app.route('/redefinir_senha', methods=['GET', 'POST'])
def redefinir_senha():
    if 'user_id' not in session:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('recuperar_senha'))
    
    if request.method == 'POST':
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']
        
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem. Tente novamente.', 'danger')
        else:
            usuario = User.query.get(session['user_id'])
            # Utilizando generate_password_hash para gerar o hash da nova senha
            usuario.senha = generate_password_hash(nova_senha)
            db.session.commit()
            session.pop('user_id', None)  # Remove o usuário da sessão após redefinir
            flash('Senha redefinida com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('redefinir_senha.html')

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
@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        tipo_folga = request.form['tipo_folga']  # Tipo de folga (Simples, Banco de Horas, AB)
        data_folga = request.form['data']  # Data da folga
        motivo = request.form['motivo']  # Motivo da folga
        data_referencia = request.form.get('data_referencia')  # Obtém o valor de data_referencia

<<<<<<< HEAD
        # Novo campo: Substituição
        substituicao = request.form.get('substituicao', 'Não')  # 'Sim' ou 'Não' (padrão: 'Não')
        nome_substituto = request.form.get('nome_substituto') if substituicao == 'Sim' else None  # Apenas se 'Sim'

        if tipo_folga == 'AB':
            motivo = 'AB'  # Se for AB, coloca "Abonada" no campo motivo
            tipo_folga = 'AB'  # Define o tipo de folga como 'AB'
=======
        # Captura os valores de substituição
        substituicao = request.form.get("havera_substituicao")  # "Sim" ou "Não"
        nome_substituto = request.form.get("nome_substituto")  # Nome do substituto

        # Se não houver substituição, o nome do substituto deve ser None
        if substituicao == "Não":
            nome_substituto = None

        # Se o tipo de folga for 'AB', vamos usar "AB" tanto em tipo_folga quanto em motivo
        if tipo_folga == 'AB':
            motivo = 'AB'
            tipo_folga = 'AB'
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)

        # Converte a data de folga para o formato datetime
        try:
            data_folga = datetime.datetime.strptime(data_folga, '%Y-%m-%d').date()
        except ValueError:
            flash("Data inválida.", "danger")
            return redirect(url_for('agendar'))

<<<<<<< HEAD
=======
        # Verifica se já existe um 'AB' deferido no mês
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)
        if motivo == 'AB':
            agendamento_existente = Agendamento.query.filter(
                Agendamento.funcionario_id == current_user.id,
                Agendamento.motivo == 'AB',
                db.extract('year', Agendamento.data) == data_folga.year,
                db.extract('month', Agendamento.data) == data_folga.month
            ).first()

            if agendamento_existente and agendamento_existente.status != 'indeferido':
                flash("Você já possui um agendamento 'AB' aprovado ou em análise neste mês.", "danger")
                return render_template('agendar.html')

<<<<<<< HEAD
=======
        # Verifica limite de 6 folgas 'AB' deferidas no ano
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)
        agendamentos_ab_deferidos = Agendamento.query.filter(
            Agendamento.funcionario_id == current_user.id,
            Agendamento.motivo == 'AB',
            db.extract('year', Agendamento.data) == data_folga.year,
            Agendamento.status == 'deferido'
        ).count()

        if agendamentos_ab_deferidos >= 6:
            flash("Você já atingiu o limite de 6 folgas 'AB' deferidas neste ano.", "danger")
            return render_template('agendar.html')

<<<<<<< HEAD
=======
        # Converte data de referência, se for Banco de Horas
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)
        if tipo_folga == 'BH' and data_referencia:
            try:
                data_referencia = datetime.datetime.strptime(data_referencia, '%Y-%m-%d').date()
            except ValueError:
                flash("Data de referência inválida.", "danger")
                return redirect(url_for('agendar'))
        else:
            data_referencia = None

        # Captura horas e minutos
        try:
            horas = int(request.form['quantidade_horas']) if request.form['quantidade_horas'].strip() else 0
            minutos = int(request.form['quantidade_minutos']) if request.form['quantidade_minutos'].strip() else 0
        except ValueError:
            flash("Horas ou minutos inválidos.", "danger")
            return redirect(url_for('agendar'))

<<<<<<< HEAD
        total_minutos = (horas * 60) + minutos
        
=======
        # Converte horas para minutos
        total_minutos = (horas * 60) + minutos

        # Verifica se o usuário tem saldo suficiente no banco de horas
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)
        usuario = User.query.get(current_user.id)
        if usuario.banco_horas < total_minutos:
            flash("Você não possui horas suficientes no banco de horas para este agendamento.", "danger")
            return redirect(url_for('index'))

<<<<<<< HEAD
        # Criação do novo agendamento com substituição
=======
        # Criar e salvar no banco
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)
        novo_agendamento = Agendamento(
            funcionario_id=current_user.id,
            status='em_espera',
            data=data_folga,
            motivo=motivo,
            tipo_folga=tipo_folga,
            data_referencia=data_referencia,
            horas=horas,
            minutos=minutos,
            substituicao=substituicao,
<<<<<<< HEAD
            nome_substituto=nome_substituto  # Apenas se 'Sim'
=======
            nome_substituto=nome_substituto  # Agora o nome do substituto é salvo corretamente
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)
        )

        try:
            db.session.add(novo_agendamento)
            db.session.commit()
            flash("Agendamento realizado com sucesso. A folga aguarda deferimento.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar agendamento: {str(e)}", "danger")
<<<<<<< HEAD
        
        return redirect(url_for('index'))
    
=======

        return redirect(url_for('index'))

>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)
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
        
        # Se o campo 'tipo' não for enviado, atribua um valor padrão (por exemplo, 'user')
        tipo = request.form.get('tipo', 'user')  # Aqui, 'user' é o valor padrão

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

        # Criação do novo usuário com o status 'pendente', aguardando aprovação
        new_user = User(
            nome=nome, 
            registro=registro, 
            email=email, 
            senha=senha_hash, 
            tipo=tipo, 
            status='pendente'  # Novo campo para controlar a aprovação
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Usuário registrado com sucesso. Aguardando aprovação do administrador.', 'info')
        return redirect(url_for('login'))

    return render_template('register.html')


# Rota Aprovar Usuarios
@app.route('/aprovar_usuarios', methods=['GET', 'POST'])
@login_required
def aprovar_usuarios():
    # Verifica se o usuário logado é administrador
    if current_user.tipo != 'administrador':
        flash('Você não tem permissão para acessar essa página.', 'danger')
        return redirect(url_for('index'))  # Redireciona para a página inicial ou outra página apropriada

    # Exibe todos os usuários com status 'pendente'
    usuarios_pendentes = User.query.filter_by(status='pendente').all()

    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')  # Recupera o ID do usuário a ser aprovado ou recusado
        acao = request.form.get('acao')  # Recupera a ação do formulário (aprovar ou recusar)

        # Verifica se a ação foi recebida corretamente
        if acao is None:
            flash('Ação não especificada', 'danger')
            return redirect(url_for('aprovar_usuarios'))

        usuario = User.query.get(usuario_id)  # Busca o usuário pelo ID
        if usuario:
            if acao == 'aprovar':
                usuario.status = 'aprovado'  # Altera o status do usuário para 'aprovado'
                flash(f'Usuário {usuario.nome} aprovado com sucesso!', 'success')
            elif acao == 'recusar':
                usuario.status = 'rejeitado'  # Altera o status do usuário para 'rejeitado'
                flash(f'Usuário {usuario.nome} recusado.', 'danger')

            db.session.commit()  # Salva as alterações no banco de dados

        return redirect(url_for('aprovar_usuarios'))  # Redireciona de volta para a página de aprovação de usuários

    # Retorna o template com a lista de usuários pendentes
    return render_template('aprovar_usuarios.html', usuarios=usuarios_pendentes)


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


@app.route('/relatar_esquecimento', methods=['GET', 'POST'])
@login_required  # Garante que o usuário esteja logado
def relatar_esquecimento():
    if request.method == 'POST':
        data_esquecimento = request.form.get('data_esquecimento')
        hora_primeira_entrada = request.form.get('hora_primeira_entrada') or None
        hora_primeira_saida = request.form.get('hora_primeira_saida') or None
        hora_segunda_entrada = request.form.get('hora_segunda_entrada') or None
        hora_segunda_saida = request.form.get('hora_segunda_saida') or None

        # Verifica se ao menos um horário foi preenchido
        if not any([hora_primeira_entrada, hora_primeira_saida, hora_segunda_entrada, hora_segunda_saida]):
            flash(('danger', 'Você deve preencher ao menos um campo de horário.'))
            return redirect(url_for('relatar_esquecimento'))

        # Criando o novo registro no banco de dados
        # Ajuste na conversão da data
        novo_esquecimento = EsquecimentoPonto(
            user_id=current_user.id,
            nome=current_user.nome,
            registro=current_user.registro,
            data_esquecimento=datetime.datetime.strptime(data_esquecimento, '%Y-%m-%d').date(),
            hora_primeira_entrada=hora_primeira_entrada,
            hora_primeira_saida=hora_primeira_saida,
            hora_segunda_entrada=hora_segunda_entrada,
            hora_segunda_saida=hora_segunda_saida
        )

        db.session.add(novo_esquecimento)
        db.session.commit()
        flash(('Registro de esquecimento enviado com sucesso!'))
        return redirect(url_for('relatar_esquecimento'))

    return render_template('relatar_esquecimento.html')

from datetime import date, timedelta
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

@app.route('/relatorio_ponto')
@login_required
def relatorio_ponto():
    if current_user.tipo != 'administrador':  # Apenas administradores podem acessar
        flash("Acesso negado.", "danger")
        return redirect(url_for('index'))

    # Obtém o mês selecionado a partir da query string (GET)
    mes_selecionado = request.args.get('mes', type=int)

    # Lista vazia para os registros filtrados
    registros = []
    periodo_inicio = periodo_fim = None  # Inicializa como None para evitar erro

    if mes_selecionado:  # Apenas se um mês foi selecionado
        ano_atual = datetime.datetime.now().year  # Obtém o ano atual
        mes_anterior = 12 if mes_selecionado == 1 else mes_selecionado - 1
        ano_mes_anterior = ano_atual - 1 if mes_selecionado == 1 else ano_atual

        # Define o período correto de busca (10 do mês anterior até 09 do mês atual)
        periodo_inicio = datetime.datetime(ano_mes_anterior, mes_anterior, 10)
        periodo_fim = datetime.datetime(ano_atual, mes_selecionado, 9, 23, 59, 59)  # Final do dia 09

        # Buscar os agendamentos dentro do período
        agendamentos = Agendamento.query.filter(
            Agendamento.data >= periodo_inicio,
            Agendamento.data <= periodo_fim
        ).join(User).order_by(User.nome.asc()).all()

        # Buscar os esquecimentos dentro do período
        esquecimentos = EsquecimentoPonto.query.filter(
            EsquecimentoPonto.data_esquecimento >= periodo_inicio,
            EsquecimentoPonto.data_esquecimento <= periodo_fim
        ).join(User).order_by(User.nome.asc()).all()

        # Adiciona os resultados à lista `registros`
        for agendamento in agendamentos:
            registros.append({
                'usuario': agendamento.funcionario,  
                'tipo': 'Agendamento',
                'data': agendamento.data,
                'motivo': agendamento.motivo,
                'horapentrada': 'N/A',
                'horapsaida': 'N/A',
                'horasentrada': 'N/A',
                'horassaida': 'N/A',
            })

        for esquecimento in esquecimentos:
            registros.append({
                'usuario': esquecimento.usuario,  
                'tipo': 'Esquecimento de Ponto',
                'data': esquecimento.data_esquecimento,
                'motivo': 'N/A',
                'horapentrada': esquecimento.hora_primeira_entrada,
                'horapsaida': esquecimento.hora_primeira_saida,
                'horasentrada': esquecimento.hora_segunda_entrada,
                'horassaida': esquecimento.hora_segunda_saida,
            })

    return render_template(
        'relatorio_ponto.html',
        registros=registros,
        mes_selecionado=mes_selecionado,
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim
    )

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
            usuario = User.query.get(folga.funcionario_id)  # Recupera o usuário
<<<<<<< HEAD

            # 🟢 Caso seja TRE e for deferida, incrementamos TREs usufruídas e decrementamos TREs a usufruir
            if folga.motivo == 'TRE' and novo_status == 'deferido':
                if usuario.tre_total > 0:  # Evita número negativo
                    usuario.tre_usufruidas += 1  # Adiciona uma TRE usufruída
                    usuario.tre_total -= 1  # Remove uma TRE disponível

            # 🟢 Caso seja Banco de Horas (BH), verificamos e subtraímos do banco de horas
            elif folga.motivo == 'BH' and novo_status == 'deferido':
=======
            
            # Verifica se a folga é do tipo "Banco de Horas"
            if folga.motivo == 'BH' and novo_status == 'deferido':
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)
                total_minutos = (folga.horas * 60) + folga.minutos  # Total em minutos da folga
                
                if usuario.banco_horas >= total_minutos:
                    usuario.banco_horas -= total_minutos  # Subtrai do banco de horas

                    # Registra na tabela BancoDeHoras
                    novo_banco_horas = BancoDeHoras(
                        funcionario_id=usuario.id,
                        horas=folga.horas,
                        minutos=folga.minutos,
                        total_minutos=total_minutos,
                        data_realizacao=folga.data,
                        motivo=folga.motivo,
                        status="Deferida",
                        data_criacao=datetime.datetime.utcnow(),
                    )
                    db.session.add(novo_banco_horas)  # Adiciona o registro de Banco de Horas
                else:
                    flash("O funcionário não tem horas suficientes no banco de horas para este agendamento.", "danger")
                    return redirect(url_for('deferir_folgas'))  # Redireciona de volta para a página de deferimento

            # Se a folga for TRE e estiver sendo deferida, atualiza os campos no usuário
            if folga.motivo == 'TRE' and novo_status == 'deferido':
                usuario.tre_total -= 1
                usuario.tre_usufruidas += 1

            # Atualiza o status da folga para o status desejado
            folga.status = novo_status
<<<<<<< HEAD
            db.session.commit()  # 🔹 Salva todas as alterações no banco

            flash(f"A folga de {folga.funcionario.nome} foi {novo_status} com sucesso!", "success" if novo_status == 'deferido' else "danger")
=======

            try:
                db.session.commit()
                flash(f"A folga de {folga.funcionario.nome} foi {novo_status} com sucesso!", "success" if novo_status == 'deferido' else "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao atualizar folga: {str(e)}", "danger")
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)
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

@app.route('/historico', methods=['GET'])
@login_required
def historico():
    # Obtém os dados do usuário logado
    usuario = User.query.get(current_user.id)

    # Inicializa as contagens de folgas
    folgas_contabilizadas = {
        'AB': 0,  # Abonada
        'BH': 0,  # Banco de Horas
        'DS': 0,  # Doação de Sangue
        'TRE': 0,  # TREs restantes (será atualizado abaixo)
        'FS': 0   # Falta Simples
    }
<<<<<<< HEAD

    # Contabiliza as folgas de agendamentos deferidos
    agendamentos = Agendamento.query.filter_by(funcionario_id=current_user.id, status="deferido").all()
=======
    
    # Contabiliza as folgas de agendamentos
    agendamentos = Agendamento.query.filter_by(funcionario_id=current_user.id).all()
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)
    for agendamento in agendamentos:
        if agendamento.motivo in folgas_contabilizadas:
            folgas_contabilizadas[agendamento.motivo] += 1

    # Contabiliza as folgas já deferidas
    folgas = Folga.query.filter_by(funcionario_id=current_user.id).all()
    for folga in folgas:
        if folga.motivo in folgas_contabilizadas:
            folgas_contabilizadas[folga.motivo] += 1

<<<<<<< HEAD
    # 🔹 Obtém os valores corretos do banco, garantindo que não sejam None
    total_tres = usuario.tre_total if usuario.tre_total is not None else 0
    tres_usufruidas = usuario.tre_usufruidas if usuario.tre_usufruidas is not None else 0

    # 🔹 TREs restantes (não pode ser negativo)
    folgas_contabilizadas['TRE_total'] = total_tres
    folgas_contabilizadas['TRE_usufruidas'] = tres_usufruidas
    folgas_contabilizadas['TRE'] = max(total_tres - tres_usufruidas, 0)
=======
    # Obtendo os valores de TREs do banco de dados
    tre_total = current_user.tre_total  # TREs a Usufruir
    tre_usufruidas = current_user.tre_usufruidas  # TREs já usadas
>>>>>>> ee0a3e7 (substitutos, relatorio de ponto, esquecimento.)

    # Passa os dados para o template
    return render_template(
        'historico.html',
        folgas_contabilizadas=folgas_contabilizadas,
        tre_total=tre_total,
        tre_usufruidas=tre_usufruidas
    )

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

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    usuario = current_user
    
    if request.method == 'POST':
        # Recupera os dados do formulário
        celular = request.form['celular']
        data_nascimento = request.form['data_nascimento']
        
        # Atualiza o usuário com os novos dados
        usuario.celular = celular
        usuario.data_nascimento = data_nascimento
        
        # Salva as alterações no banco de dados
        try:
            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar o perfil. Tente novamente mais tarde.', 'danger')
        
        return redirect(url_for('perfil'))
    
    return render_template('perfil.html', usuario=usuario)

@app.route('/criar_banco')
def criar_banco():
    try:
        db.create_all()  # Tenta criar as tabelas no banco
        return "Banco de dados criado com sucesso!"
    except Exception as e:
        return f"Erro ao criar o banco: {str(e)}"
    
# Login Manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run(debug=True)
