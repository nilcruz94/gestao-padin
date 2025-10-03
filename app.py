from flask import Flask, session, render_template, redirect, url_for, request, flash, make_response, abort, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import calendar
import datetime   # Mantém o módulo inteiro
from datetime import timedelta  # Importa só o timedelta
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ===========================================
# Configuração principal do app
# ===========================================
app = Flask(__name__)

# Config Banco PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://folgas_user:BLS6AMWRXX0vuFBM6q7oHKKwJChaK8dk@'
    'dpg-cuece7hopnds738g0usg-a.virginia-postgres.render.com/folgas_3tqr'
)
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
app.config['SECRET_KEY'] = 'supersecretkey'

# Config Uploads
UPLOAD_FOLDER = "uploads/tre"
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ===========================================
# Extensões
# ===========================================
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ===========================================
# Configurações de Email (SMTP)
# ===========================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "nilcr94@gmail.com"
SMTP_PASS = "xboztvmzwskygzzh"   # 🔒 Melhor usar variável de ambiente depois!

# Modelo User (Funcionario e Administrador)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    registro = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    senha = db.Column(db.String(256), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'funcionario' ou 'administrador'
    status = db.Column(db.String(20), default='pendente')  # 'pendente', 'aprovado', 'rejeitado'
    # Adicionando os campos para TRE
    tre_total = db.Column(db.Integer, default=0)  # TREs a usufruir
    tre_usufruidas = db.Column(db.Integer, default=0)  # TREs já utilizadas
    cargo = db.Column(db.String(100), nullable=True)  # Este campo pode ser preenchido depois
    
    # Banco de horas em minutos
    banco_horas = db.Column(db.Integer, default=0, nullable=False)

    # Novos campos
    celular = db.Column(db.String(20), nullable=True)  # Aceita formato internacional +55 11 99999-9999
    data_nascimento = db.Column(db.Date, nullable=True)  # Armazena a data de nascimento

    # Novos campos
    cpf = db.Column(db.String(14), nullable=False, unique=True)  # Exemplo: 123.456.789-00
    rg = db.Column(db.String(20), nullable=False, unique=True)  # Exemplo: 12.345.678-9 ou MG-12.345.678
    data_emissao_rg = db.Column(db.Date, nullable=True)
    orgao_emissor = db.Column(db.String(20), nullable=True)  # Exemplo: SSP-SP, DETRAN, etc.

    # Graduação diretamente como String
    graduacao = db.Column(db.String(50), nullable=True)  # Ex: 'Técnico', 'Mestrado', 'Doutorado'
    # Termos
    aceitou_termo = db.Column(db.Boolean, default=False)
    versao_termo = db.Column(db.String(20), default=None)  # Ex: '2025-07-25'

    # Relacionamento com Agendamento
    agendamentos = db.relationship('Agendamento', backref='user_funcionario', lazy=True)

class Agendamento(db.Model):
    __tablename__ = 'agendamento'
    
    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(100), nullable=False)
    tipo_folga = db.Column(db.String(50)) 
    data_referencia = db.Column(db.Date) 
    horas = db.Column(db.Integer, nullable=True) 
    minutos = db.Column(db.Integer, nullable=True) 
    substituicao = db.Column(db.String(3), nullable=False, default="Não")  
    nome_substituto = db.Column(db.String(255), nullable=True)  
    # Novo campo
    conferido = db.Column(db.Boolean, default=False)

    # Relacionamento com o modelo User
    funcionario = db.relationship('User', backref='agendamentos_funcionario', lazy=True)

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
    usufruido = db.Column(db.Boolean, default=False) 

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
    conferido = db.Column(db.Boolean, default=False)

    
    motivo = db.Column(db.Text, nullable=True)

    usuario = db.relationship('User', backref=db.backref('esquecimentos_ponto', lazy=True))

# =========================
# TRE (com workflow de aprovação)
# =========================
class TRE(db.Model):
    __tablename__ = 'tre'

    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # enviado pelo usuário
    dias_folga = db.Column(db.Integer, nullable=False)
    arquivo_pdf = db.Column(db.String(255), nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # workflow de aprovação
    status = db.Column(db.String(20), default='pendente')  # 'pendente' | 'deferida' | 'indeferida'
    dias_validados = db.Column(db.Integer, nullable=True)  # admin pode corrigir os dias
    parecer_admin = db.Column(db.Text, nullable=True)
    validado_em = db.Column(db.DateTime, nullable=True)
    validado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # admin

    # >>> RELACIONAMENTOS <<<
    funcionario = db.relationship(
        'User',
        backref=db.backref('tres', lazy=True),
        foreign_keys=[funcionario_id],
        lazy=True
    )
    # Quem validou (admin)
    validador = db.relationship(
        'User',
        backref=db.backref('tres_validadas', lazy=True),
        foreign_keys=[validado_por_id],
        lazy=True
    )

def enviar_email(destinatario, assunto, mensagem_html, mensagem_texto=None):
        """
        Envia um e-mail com mensagem HTML. Opcionalmente, pode incluir uma alternativa em texto puro.
        """
        msg = MIMEMultipart("alternative")
        msg['From'] = SMTP_USER
        msg['To'] = destinatario
        msg['Subject'] = assunto

        # Se não fornecer a versão em texto, cria uma simples a partir do HTML
        if not mensagem_texto:
            mensagem_texto = "Por favor, visualize este e-mail em um cliente que suporte HTML."

        # Cria as partes do e-mail
        parte_texto = MIMEText(mensagem_texto, 'plain')
        parte_html = MIMEText(mensagem_html, 'html')

        msg.attach(parte_texto)
        msg.attach(parte_html)
        
        try:
            servidor = smtplib.SMTP( SMTP_SERVER, SMTP_PORT)
            servidor.starttls()
            servidor.login(SMTP_USER, SMTP_PASS)  
            servidor.send_message(msg)
            servidor.quit()
            print("E-mail enviado com sucesso!")
        except Exception as e:
            print("Erro ao enviar e-mail:", e)

VERSAO_ATUAL_TERMO = '2025-07-25'  # Atualize aqui quando mudar o termo

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            if user.status == 'pendente':
                flash('Seu registro está pendente de aprovação. Por favor, aguarde a confirmação do administrador.', 'warning')
                return render_template('login.html')
            elif user.status == 'rejeitado':
                flash('Seu acesso foi recusado. Contate um administrador.', 'danger')
                return render_template('login.html')

            login_user(user)

            # Verifica se o usuário já aceitou a versão atual do termo
            if not user.aceitou_termo or user.versao_termo != VERSAO_ATUAL_TERMO:
                return redirect(url_for('termo_uso'))

            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos', 'danger')

    return render_template('login.html')

CURRENT_TERMO = "2025-07-25"

@app.route('/termo_uso', methods=['GET', 'POST'])
@login_required
def termo_uso():
    if request.method == 'POST':
        acao = request.form.get('acao')

        if acao == 'aceito':
            current_user.aceitou_termo = True
            current_user.versao_termo = CURRENT_TERMO
            db.session.commit()
            flash("Termo aceito com sucesso.", "success")
            return redirect(url_for('index'))

        elif acao == 'nao_aceito':
            flash("Você precisa aceitar o termo para usar o sistema.", "danger")
            logout_user()
            return redirect(url_for('login'))

    # Se já aceitou a versão atual, redireciona para index
    if current_user.aceitou_termo and current_user.versao_termo == CURRENT_TERMO:
        return redirect(url_for('index'))

    return render_template('termo_uso.html', termo_versao=CURRENT_TERMO)


CURRENT_TERMO = "2025-07-25"

@app.route('/aceitar_termo', methods=['POST'])
@login_required
def aceitar_termo():
    current_user.aceitou_termo = True
    current_user.versao_termo = CURRENT_TERMO
    # Se quiser salvar a data do aceite, pode criar e usar outro campo no modelo, ex: termo_aceite_data
    db.session.commit()
    flash('Termo de uso aceito com sucesso.', 'success')
    return redirect(url_for('index'))


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

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    usuario = current_user  # Obtém o usuário logado

    # Lista dos campos obrigatórios que precisam ser verificados
    campos_obrigatorios = {
        "Celular": usuario.celular,
        "Data de Nascimento": usuario.data_nascimento,
        "CPF": usuario.cpf,
        "RG": usuario.rg,
        "Cargo": usuario.cargo  # Verifica o campo cargo também
    }

    # Filtra os campos obrigatórios que estão vazios
    campos_pendentes = [campo for campo, valor in campos_obrigatorios.items() if not valor]

    # Se houver campos obrigatórios pendentes, redireciona para a página de preenchimento
    if campos_pendentes:
        # Gera uma mensagem com os campos obrigatórios faltantes
        mensagem = f"""
            Atenção! Complete seu perfil. Os seguintes campos estão em branco: {', '.join(campos_pendentes)}.
            <a href="{url_for('informar_dados')}" class="link-perfil">Clique aqui para preenchê-los</a>.
        """
        flash(mensagem, "warning")  # Flash message para mostrar a mensagem de alerta
        return redirect(url_for('informar_dados'))  # Redireciona para a página de preencher os dados obrigatórios

    # Lista dos campos opcionais que não são obrigatórios
    campos_opcionais = {
        "Data de Emissão do RG": usuario.data_emissao_rg,
        "Órgão Emissor": usuario.orgao_emissor,
        "Graduação": usuario.graduacao,
    }

    # Verifica se os campos opcionais estão vazios e exibe uma mensagem de aviso
    campos_faltantes_opcionais = [campo for campo, valor in campos_opcionais.items() if not valor]

    # Se houver campos opcionais faltando, exibe uma mensagem
    if campos_faltantes_opcionais:
        mensagem_opcional = f"""
            Você pode completar seu perfil com os seguintes dados: {', '.join(campos_faltantes_opcionais)}.
            <a href="{url_for('perfil')}" class="link-perfil">Clique aqui para preenchê-los</a>.
        """
        flash(mensagem_opcional, "info")  # Flash message para campos opcionais

    return render_template('index.html', usuario=usuario)

# Rota Minhas Justificativas (Index)
@app.route('/minhas_justificativas')
@login_required
def minhas_justificativas():
    agendamentos = Agendamento.query.filter_by(funcionario_id=current_user.id).all()
    print(f"Agendamentos: {agendamentos}")  # Adicione isso para verificar os dados
    return render_template('minhas_justificativas.html', agendamentos=agendamentos)

@app.route('/agendar', methods=['GET', 'POST'])
@login_required
def agendar():
    if request.method == 'POST':
        # 🔹 Mantém o saldo de TRE sempre correto antes de validar
        sync_tre_user(current_user.id)

        tipo_folga       = request.form['tipo_folga']         # Código do motivo: 'AB', 'BH', 'DS', 'TRE', 'FS'
        data_folga       = request.form['data']               # Data da folga
        motivo           = request.form['motivo']             # Mesmo código acima
        data_referencia  = request.form.get('data_referencia')# Para Banco de Horas

        substituicao     = request.form.get("havera_substituicao")  # "Sim" ou "Não"
        nome_substituto  = request.form.get("nome_substituto")

        if substituicao == "Não":
            nome_substituto = None

        if tipo_folga == 'AB':
            motivo     = 'AB'
            tipo_folga = 'AB'

        # Validação específica para TRE: verifica se tipo_folga ou motivo são "TRE"
        if tipo_folga == 'TRE' or motivo == 'TRE':
            usuario = User.query.get(current_user.id)  # Buscar o usuário atualizado (já sincronizado)
            # Saldo real
            tre_total = int(usuario.tre_total or 0)
            tre_usuf = int(usuario.tre_usufruidas or 0)
            tre_restantes = max(tre_total - tre_usuf, 0)

            # (Opcional, mas recomendado) Evitar "overbooking":
            # Se já existem solicitações TRE em análise, desconta do saldo disponível para nova solicitação
            pedidos_abertos = (
                Agendamento.query
                .filter(
                    Agendamento.funcionario_id == current_user.id,
                    Agendamento.motivo == 'TRE',
                    Agendamento.status.in_( ['em_espera', 'pendente'] )
                )
                .count()
            )
            saldo_disponivel_para_solicitar = tre_restantes - pedidos_abertos

            if saldo_disponivel_para_solicitar <= 0:
                flash("Você não possui TREs disponíveis para agendar no momento.", "danger")
                return render_template('agendar.html')

        # mapeia o código para descrição legível
        descricao_motivo = {
            'AB':  'Abonada',
            'BH':  'Banco de Horas',
            'DS':  'Doação de Sangue',
            'TRE': 'TRE',
            'FS':  'Falta Simples'
        }.get(motivo, 'Agendamento')

        try:
            data_folga = datetime.datetime.strptime(data_folga, '%Y-%m-%d').date()
        except ValueError:
            flash("Data inválida.", "danger")
            return redirect(url_for('agendar'))

        if motivo == 'AB':
            # Verifica se já existe AB no mesmo mês
            agendamento_existente = Agendamento.query.filter(
                Agendamento.funcionario_id == current_user.id,
                Agendamento.motivo == 'AB',
                db.extract('year', Agendamento.data) == data_folga.year,
                db.extract('month', Agendamento.data) == data_folga.month
            ).first()
            if agendamento_existente and agendamento_existente.status != 'indeferido':
                flash("Você já possui um agendamento 'AB' aprovado ou em análise neste mês.", "danger")
                return render_template('agendar.html')

            # Verifica o limite anual de AB deferidas
            agendamentos_ab_deferidos = Agendamento.query.filter(
                Agendamento.funcionario_id == current_user.id,
                Agendamento.motivo == 'AB',
                db.extract('year', Agendamento.data) == data_folga.year,
                Agendamento.status == 'deferido'
            ).count()

            if agendamentos_ab_deferidos >= 6:
                flash("Você já atingiu o limite de 6 folgas 'AB' deferidas neste ano.", "danger")
                return render_template('agendar.html')

        if tipo_folga == 'BH' and data_referencia:
            try:
                data_referencia = datetime.datetime.strptime(data_referencia, '%Y-%m-%d').date()
            except ValueError:
                flash("Data de referência inválida.", "danger")
                return redirect(url_for('agendar'))
        else:
            data_referencia = None

        try:
            horas   = int(request.form['quantidade_horas'])   if request.form['quantidade_horas'].strip()   else 0
            minutos = int(request.form['quantidade_minutos']) if request.form['quantidade_minutos'].strip() else 0
        except ValueError:
            flash("Horas ou minutos inválidos.", "danger")
            return redirect(url_for('agendar'))

        total_minutos = (horas * 60) + minutos
        usuario = User.query.get(current_user.id)

        if tipo_folga == 'BH' and usuario.banco_horas < total_minutos:
            flash("Você não possui horas suficientes no banco de horas para este agendamento.", "danger")
            return redirect(url_for('index'))

        novo_agendamento = Agendamento(
            funcionario_id   = current_user.id,
            status           = 'em_espera',
            data             = data_folga,
            motivo           = motivo,
            tipo_folga       = tipo_folga,
            data_referencia  = data_referencia,
            horas            = horas,
            minutos          = minutos,
            substituicao     = substituicao,
            nome_substituto  = nome_substituto
        )

        try:
            # salva o agendamento
            db.session.add(novo_agendamento)
            db.session.commit()

            # prepara dados para o e-mail
            assunto  = "E.M José Padin Mouta – Confirmação de Agendamento"
            nome     = current_user.nome
            data_str = novo_agendamento.data.strftime('%d/%m/%Y')

            mensagem_html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5;">
                <p>Prezado(a) Senhor(a) <strong>{nome}</strong>,</p>
                <p>
                  Sua solicitação de <strong>{descricao_motivo}</strong> para o dia
                  <strong>{data_str}</strong> foi registrada com sucesso e encontra-se
                  em <strong style="color: #FFA500;">EM ESPERA</strong>, aguardando análise da direção.
                </p>
                <p>Você será notificado assim que houver uma decisão.</p>
                <br>
                <p>Atenciosamente,</p>
                <p>
                  Nilson Cruz<br>
                  Secretário da Unidade Escolar<br>
                  E.M José Padin Mouta
                </p>
              </body>
            </html>
            """

            mensagem_texto = f"""Prezado(a) Senhor(a) {nome},

Sua solicitação de {descricao_motivo} para o dia {data_str} foi registrada com sucesso e encontra-se EM ESPERA, aguardando análise da direção.

Você será notificado assim que houver uma decisão.

Atenciosamente,

Nilson Cruz
Secretário da Unidade Escolar
E.M José Padin Mouta
"""

            # envia o e-mail
            enviar_email(current_user.email, assunto, mensagem_html, mensagem_texto)

            flash("Agendamento realizado com sucesso. Você receberá um e-mail de confirmação.", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar agendamento: {str(e)}", "danger")

        return redirect(url_for('index'))

    return render_template('agendar.html')

# Rota de Calendário de Folgas
@app.route('/calendario', methods=['GET', 'POST'])
@app.route('/calendario/<int:year>/<int:month>', methods=['GET', 'POST'])
@login_required
def calendario(year=None, month=None):
    # Intervalo de 10 anos a partir de 2025
    inicio_ano = 2025
    fim_ano = inicio_ano + 9  # 10 anos

    # Se não passar ano/mês, cai no mês atual
    if not year or not month:
        hoje = datetime.date.today()
        year = hoje.year
        month = hoje.month

    # Ajuste para manter mês entre 1 e 12
    while month < 1:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1

    # Calcular anterior e próximo
    prev_month = 12 if month == 1 else month - 1
    prev_year = year if month > 1 else year - 1
    next_month = 1 if month == 12 else month + 1
    next_year = year if month < 12 else year + 1

    # Dias do mês
    try:
        first_day_of_month = datetime.date(year, month, 1)
        last_day_of_month = datetime.date(year, month, calendar.monthrange(year, month)[1])
    except ValueError as e:
        return f"Erro ao calcular datas: {e}", 400

    # Consulta agendamentos
    agendamentos = Agendamento.query.filter(
        Agendamento.data >= first_day_of_month,
        Agendamento.data <= last_day_of_month
    ).all()

    # Agrupar por data
    folgas_por_data = {}
    for agendamento in agendamentos:
        folgas_por_data.setdefault(agendamento.data, []).append(agendamento)

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

@app.route('/informar_dados', methods=['GET', 'POST'])
@login_required
def informar_dados():
    usuario = current_user

    if request.method == 'POST':
        # Verifique se os campos obrigatórios estão sendo atualizados
        campos_atualizar = {
            'cpf': request.form.get('cpf'),
            'rg': request.form.get('rg'),
            'data_nascimento': request.form.get('data_nascimento'),
            'celular': request.form.get('celular'),
            'cargo': request.form.get('cargo')
        }

        # Atualiza os campos faltantes no banco de dados
        for campo, valor in campos_atualizar.items():
            if valor:
                setattr(usuario, campo, valor)  # Atualiza o atributo do usuário

        # Valida o cargo se ele foi fornecido
        if campos_atualizar['cargo']:
            cargos_validos = [
                "Agente Administrativo", "Professor I", "Professor Adjunto", 
                "Professor II", "Professor III", "Professor IV", 
                "Servente I", "Servente II", "Servente", 
                "Diretor de Unidade Escolar", "Assistente de Direção", 
                "Pedagoga Comunitaria", "Assistente Tecnico Pedagogico", 
                "Secretario de Unidade Escolar", "Educador de Desenvolvimento Infanto Juvenil", 
                "Atendente de Educação I", "Atendente de Educação II", 
                "Trabalhador", "Inspetor de Aluno"
            ]
            cargo = campos_atualizar['cargo']
            if cargo not in cargos_validos:
                flash('Cargo inválido. Por favor, selecione um cargo válido.', 'danger')
                return render_template('informar_dados.html', usuario=usuario)  # Se cargo for inválido, retorna ao formulário

        # Salva os dados atualizados no banco
        db.session.commit()

        flash("Dados atualizados com sucesso! Você agora pode acessar o sistema.", "success")
        return redirect(url_for('index'))  # Redireciona de volta para a página principal

    return render_template('informar_dados.html', usuario=usuario)

from email_validator import validate_email, EmailNotValidError

@app.route('/register', methods=['GET', 'POST'])
def register():
    usuario = current_user  # Obtém o usuário logado
    
    if request.method == 'POST':
        nome = request.form['nome']
        registro = request.form['registro']
        email = request.form['email']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar_senha']
        cpf = request.form['cpf']
        rg = request.form['rg']
        data_nascimento = request.form['data_nascimento']
        celular = request.form['celular']
        cargo = request.form['cargo']

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

        # Verifica se todos os campos obrigatórios estão preenchidos
        campos_obrigatorios = {
            "CPF": cpf,
            "RG": rg,
            "Data de Nascimento": data_nascimento,
            "Celular": celular,
            "Cargo": cargo
        }

        campos_pendentes = [campo for campo, valor in campos_obrigatorios.items() if not valor]
        
        if campos_pendentes:
            mensagem = f"Os seguintes campos são obrigatórios: {', '.join(campos_pendentes)}."
            flash(mensagem, 'danger')
            return redirect(url_for('informar_dados'))  # Redireciona para a página de informar dados

        # Criptografa a senha usando pbkdf2:sha256 (método compatível)
        senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')

        # Criação do novo usuário com o status 'pendente', aguardando aprovação
        new_user = User(
            nome=nome,
            registro=registro,
            email=email,
            senha=senha_hash,
            tipo='funcionario',  # Por padrão, o tipo é 'funcionario', mas você pode personalizar conforme necessário
            status='pendente',  # Novo campo para controlar a aprovação
            cpf=cpf,
            rg=rg,
            data_nascimento=data_nascimento,
            celular=celular,
            cargo=cargo
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
@login_required
def relatar_esquecimento():
    if request.method == 'POST':
        data_esquecimento = request.form.get('data_esquecimento')
        hora_primeira_entrada = request.form.get('hora_primeira_entrada') or None
        hora_primeira_saida = request.form.get('hora_primeira_saida') or None
        hora_segunda_entrada = request.form.get('hora_segunda_entrada') or None
        hora_segunda_saida = request.form.get('hora_segunda_saida') or None

        if not any([hora_primeira_entrada, hora_primeira_saida, hora_segunda_entrada, hora_segunda_saida]):
            flash('Você deve preencher ao menos um campo de horário.', 'danger')
            return redirect(url_for('relatar_esquecimento'))

        motivo = request.form.get('motivo') or None

        # Observe que agora chamamos datetime.datetime.strptime
        nova_data = datetime.datetime.strptime(data_esquecimento, '%Y-%m-%d').date()

        novo_esquecimento = EsquecimentoPonto(
            user_id=current_user.id,
            nome=current_user.nome,
            registro=current_user.registro,
            data_esquecimento=nova_data,
            hora_primeira_entrada=hora_primeira_entrada,
            hora_primeira_saida=hora_primeira_saida,
            hora_segunda_entrada=hora_segunda_entrada,
            hora_segunda_saida=hora_segunda_saida,
            motivo=motivo
        )

        try:
            db.session.add(novo_esquecimento)
            db.session.commit()
            flash('Registro de esquecimento enviado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar o registro: {e}', 'danger')

        return redirect(url_for('relatar_esquecimento'))

    return render_template('relatar_esquecimento.html')


from datetime import date, timedelta
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

@app.route('/relatorio_ponto')
@login_required
def relatorio_ponto():
    if current_user.tipo != 'administrador':  
        flash("Acesso negado.", "danger")
        return redirect(url_for('index'))

    mes_selecionado = request.args.get('mes', type=int)
    registros = []
    periodo_inicio = periodo_fim = None  

    if mes_selecionado:
        ano_atual = datetime.datetime.now().year
        mes_anterior = 12 if mes_selecionado == 1 else mes_selecionado - 1
        ano_mes_anterior = ano_atual - 1 if mes_selecionado == 1 else ano_atual

        periodo_inicio = datetime.datetime(ano_mes_anterior, mes_anterior, 10)
        periodo_fim     = datetime.datetime(ano_atual, mes_selecionado, 9, 23, 59, 59)

        # Agendamentos
        agendamentos = Agendamento.query.filter(
            Agendamento.data >= periodo_inicio,
            Agendamento.data <= periodo_fim
        ).order_by(Agendamento.data.asc()).all()

        for ag in agendamentos:
            registros.append({
                'id':            ag.id,
                'usuario':       ag.funcionario,
                'registro':      ag.funcionario.registro,
                'tipo':          'Agendamento',
                'data':          ag.data,
                'motivo':        ag.motivo,
                'horapentrada':  '—',
                'horapsaida':    '—',
                'horasentrada':  '—',
                'horassaida':    '—',
                'conferido':     ag.conferido
            })

        # Esquecimentos de Ponto
        esquecimentos = EsquecimentoPonto.query.filter(
            EsquecimentoPonto.data_esquecimento >= periodo_inicio,
            EsquecimentoPonto.data_esquecimento <= periodo_fim
        ).order_by(EsquecimentoPonto.data_esquecimento.asc()).all()

        for esc in esquecimentos:
            registros.append({
                'id':            esc.id,
                'usuario':       esc.usuario,
                'registro':      esc.usuario.registro,
                'tipo':          'Esquecimento de Ponto',
                'data':          esc.data_esquecimento,
                'motivo':        esc.motivo,
                'horapentrada':  esc.hora_primeira_entrada or '—',
                'horapsaida':    esc.hora_primeira_saida  or '—',
                'horasentrada':  esc.hora_segunda_entrada or '—',
                'horassaida':    esc.hora_segunda_saida   or '—',
                'conferido':     esc.conferido
            })

        # 🔠 Ordenar os registros em ordem alfabética pelo nome do usuário
        registros.sort(key=lambda r: r['usuario'].nome.lower())

    return render_template(
        'relatorio_ponto.html',
        registros=registros,
        mes_selecionado=mes_selecionado,
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim
    )

@app.route('/atualizar_conferido', methods=['POST'])
@login_required
def atualizar_conferido():
    data = request.get_json()
    registro_id = data.get("id")
    tipo = data.get("tipo")
    status = data.get("conferido")  # Booleano True/False

    if tipo == "Agendamento":
        registro = Agendamento.query.get(registro_id)
    else:
        registro = EsquecimentoPonto.query.get(registro_id)

    if registro:
        registro.conferido = status
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"success": False}), 400


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
    

from sqlalchemy import asc
from collections import defaultdict
from flask import flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user
import datetime

@app.route('/deferir_folgas', methods=['GET', 'POST'])
@login_required
def deferir_folgas():
    # Função para buscar folgas pendentes/espera, com filtro para administrador e funcionário comum
    def buscar_folgas():
        if current_user.tipo == 'administrador':
            folgas_query = (
                db.session.query(Agendamento)
                .join(User, Agendamento.funcionario_id == User.id)
                .filter(Agendamento.status.in_(['em_espera', 'pendente']))
                .order_by(asc(User.cargo))
            )
        else:
            folgas_query = (
                db.session.query(Agendamento)
                .join(User, Agendamento.funcionario_id == User.id)
                .filter(
                    Agendamento.funcionario_id == current_user.id,
                    Agendamento.status.in_(['em_espera', 'pendente'])
                )
                .order_by(asc(User.cargo))
            )
        return folgas_query.all()

    def gerar_avisos(folgas_em_espera):
        avisos = []
        if current_user.tipo == 'administrador':
            for folga_espera in folgas_em_espera:
                cargo = folga_espera.funcionario.cargo or 'Sem Cargo Definido'
                data = folga_espera.data

                # Buscar apenas os outros agendamentos do mesmo cargo e mesma data
                conflitos = (
                    db.session.query(User.nome)
                    .join(Agendamento, Agendamento.funcionario_id == User.id)
                    .filter(
                        User.cargo == cargo,
                        Agendamento.data == data,
                        Agendamento.id != folga_espera.id,
                        Agendamento.status.in_(["deferido", "em_espera", "pendente"])
                    )
                    .all()
                )

                if conflitos:
                    linhas = ""
                    # Funcionário em espera
                    linhas += f"""
                    <tr>
                        <td>
                            <span class="status-dot dot-warning"></span> {folga_espera.funcionario.nome}
                        </td>
                        <td>{cargo}</td>
                        <td>{data.strftime('%d/%m/%Y')}</td>
                        <td><span class="badge bg-warning text-dark">Em espera</span></td>
                    </tr>
                    """
                    # Funcionários já agendados
                    for (nome,) in conflitos:
                        linhas += f"""
                        <tr>
                            <td>
                                <span class="status-dot dot-success"></span> {nome}
                            </td>
                            <td>{cargo}</td>
                            <td>{data.strftime('%d/%m/%Y')}</td>
                            <td><span class="badge bg-success">Agendado</span></td>
                        </tr>
                        """

                    mensagem = f"""
                    <div class="card shadow-sm border-0 mb-3 premium-alert">
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-sm table-striped mb-0 align-middle">
                                    <thead class="table-light">
                                        <tr>
                                            <th>Funcionário</th>
                                            <th>Cargo</th>
                                            <th>Data</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {linhas}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    """
                    avisos.append(mensagem)

        return avisos

    # Busca as folgas em espera para mostrar na página
    folgas = buscar_folgas()
    avisos = gerar_avisos(folgas)

    # Processa submissão de formulário POST para deferir ou indeferir folgas
    if request.method == 'POST':
        folga_id = request.form.get('folga_id')
        novo_status = request.form.get('status')
        folga = Agendamento.query.get(folga_id)

        if not folga:
            flash("Agendamento não encontrado.", "danger")
            return redirect(url_for('deferir_folgas'))

        usuario = User.query.get(folga.funcionario_id)

        # Validação banco de horas para folgas do tipo BH
        if folga.motivo == 'BH' and novo_status == 'deferido':
            total_minutos = (folga.horas or 0) * 60 + (folga.minutos or 0)
            if usuario.banco_horas >= total_minutos:
                usuario.banco_horas -= total_minutos
                novo_banco_horas = BancoDeHoras(
                    funcionario_id=usuario.id,
                    horas=folga.horas or 0,
                    minutos=folga.minutos or 0,
                    total_minutos=total_minutos,
                    data_realizacao=folga.data,
                    motivo=folga.motivo,
                    status="Deferida",
                    data_criacao=datetime.datetime.utcnow(),
                )
                db.session.add(novo_banco_horas)
            else:
                flash("O funcionário não tem horas suficientes no banco de horas para este agendamento.", "danger")
                return redirect(url_for('deferir_folgas'))

        # Validação para TRE: agora apenas chama sync ao deferir
        if folga.motivo == 'TRE' and novo_status == 'deferido':
            sync_tre_user(usuario.id)

        # Atualiza o status da folga
        folga.status = novo_status

        try:
            db.session.commit()
            flash(
                f"A folga de {folga.funcionario.nome} foi {novo_status} com sucesso!",
                "success" if novo_status == 'deferido' else "danger"
            )

            # Preparação do email personalizado
            if novo_status == 'deferido':
                assunto = "E.M José Padin Mouta - Deferimento de Folga"
                mensagem_html = f"""
                <html>
                  <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5;">
                    <p>Prezado(a) Senhor(a) <strong>{usuario.nome}</strong>,</p>
                    <p>
                      Cumprimentando-o(a), informamos que a sua solicitação de 
                      <strong style="color: #007bff;">FOLGA</strong> para o dia 
                      <strong style="color: #007bff;">{folga.data.strftime('%d/%m/%Y')}</strong> foi 
                      <strong style="color: #5cb85c;">DEFERIDA</strong> pela direção da unidade escolar.
                      Assim, seu afastamento para a referida data está devidamente registrado.
                    </p>
                    <p>
                      Agradecemos a colaboração e estamos à disposição para quaisquer esclarecimentos adicionais.
                    </p>
                    <p>
                      Caso necessite, você pode acessar o protocolo do agendamento através do nosso sistema.
                    </p>
                    <br>
                    <p>Atenciosamente,</p>
                    <p>
                      Nilson Cruz<br>
                      Secretário da Unidade Escolar<br>
                      3496-5321<br>
                      E.M José Padin Mouta
                    </p>
                  </body>
                </html>
                """
                mensagem_texto = f"""Prezado(a) Senhor(a) {usuario.nome},

Cumprimentando-o(a), informamos que a sua solicitação de FOLGA para o dia {folga.data.strftime('%d/%m/%Y')} foi DEFERIDA pela direção da unidade escolar.
Assim, seu afastamento para a referida data está devidamente registrado.

Agradecemos a colaboração e estamos à disposição para quaisquer esclarecimentos adicionais.

Caso necessite, você pode acessar o protocolo do agendamento através do nosso sistema.

Atenciosamente,

Nilson Cruz
Secretário da Unidade Escolar
3496-5321
E.M José Padin Mouta
"""
            else:
                assunto = "E.M José Padin Mouta - Indeferimento de Folga"
                mensagem_html = f"""
                <html>
                  <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5;">
                    <p>Prezado(a) Senhor(a) <strong>{usuario.nome}</strong>,</p>
                    <p>
                      Cumprimentando-o(a), comunicamos que, após análise criteriosa, a sua solicitação de 
                      <strong style="color: #007bff;">FOLGA</strong> para o dia 
                      <strong style="color: #007bff;">{folga.data.strftime('%d/%m/%Y')}</strong> não pôde ser 
                      <strong style="color: #d9534f;">DEFERIDA</strong> pela direção da unidade escolar.
                    </p>
                    <p>
                      Lamentamos o inconveniente e estamos à disposição para eventuais esclarecimentos ou para discutir alternativas viáveis. Agradecemos a sua compreensão.
                    </p>
                    <p>
                      Caso necessite, você pode acessar o protocolo do agendamento através do nosso sistema.
                    </p>
                    <br>
                    <p>Atenciosamente,</p>
                    <p>
                      Nilson Cruz<br>
                      Secretário da Unidade Escolar<br>
                      3496-5321<br>
                      E.M José Padin Mouta
                    </p>
                  </body>
                </html>
                """
                mensagem_texto = f"""Prezado(a) Senhor(a) {usuario.nome},

Cumprimentando-o, comunicamos que, após análise criteriosa, a sua solicitação de FOLGA para o dia {folga.data.strftime('%d/%m/%Y')} não pôde ser DEFERIDA pela direção da unidade escolar.

Lamentamos o inconveniente e estamos à disposição para eventuais esclarecimentos ou para discutir alternativas viáveis. Agradecemos a sua compreensão.

Caso necessite, você pode acessar o protocolo do agendamento através do nosso sistema.

Atenciosamente,

Nilson Cruz
Secretário da Unidade Escolar
3496-5321
E.M José Padin Mouta
"""
            # Envia o email para o usuário
            enviar_email(usuario.email, assunto, mensagem_html, mensagem_texto)

        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar folga: {str(e)}", "danger")

        # Atualiza lista e avisos para exibir as mudanças sem recarregar a página
        folgas = buscar_folgas()
        avisos = gerar_avisos(folgas)

    # Agrupa folgas por cargo para facilitar exibição agrupada no template
    folgas_por_cargo = defaultdict(list)
    for f in folgas:
        cargo = f.funcionario.cargo or "Sem Cargo Definido"
        folgas_por_cargo[cargo].append(f)

    return render_template(
        'deferir_folgas.html',
        folgas_por_cargo=folgas_por_cargo,
        avisos=avisos
    )

import datetime
from flask import render_template, request
from flask_login import login_required, current_user

# ajuste os imports conforme o seu projeto
# from app import app, db
# from models import User, TRE, Agendamento

@app.route('/historico', methods=['GET'])
@login_required
def historico():
    # 🔹 Garante que os campos tre_total e tre_usufruidas do User estejam sincronizados
    sync_tre_user(current_user.id)

    usuario = User.query.get_or_404(current_user.id)

    # --- Ano selecionado (default = ano atual)
    ano = request.args.get("ano", type=int) or datetime.datetime.now().year

    # ===== Folgas abonadas (conta apenas AB deferido no ano) =====
    limite_abonadas_ano = 6
    abonadas_ano = (
        Agendamento.query
        .filter(
            Agendamento.funcionario_id == current_user.id,
            Agendamento.motivo == 'AB',
            Agendamento.status == 'deferido',
            Agendamento.data >= datetime.date(ano, 1, 1),
            Agendamento.data <= datetime.date(ano, 12, 31),
        )
        .count()
    )
    saldo_abonadas = max(limite_abonadas_ano - abonadas_ano, 0)

    # ===== TREs (agora já estão sincronizadas no User) =====
    tre_total = int(usuario.tre_total or 0)            # créditos totais de TRE do usuário
    tre_usufruidas = int(usuario.tre_usufruidas or 0)  # dias já utilizados pelo usuário
    tre_restantes = max(tre_total - tre_usufruidas, 0)

    # ===== Banco de horas =====
    total_minutos = int(usuario.banco_horas or 0)
    horas = total_minutos // 60
    minutos = total_minutos % 60
    banco_horas_formatado = f"{horas}h {minutos}min" if total_minutos > 0 else "0h 0min"

    # ===== Últimas folgas (extrato) =====
    ultimas_folgas = (
        Agendamento.query
        .filter_by(funcionario_id=current_user.id)
        .order_by(Agendamento.data.desc())
        .limit(10)
        .all()
    )

    # ===== Minhas TREs (lista para a tabela) =====
    minhas_tres = (
        TRE.query
        .filter(TRE.funcionario_id == current_user.id)
        .order_by(TRE.data_envio.desc(), TRE.id.desc())
        .all()
    )

    # Estatísticas para os chips (apenas informativo)
    pend = def_ = ind = dias_pend = dias_def = 0
    for t in minhas_tres:
        st = (t.status or '').strip().lower()
        if st == 'pendente':
            pend += 1
            dias_pend += int(t.dias_folga or 0)
        elif st == 'deferida':
            def_ += 1
            dias_def += int((t.dias_validados if t.dias_validados is not None else t.dias_folga) or 0)
        elif st == 'indeferida':
            ind += 1

    tre_stats = {
        "total": len(minhas_tres),
        "pend": pend,
        "def_": def_,
        "ind": ind,
        "dias_pend": dias_pend,
        "dias_def": dias_def,
    }

    # ===== Avisos =====
    avisos = []
    if saldo_abonadas == 0:
        avisos.append("⚠️ Você atingiu o limite anual de folgas abonadas.")
    if tre_restantes > 0:
        avisos.append(f"🔔 Você ainda pode usufruir {tre_restantes} TRE(s).")
    if total_minutos > 300:
        avisos.append("ℹ️ Você possui muitas horas acumuladas no Banco de Horas.")

    # Render
    return render_template(
        'historico.html',
        ano=ano,
        limite_abonadas_ano=limite_abonadas_ano,
        abonadas_ano=abonadas_ano,
        saldo_abonadas=saldo_abonadas,
        tre_total=tre_total,
        tre_usufruidas=tre_usufruidas,
        tre_restantes=tre_restantes,
        banco_horas_formatado=banco_horas_formatado,
        ultimas_folgas=ultimas_folgas,
        minhas_tres=minhas_tres,
        tre_stats=tre_stats,
        avisos=avisos,
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
    usuario = current_user  # Usuário logado

    # Lista de cargos para popular o select no template, em ordem alfabética
    cargos = sorted([
        "Agente Administrativo", "Professor I", "Professor Adjunto", 
        "Professor II", "Professor III", "Professor IV", 
        "Servente I", "Servente II", "Servente", 
        "Diretor de Unidade Escolar", "Assistente de Direção", 
        "Pedagoga Comunitaria", "Assistente Tecnico Pedagogico", 
        "Secretario de Unidade Escolar", "Educador de Desenvolvimento Infanto Juvenil", 
        "Atendente de Educação I", "Atendente de Educação II", 
        "Trabalhador", "Inspetor de Aluno"
    ])

    if request.method == 'POST':
        try:
            # Recupera os dados do formulário
            usuario.celular = request.form.get('celular') or None
            usuario.data_nascimento = request.form.get('data_nascimento') or None
            usuario.cpf = request.form.get('cpf') or None
            usuario.rg = request.form.get('rg') or None
            usuario.data_emissao_rg = request.form.get('data_emissao_rg') or None
            usuario.orgao_emissor = request.form.get('orgao_emissor') or None
            usuario.graduacao = request.form.get('graduacao') or None
            usuario.cargo = request.form.get('cargo') or None  # Atualiza o cargo
            
            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar o perfil: {str(e)}', 'danger')

        return redirect(url_for('perfil'))

    return render_template('perfil.html', usuario=usuario, cargos=cargos)



@app.route('/relatorio_horas_extras')
@login_required
def relatorio_horas_extras():
    # Verifica se o usuário logado é administrador
    if current_user.tipo != 'administrador':
        flash("Acesso negado. Você não tem permissão para acessar este relatório.", "danger")
        return redirect(url_for('index'))
    
    # Consulta todos os usuários
    usuarios = User.query.all()
    usuarios_relatorio = []
    for usuario in usuarios:
        total_minutos = usuario.banco_horas  # Total de minutos armazenados
        horas = total_minutos // 60
        minutos = total_minutos % 60
        
        usuarios_relatorio.append({
            "nome": usuario.nome,
            "registro": usuario.registro,
            "email": usuario.email,
            "horas": horas,
            "minutos": minutos
        })

    return render_template('relatorio_horas_extras.html', usuarios=usuarios_relatorio)

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

# Página principal
@app.route('/admin/agendamentos', methods=['GET'])
@login_required
def admin_agendamentos():
    if current_user.tipo != 'administrador':
        flash("Acesso negado.", "danger")
        return redirect(url_for('index'))

    return render_template("admin_agendamentos.html")


@app.route('/admin/agendamentos/ajax', methods=['GET'])
@login_required
def admin_agendamentos_ajax():
    if current_user.tipo != 'administrador':
        return jsonify({"error": "Acesso negado"}), 403

    nome = (request.args.get("nome") or "").strip()
    status = (request.args.get("status") or "").strip().lower()
    cargo = (request.args.get("cargo") or "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Base query
    query = (
        User.query
        .join(Agendamento)
        .options(joinedload(User.agendamentos))
    )

    # Filtros por nome e cargo
    if nome:
        query = query.filter(User.nome.ilike(f"%{nome}%"))
    if cargo:
        query = query.filter(User.cargo == cargo)

    # Ordena e pagina
    query = query.order_by(User.nome.asc()).distinct()
    funcionarios = query.paginate(page=page, per_page=per_page)

    dados = []
    for func in funcionarios.items:
        ags = []
        for ag in func.agendamentos:
            ag_status = (ag.status or "").strip().lower()

            # Aplica os filtros de status só aqui
            if not status:
                pass
            elif status == "deferido" and not ag_status.startswith("deferido"):
                continue
            elif status == "indeferido" and not ag_status.startswith("indeferido"):
                continue
            elif status == "em_espera" and ag_status not in ["em_espera", "em espera", "pendente"]:
                continue

            ags.append({
                "id": ag.id,
                "data": ag.data.strftime("%d/%m/%Y"),
                "motivo": ag.motivo,
                "status": ag.status.strip().title() if ag.status else "",
                "delete_url": url_for('admin_delete_agendamento', id=ag.id)
            })

        # Só adiciona o funcionário se tiver agendamentos visíveis
        if ags:
            dados.append({
                "id": func.id,
                "funcionario": (func.nome or "").title(),
                "cargo": func.cargo,
                "agendamentos": ags
            })

    return jsonify({
        "page": funcionarios.page,
        "pages": funcionarios.pages,
        "has_next": funcionarios.has_next,
        "has_prev": funcionarios.has_prev,
        "next_num": funcionarios.next_num,
        "prev_num": funcionarios.prev_num,
        "filters": {"nome": nome, "status": status, "cargo": cargo},
        "dados": dados
    })

# Rota para exclusão de um agendamento pelo administrador
@app.route('/admin/delete_agendamento/<int:id>', methods=['POST'])
@login_required
def admin_delete_agendamento(id):
    if current_user.tipo != 'administrador':
        return jsonify({"error": "Acesso negado"}), 403
    
    agendamento = Agendamento.query.get_or_404(id)
    db.session.delete(agendamento)
    db.session.commit()
    return jsonify({"success": True, "message": "Agendamento excluído com sucesso."})

@app.route('/user_info_all', methods=['GET'])
@login_required
def user_info_all():
    if current_user.tipo != 'administrador':
        flash("Acesso negado. Esta página é exclusiva para administradores.", "danger")
        return redirect(url_for('index'))
    
    # Recupera todos os usuários ordenados pelo nome
    users = User.query.order_by(User.nome.asc()).all()
    return render_template('user_info_all.html', users=users)

@app.route('/check_unique')
def check_unique():
    campo = request.args.get('campo')
    valor = request.args.get('valor', '').strip()
    exists = False
    if campo == 'registro':
        exists = User.query.filter_by(registro=valor).first() is not None
    elif campo == 'email':
        exists = User.query.filter_by(email=valor).first() is not None
    elif campo == 'cpf':
        exists = User.query.filter_by(cpf=valor).first() is not None
    elif campo == 'rg':
        exists = User.query.filter_by(rg=valor).first() is not None
    return jsonify({'exists': exists})

# =============================
# IMPORTS EXTRAS (se ainda não tiver)
# =============================
from sqlalchemy import or_
from sqlalchemy import func, case

# =============================
# Funções auxiliares
# =============================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# =============================
# Função de sincronização TRE
# =============================
def sync_tre_user(usuario_id):
    usuario = User.query.get(usuario_id)
    if not usuario:
        return 0, 0, 0

    # 1) Total deferido (dias de TRE deferidos na tabela TRE)
    tre_total = db.session.query(
        func.coalesce(func.sum(
            case(
                (TRE.status == "deferida",
                 case(
                     (TRE.dias_validados != None, TRE.dias_validados),
                     else_=TRE.dias_folga
                 )),
                else_=0
            )
        ), 0)
    ).filter(TRE.funcionario_id == usuario_id).scalar()

    # 2) Usufruídas (quantos agendamentos de TRE foram deferidos)
    tre_usufruidas = db.session.query(
        func.count(Agendamento.id)
    ).filter(
        Agendamento.funcionario_id == usuario_id,
        Agendamento.motivo == "TRE",
        Agendamento.status == "deferido"
    ).scalar()

    # 3) Restantes (saldo = deferidos - usados)
    tre_restantes = max((tre_total or 0) - (tre_usufruidas or 0), 0)

    # Atualiza o usuário
    usuario.tre_total = tre_total or 0
    usuario.tre_usufruidas = tre_usufruidas or 0
    db.session.commit()

    return usuario.tre_total, usuario.tre_usufruidas, tre_restantes

# =============================
# Rota: Adicionar TRE (usuário)
# =============================
@app.route("/adicionar_tre", methods=["GET", "POST"])
@login_required
def adicionar_tre():
    if request.method == "POST":
        dias_folga = request.form.get("dias_folga", type=int)
        arquivo = request.files.get("arquivo_pdf")

        if not dias_folga or dias_folga < 1 or not arquivo:
            flash("Preencha corretamente os campos e anexe o PDF.", "danger")
            return redirect(url_for("adicionar_tre"))

        if not allowed_file(arquivo.filename):
            flash("Somente PDF é permitido.", "danger")
            return redirect(url_for("adicionar_tre"))

        # Salva arquivo com nome seguro + timestamp
        filename = secure_filename(f"{current_user.id}_{datetime.datetime.now():%Y%m%d%H%M%S}_{arquivo.filename}")
        save_path = os.path.join(app.root_path, UPLOAD_FOLDER)
        os.makedirs(save_path, exist_ok=True)
        arquivo.save(os.path.join(save_path, filename))

        # Cria registro pendente
        nova = TRE(
            funcionario_id=current_user.id,
            dias_folga=dias_folga,
            arquivo_pdf=filename,
            status="pendente"
        )
        db.session.add(nova)
        db.session.commit()

        # Sincroniza usuário
        sync_tre_user(current_user.id)

        flash("TRE enviada para análise do administrador.", "success")
        return redirect(url_for("historico"))

    tres_ultimas = (TRE.query.filter_by(funcionario_id=current_user.id)
                    .order_by(TRE.data_envio.desc()).limit(3).all())
    return render_template("adicionar_tre.html", user=current_user, tres=tres_ultimas)


# =============================
# Rota: Listar TREs do usuário
# =============================
@app.route("/minhas_tres", methods=["GET"])
@login_required
def minhas_tres():
    minhas_tres = (TRE.query
                   .filter_by(funcionario_id=current_user.id)
                   .order_by(TRE.data_envio.desc())
                   .all())

    # Sincroniza antes de exibir
    sync_tre_user(current_user.id)

    return render_template("minhas_tres.html", tres=minhas_tres, user=current_user)


# =============================
# Rota: Download do PDF da TRE
# =============================
@app.route("/download_tre/<int:tre_id>", methods=["GET"])
@login_required
def download_tre(tre_id):
    tre = TRE.query.get_or_404(tre_id)

    if tre.funcionario_id != current_user.id and current_user.tipo != "administrador":
        flash("Você não tem permissão para acessar este arquivo.", "danger")
        return redirect(url_for("minhas_tres"))

    directory = os.path.join(app.root_path, UPLOAD_FOLDER)
    return send_from_directory(directory, tre.arquivo_pdf, as_attachment=True)


# =============================
# ADMIN: Listagem/Análise de TREs
# =============================
@app.route("/admin/tres", methods=["GET"])
@login_required
def admin_tres_list():
    if current_user.tipo != "administrador":
        flash("Acesso negado.", "danger")
        return redirect(url_for("index"))

    status = request.args.get("status", "pendente")
    busca = request.args.get("q", "").strip()

    q = TRE.query.join(User, User.id == TRE.funcionario_id)
    if status in ("pendente", "deferida", "indeferida"):
        q = q.filter(TRE.status == status)

    if busca:
        like = f"%{busca}%"
        q = q.filter(or_(User.nome.ilike(like), User.registro.ilike(like)))

    tres = q.order_by(TRE.data_envio.desc()).all()
    return render_template("admin_tres.html", tres=tres, status=status)


# =============================
# ADMIN: Decidir (deferir/indeferir) TRE
# =============================
@app.route("/admin/tre/<int:tre_id>/decidir", methods=["POST"])
@login_required
def admin_tre_decidir(tre_id):
    if current_user.tipo != "administrador":
        return jsonify({"error": "Acesso negado"}), 403

    tre = TRE.query.get_or_404(tre_id)
    user = User.query.get_or_404(tre.funcionario_id)

    acao = request.form.get("acao")  # "aprovar" | "indeferir"
    dias_validados = request.form.get("dias_validados", type=int)
    parecer = (request.form.get("parecer_admin") or "").strip()

    if acao not in ("aprovar", "indeferir"):
        return jsonify({"error": "Ação inválida."}), 400

    if tre.status in ("deferida", "indeferida"):
        return jsonify({"error": "Esta TRE já foi analisada."}), 400

    if acao == "aprovar":
        dias_aprovados = dias_validados if (dias_validados and dias_validados > 0) else tre.dias_folga
        tre.status = "deferida"
        tre.dias_validados = dias_aprovados
        tre.parecer_admin = parecer or None
        tre.validado_em = datetime.datetime.utcnow()
        tre.validado_por_id = current_user.id

        db.session.commit()
        sync_tre_user(user.id)
        return jsonify({"success": True, "message": f"TRE deferida (+{dias_aprovados} dia(s))."})

    else:
        tre.status = "indeferida"
        tre.dias_validados = dias_validados if (dias_validados and dias_validados > 0) else None
        tre.parecer_admin = parecer or None
        tre.validado_em = datetime.datetime.utcnow()
        tre.validado_por_id = current_user.id

        db.session.commit()
        sync_tre_user(user.id)
        return jsonify({"success": True, "message": "TRE indeferida."})


# =============================
# ADMIN: Excluir TRE
# =============================
@app.route("/admin/tre/<int:tre_id>/excluir", methods=["POST"])
@login_required
def admin_tre_excluir(tre_id):
    if current_user.tipo != "administrador":
        return jsonify({"error": "Acesso negado"}), 403

    tre = TRE.query.get_or_404(tre_id)
    user = User.query.get_or_404(tre.funcionario_id)

    try:
        db.session.delete(tre)
        db.session.commit()

        # Sincroniza saldo do usuário após exclusão
        sync_tre_user(user.id)

        return jsonify({"success": True})
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Falha ao excluir a TRE."}), 500

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
