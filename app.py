from flask import (
    Flask,
    session,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    make_response,
    abort,
    jsonify,
    send_from_directory,
    send_file,
    current_app,
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import io
import smtplib
import calendar
import datetime          # datetime.date, datetime.datetime etc.
from datetime import timedelta, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy import func, or_, case
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm   # << agora tem cm e mm
from reportlab.lib import colors


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
SMTP_PASS = "xboztvmzwskygzzh"   # 🔒 Ideal: usar variável de ambiente!

VERSAO_ATUAL_TERMO = '2025-07-25'  # Versão usada no login
CURRENT_TERMO = "2025-07-25"       # Versão usada nas rotas de termo


# ===========================================
# MODELOS
# ===========================================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    registro = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    senha = db.Column(db.String(256), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'funcionario' ou 'administrador'
    status = db.Column(db.String(20), default='pendente')  # 'pendente', 'aprovado', 'rejeitado'

    # Controle de ativo na unidade (soft delete)
    ativo = db.Column(db.Boolean, nullable=False, default=True, index=True)

    # Campos para TRE
    tre_total = db.Column(db.Integer, default=0)         # Total de dias de TRE deferidos (créditos)
    tre_usufruidas = db.Column(db.Integer, default=0)    # Dias de TRE já utilizados (agendamentos deferidos)
    cargo = db.Column(db.String(100), nullable=True)

    # Banco de horas em minutos
    banco_horas = db.Column(db.Integer, default=0, nullable=False)

    # Contato/pessoais
    celular = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)

    # Documentos
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    rg = db.Column(db.String(20), nullable=False, unique=True)
    data_emissao_rg = db.Column(db.Date, nullable=True)
    orgao_emissor = db.Column(db.String(20), nullable=True)

    graduacao = db.Column(db.String(50), nullable=True)

    # Termos
    aceitou_termo = db.Column(db.Boolean, default=False)
    versao_termo = db.Column(db.String(20), default=None)  # Ex: '2025-07-25'

    # Relacionamentos
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
    conferido = db.Column(db.Boolean, default=False)

    funcionario = db.relationship('User', backref='agendamentos_funcionario', lazy=True)


class Folga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="Pendente")  # "Pendente", "Deferida"
    funcionario = db.relationship('User', backref=db.backref('folgas', lazy=True))


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
    dias_validados = db.Column(db.Integer, nullable=True)
    parecer_admin = db.Column(db.Text, nullable=True)
    validado_em = db.Column(db.DateTime, nullable=True)
    validado_por_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Funcionário dono da TRE
    funcionario = db.relationship(
        'User',
        backref=db.backref('tres', lazy=True),
        foreign_keys=[funcionario_id],
        lazy=True
    )
    # Admin que validou
    validador = db.relationship(
        'User',
        backref=db.backref('tres_validadas', lazy=True),
        foreign_keys=[validado_por_id],
        lazy=True
    )


# ===========================================
# FUNÇÕES GERAIS
# ===========================================
def enviar_email(destinatario, assunto, mensagem_html, mensagem_texto=None):
    """
    Envia um e-mail com mensagem HTML. Opcionalmente, pode incluir texto puro.
    """
    msg = MIMEMultipart("alternative")
    msg['From'] = SMTP_USER
    msg['To'] = destinatario
    msg['Subject'] = assunto

    if not mensagem_texto:
        mensagem_texto = "Por favor, visualize este e-mail em um cliente que suporte HTML."

    parte_texto = MIMEText(mensagem_texto, 'plain')
    parte_html = MIMEText(mensagem_html, 'html')

    msg.attach(parte_texto)
    msg.attach(parte_html)

    try:
        servidor = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        servidor.starttls()
        servidor.login(SMTP_USER, SMTP_PASS)
        servidor.send_message(msg)
        servidor.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print("Erro ao enviar e-mail:", e)


# ===========================================
# AUTENTICAÇÃO / TERMO
# ===========================================
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

    if current_user.aceitou_termo and current_user.versao_termo == CURRENT_TERMO:
        return redirect(url_for('index'))

    return render_template('termo_uso.html', termo_versao=CURRENT_TERMO)


@app.route('/aceitar_termo', methods=['POST'])
@login_required
def aceitar_termo():
    current_user.aceitou_termo = True
    current_user.versao_termo = CURRENT_TERMO
    db.session.commit()
    flash('Termo de uso aceito com sucesso.', 'success')
    return redirect(url_for('index'))


# ===========================================
# RECUPERAÇÃO DE SENHA
# ===========================================
@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form['email']
        registro = request.form['registro']
        usuario = User.query.filter_by(email=email, registro=registro).first()

        if usuario:
            session['user_id'] = usuario.id
            return redirect(url_for('redefinir_senha'))
        else:
            flash('Usuário não encontrado. Verifique os dados e tente novamente.', 'danger')

    return render_template('recuperar_senha.html')


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
            usuario.senha = generate_password_hash(nova_senha)
            db.session.commit()
            session.pop('user_id', None)
            flash('Senha redefinida com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))

    return render_template('redefinir_senha.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema. Para acessá-lo, faça login novamente.", "success")
    return redirect(url_for('login'))


# ===========================================
# PÁGINA INICIAL
# ===========================================
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    usuario = current_user

    # Campos obrigatórios
    campos_obrigatorios = {
        "Celular": usuario.celular,
        "Data de Nascimento": usuario.data_nascimento,
        "CPF": usuario.cpf,
        "RG": usuario.rg,
        "Cargo": usuario.cargo
    }

    campos_pendentes = [campo for campo, valor in campos_obrigatorios.items() if not valor]

    if campos_pendentes:
        mensagem = f"""
            Atenção! Complete seu perfil. Os seguintes campos estão em branco: {', '.join(campos_pendentes)}.
            <a href="{url_for('informar_dados')}" class="link-perfil">Clique aqui para preenchê-los</a>.
        """
        flash(mensagem, "warning")
        return redirect(url_for('informar_dados'))

    # Campos opcionais
    campos_opcionais = {
        "Data de Emissão do RG": usuario.data_emissao_rg,
        "Órgão Emissor": usuario.orgao_emissor,
        "Graduação": usuario.graduacao,
    }

    campos_faltantes_opcionais = [campo for campo, valor in campos_opcionais.items() if not valor]

    if campos_faltantes_opcionais:
        mensagem_opcional = f"""
            Você pode completar seu perfil com os seguintes dados: {', '.join(campos_faltantes_opcionais)}.
            <a href="{url_for('perfil')}" class="link-perfil">Clique aqui para preenchê-los</a>.
        """
        flash(mensagem_opcional, "info")

    return render_template('index.html', usuario=usuario)


# ===========================================
# MINHAS JUSTIFICATIVAS
# ===========================================
@app.route('/minhas_justificativas')
@login_required
def minhas_justificativas():
    agendamentos = (
        Agendamento.query
        .filter_by(funcionario_id=current_user.id)
        .order_by(Agendamento.data.desc(), Agendamento.id.desc())
        .all()
    )
    return render_template('minhas_justificativas.html', agendamentos=agendamentos)


# ===========================================
# AGENDAR FOLGA
# ===========================================
@app.route('/agendar', methods=['GET', 'POST'])
@login_required
def agendar():
    if request.method == 'POST':
        # 🔹 Mantém o saldo de TRE sempre correto antes de validar
        sync_tre_user(current_user.id)

        tipo_folga = request.form['tipo_folga']         # 'AB', 'BH', 'DS', 'TRE', 'FS'
        data_folga = request.form['data']
        motivo = request.form['motivo']
        data_referencia = request.form.get('data_referencia')

        substituicao = request.form.get("havera_substituicao")
        nome_substituto = request.form.get("nome_substituto")

        if substituicao == "Não":
            nome_substituto = None

        if tipo_folga == 'AB':
            motivo = 'AB'
            tipo_folga = 'AB'

        # ---- Validação específica para TRE ----
        if tipo_folga == 'TRE' or motivo == 'TRE':
            usuario = User.query.get(current_user.id)
            tre_total = int(usuario.tre_total or 0)
            tre_usuf = int(usuario.tre_usufruidas or 0)
            tre_restantes = max(tre_total - tre_usuf, 0)

            pedidos_abertos = (
                Agendamento.query
                .filter(
                    Agendamento.funcionario_id == current_user.id,
                    Agendamento.motivo == 'TRE',
                    Agendamento.status.in_(['em_espera', 'pendente'])
                )
                .count()
            )

            saldo_disponivel_para_solicitar = tre_restantes - pedidos_abertos

            if saldo_disponivel_para_solicitar <= 0:
                flash("Você não possui TREs disponíveis para agendar no momento.", "danger")
                return render_template('agendar.html')

        descricao_motivo = {
            'AB': 'Abonada',
            'BH': 'Banco de Horas',
            'DS': 'Doação de Sangue',
            'TRE': 'TRE',
            'FS': 'Falta Simples'
        }.get(motivo, 'Agendamento')

        try:
            data_folga = datetime.datetime.strptime(data_folga, '%Y-%m-%d').date()
        except ValueError:
            flash("Data inválida.", "danger")
            return redirect(url_for('agendar'))

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
            horas = int(request.form['quantidade_horas']) if request.form['quantidade_horas'].strip() else 0
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
            funcionario_id=current_user.id,
            status='em_espera',
            data=data_folga,
            motivo=motivo,
            tipo_folga=tipo_folga,
            data_referencia=data_referencia,
            horas=horas,
            minutos=minutos,
            substituicao=substituicao,
            nome_substituto=nome_substituto
        )

        try:
            db.session.add(novo_agendamento)
            db.session.commit()

            assunto = "E.M José Padin Mouta – Confirmação de Agendamento"
            nome = current_user.nome
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

            enviar_email(current_user.email, assunto, mensagem_html, mensagem_texto)
            flash("Agendamento realizado com sucesso. Você receberá um e-mail de confirmação.", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar agendamento: {str(e)}", "danger")

        return redirect(url_for('index'))

    return render_template('agendar.html')


# ===========================================
# CALENDÁRIO
# ===========================================
@app.route('/calendario', methods=['GET', 'POST'])
@app.route('/calendario/<int:year>/<int:month>', methods=['GET', 'POST'])
@login_required
def calendario(year=None, month=None):
    inicio_ano = 2025
    fim_ano = inicio_ano + 9

    if not year or not month:
        hoje = datetime.date.today()
        year = hoje.year
        month = hoje.month

    while month < 1:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1

    prev_month = 12 if month == 1 else month - 1
    prev_year = year if month > 1 else year - 1
    next_month = 1 if month == 12 else month + 1
    next_year = year if month < 12 else year + 1

    try:
        first_day_of_month = datetime.date(year, month, 1)
        last_day_of_month = datetime.date(year, month, calendar.monthrange(year, month)[1])
    except ValueError as e:
        return f"Erro ao calcular datas: {e}", 400

    agendamentos = Agendamento.query.filter(
        Agendamento.data >= first_day_of_month,
        Agendamento.data <= last_day_of_month
    ).all()

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


# ===========================================
# COMPLETAR DADOS OBRIGATÓRIOS
# ===========================================
@app.route('/informar_dados', methods=['GET', 'POST'])
@login_required
def informar_dados():
    usuario = current_user

    if request.method == 'POST':
        campos_atualizar = {
            'cpf': request.form.get('cpf'),
            'rg': request.form.get('rg'),
            'data_nascimento': request.form.get('data_nascimento'),
            'celular': request.form.get('celular'),
            'cargo': request.form.get('cargo')
        }

        for campo, valor in campos_atualizar.items():
            if valor:
                setattr(usuario, campo, valor)

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
                return render_template('informar_dados.html', usuario=usuario)

        db.session.commit()
        flash("Dados atualizados com sucesso! Você agora pode acessar o sistema.", "success")
        return redirect(url_for('index'))

    return render_template('informar_dados.html', usuario=usuario)


# ===========================================
# REGISTRO
# ===========================================
from email_validator import validate_email, EmailNotValidError


@app.route('/register', methods=['GET', 'POST'])
def register():
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

        if senha != confirmar_senha:
            flash('As senhas não coincidem', 'danger')
            return render_template('register.html')

        try:
            validate_email(email)
        except EmailNotValidError as e:
            flash(f'E-mail inválido: {str(e)}', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Este e-mail já está em uso', 'danger')
            return render_template('register.html')

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
            return render_template('register.html')

        senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')

        new_user = User(
            nome=nome,
            registro=registro,
            email=email,
            senha=senha_hash,
            tipo='funcionario',
            status='pendente',
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


# ===========================================
# APROVAR USUÁRIOS
# ===========================================
@app.route('/aprovar_usuarios', methods=['GET', 'POST'])
@login_required
def aprovar_usuarios():
    if current_user.tipo != 'administrador':
        flash('Você não tem permissão para acessar essa página.', 'danger')
        return redirect(url_for('index'))

    usuarios_pendentes = User.query.filter_by(status='pendente').all()

    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        acao = request.form.get('acao')

        if acao is None:
            flash('Ação não especificada', 'danger')
            return redirect(url_for('aprovar_usuarios'))

        usuario = User.query.get(usuario_id)
        if usuario:
            if acao == 'aprovar':
                usuario.status = 'aprovado'
                flash(f'Usuário {usuario.nome} aprovado com sucesso!', 'success')
            elif acao == 'recusar':
                usuario.status = 'rejeitado'
                flash(f'Usuário {usuario.nome} recusado.', 'danger')

            db.session.commit()

        return redirect(url_for('aprovar_usuarios'))

    return render_template('aprovar_usuarios.html', usuarios=usuarios_pendentes)


# ===========================================
# DELETAR AGENDAMENTO (FUNCIONÁRIO)
# ===========================================
@app.route('/delete_agendamento/<int:id>', methods=['POST'])
@login_required
def delete_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)

    if agendamento.funcionario_id == current_user.id:
        db.session.delete(agendamento)
        db.session.commit()
        flash('Agendamento excluído com sucesso.', 'success')
    else:
        flash('Você não tem permissão para excluir este agendamento.', 'danger')

    return redirect(url_for('minhas_justificativas'))


# ===========================================
# ESQUECIMENTO DE PONTO
# ===========================================
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


# ===========================================
# RELATÓRIO PONTO (10 a 9)
# ===========================================
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
        periodo_fim = datetime.datetime(ano_atual, mes_selecionado, 9, 23, 59, 59)

        # --- Agendamentos apenas de usuários ativos ---
        agendamentos = (
            Agendamento.query
            .join(Agendamento.funcionario)  # relacionamento com User
            .options(joinedload(Agendamento.funcionario))
            .filter(
                User.ativo.is_(True),
                Agendamento.data >= periodo_inicio,
                Agendamento.data <= periodo_fim
            )
            .order_by(Agendamento.data.asc())
            .all()
        )

        for ag in agendamentos:
            # defesa extra: se por algum motivo não tiver funcionario, pula
            if not ag.funcionario:
                continue

            registros.append({
                'id': ag.id,
                'usuario': ag.funcionario,
                'registro': ag.funcionario.registro,
                'tipo': 'Agendamento',
                'data': ag.data,
                'motivo': ag.motivo,
                'horapentrada': '—',
                'horapsaida': '—',
                'horasentrada': '—',
                'horassaida': '—',
                'conferido': ag.conferido
            })

        # --- Esquecimentos de ponto apenas de usuários ativos ---
        esquecimentos = (
            EsquecimentoPonto.query
            .join(EsquecimentoPonto.usuario)  # relacionamento com User
            .options(joinedload(EsquecimentoPonto.usuario))
            .filter(
                User.ativo.is_(True),
                EsquecimentoPonto.data_esquecimento >= periodo_inicio,
                EsquecimentoPonto.data_esquecimento <= periodo_fim
            )
            .order_by(EsquecimentoPonto.data_esquecimento.asc())
            .all()
        )

        for esc in esquecimentos:
            if not esc.usuario:
                continue

            registros.append({
                'id': esc.id,
                'usuario': esc.usuario,
                'registro': esc.usuario.registro,
                'tipo': 'Esquecimento de Ponto',
                'data': esc.data_esquecimento,
                'motivo': esc.motivo,
                'horapentrada': esc.hora_primeira_entrada or '—',
                'horapsaida': esc.hora_primeira_saida or '—',
                'horasentrada': esc.hora_segunda_entrada or '—',
                'horassaida': esc.hora_segunda_saida or '—',
                'conferido': esc.conferido
            })

        # Ordena por nome do usuário e, em seguida, por data
        registros.sort(
            key=lambda r: (
                (r['usuario'].nome or '').lower().strip(),
                r['data'] or datetime.datetime.min
            )
        )

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
    # garante que só admin marque/desmarque conferido
    if current_user.tipo != 'administrador':
        return jsonify({"success": False, "error": "Acesso negado."}), 403

    data_json = request.get_json() or {}
    registro_id = data_json.get("id")
    tipo = data_json.get("tipo")
    status = data_json.get("conferido")

    if not registro_id or not tipo:
        return jsonify({"success": False, "error": "Dados inválidos."}), 400

    if tipo == "Agendamento":
        registro = Agendamento.query.get(registro_id)
    else:
        registro = EsquecimentoPonto.query.get(registro_id)

    if not registro:
        return jsonify({"success": False, "error": "Registro não encontrado."}), 404

    registro.conferido = status
    db.session.commit()
    return jsonify({"success": True})

# ===========================================
# CRIAR ADMIN
# ===========================================
@app.route('/criar_admin')
def criar_admin():
    admin_email = 'nilcr94@gmail.com'
    admin_nome = 'Nilson Cruz'
    admin_registro = '43546'
    admin_senha = generate_password_hash('neto1536', method='pbkdf2:sha256')
    admin_tipo = 'administrador'

    admin = User.query.filter_by(email=admin_email).first()

    if not admin:
        novo_admin = User(
            nome=admin_nome,
            registro=admin_registro,
            email=admin_email,
            senha=admin_senha,
            tipo=admin_tipo
        )
        db.session.add(novo_admin)
        db.session.commit()
        return 'Conta administrador criada com sucesso!'
    else:
        return 'A conta administrador já existe.'


# ===========================================
# DEFERIR FOLGAS
# ===========================================
from sqlalchemy import asc
from collections import defaultdict


@app.route('/deferir_folgas', methods=['GET', 'POST'])
@login_required
def deferir_folgas():
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

    folgas = buscar_folgas()
    avisos = gerar_avisos(folgas)

    if request.method == 'POST':
        folga_id = request.form.get('folga_id')
        novo_status = request.form.get('status')
        folga = Agendamento.query.get(folga_id)

        if not folga:
            flash("Agendamento não encontrado.", "danger")
            return redirect(url_for('deferir_folgas'))

        usuario = User.query.get(folga.funcionario_id)

        # Banco de horas
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

        # Atualiza status da folga
        folga.status = novo_status

        try:
            db.session.commit()

            # 🔄 Sincroniza TRE depois de alterar o status, se for motivo TRE
            if folga.motivo == 'TRE':
                sync_tre_user(usuario.id)

            flash(
                f"A folga de {folga.funcionario.nome} foi {novo_status} com sucesso!",
                "success" if novo_status == 'deferido' else "danger"
            )

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
            enviar_email(usuario.email, assunto, mensagem_html, mensagem_texto)

        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar folga: {str(e)}", "danger")

        folgas = buscar_folgas()
        avisos = gerar_avisos(folgas)

    folgas_por_cargo = defaultdict(list)
    for f in folgas:
        cargo = f.funcionario.cargo or "Sem Cargo Definido"
        folgas_por_cargo[cargo].append(f)

    return render_template(
        'deferir_folgas.html',
        folgas_por_cargo=folgas_por_cargo,
        avisos=avisos
    )

# ===========================================
# HISTÓRICO / SALDOS (USUÁRIO)
# ===========================================
@app.route('/historico', methods=['GET'])
@login_required
def historico():
    sync_tre_user(current_user.id)

    usuario = User.query.get_or_404(current_user.id)
    ano = request.args.get("ano", type=int) or datetime.datetime.now().year

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

    tre_total = int(usuario.tre_total or 0)
    tre_usufruidas = int(usuario.tre_usufruidas or 0)
    tre_restantes = max(tre_total - tre_usufruidas, 0)

    total_minutos = int(usuario.banco_horas or 0)
    horas = total_minutos // 60
    minutos = total_minutos % 60
    banco_horas_formatado = f"{horas}h {minutos}min" if total_minutos > 0 else "0h 0min"

    ultimas_folgas = (
        Agendamento.query
        .filter_by(funcionario_id=current_user.id)
        .order_by(Agendamento.data.desc())
        .limit(10)
        .all()
    )

    minhas_tres = (
        TRE.query
        .filter(TRE.funcionario_id == current_user.id)
        .order_by(TRE.data_envio.desc(), TRE.id.desc())
        .all()
    )

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

    avisos = []
    if saldo_abonadas == 0:
        avisos.append("⚠️ Você atingiu o limite anual de folgas abonadas.")
    if tre_restantes > 0:
        avisos.append(f"🔔 Você ainda pode usufruir {tre_restantes} TRE(s).")
    if total_minutos > 300:
        avisos.append("ℹ️ Você possui muitas horas acumuladas no Banco de Horas.")

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


# ===========================================
# BANCO DE HORAS - CADASTRAR
# ===========================================
@app.route('/banco_horas/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_horas():
    if request.method == 'POST':
        nome = request.form['nome']
        registro = request.form['registro']
        quantidade_horas = int(request.form['quantidade_horas'])
        quantidade_minutos = int(request.form['quantidade_minutos'])
        data_realizacao = request.form['data_realizacao']
        motivo = request.form['motivo']

        try:
            data_realizacao = datetime.datetime.strptime(data_realizacao, '%Y-%m-%d').date()
        except ValueError:
            flash("Data inválida.", "danger")
            return redirect(url_for('cadastrar_horas'))

        total_minutos = (quantidade_horas * 60) + quantidade_minutos

        novo_banco_horas = BancoDeHoras(
            funcionario_id=current_user.id,
            horas=quantidade_horas,
            minutos=quantidade_minutos,
            total_minutos=total_minutos,
            data_realizacao=data_realizacao,
            motivo=motivo,
            status='Horas a Serem Deferidas'
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


@app.route('/banco_horas')
@login_required
def banco_horas():
    is_admin = current_user.tipo == 'administrador'
    return render_template('menu_banco_horas.html', is_admin=is_admin)


# ===========================================
# CONSULTAR HORAS (USUÁRIO)
# ===========================================
@app.route('/consultar_horas')
@login_required
def consultar_horas():
    # Ordena do mais recente para o mais antigo
    registros = (
        BancoDeHoras.query
        .filter_by(funcionario_id=current_user.id)
        .order_by(BancoDeHoras.data_realizacao.desc())
        .all()
    )

    horas_deferidas = 0
    minutos_deferidos = 0
    horas_em_espera = 0
    minutos_em_espera = 0

    # Soma das horas por status
    for registro in registros:
        h = registro.horas or 0
        m = registro.minutos or 0

        if registro.status == 'Deferido':
            horas_deferidas += h
            minutos_deferidos += m
        elif registro.status == 'Horas a Serem Deferidas':
            horas_em_espera += h
            minutos_em_espera += m

    # Normaliza minutos das horas deferidas
    horas_deferidas += minutos_deferidos // 60
    minutos_deferidos = minutos_deferidos % 60

    # Normaliza minutos das horas em espera
    horas_em_espera += minutos_em_espera // 60
    minutos_em_espera = minutos_em_espera % 60

    # Saldo atual em minutos (banco_horas guarda o saldo)
    saldo_min = int(current_user.banco_horas or 0)

    # Total de horas deferidas em minutos
    total_deferidas_min = horas_deferidas * 60 + minutos_deferidos

    # Horas já usufruídas = deferidas - saldo (nunca negativo)
    usadas_min = max(total_deferidas_min - saldo_min, 0)
    horas_usufruidas = usadas_min // 60
    minutos_usufruidos = usadas_min % 60

    # Horas a usufruir (saldo)
    horas_a_usufruir = saldo_min // 60
    minutos_a_usufruir = saldo_min % 60

    return render_template(
        'consultar_horas.html',
        registros=registros,
        horas_deferidas=horas_deferidas,
        minutos_deferidos=minutos_deferidos,
        horas_em_espera=horas_em_espera,
        minutos_em_espera=minutos_em_espera,
        horas_usufruidas=horas_usufruidas,
        minutos_usufruidos=minutos_usufruidos,
        horas_a_usufruir=horas_a_usufruir,
        minutos_a_usufruir=minutos_a_usufruir
    )

# ===========================================
# DEFERIR BANCO DE HORAS (ADMIN)
# ===========================================
@app.route('/banco_horas/deferir', methods=['GET', 'POST'])
@login_required
def deferir_horas():
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
            funcionario = User.query.get(banco_horas.funcionario_id)
            if funcionario:
                funcionario.banco_horas += banco_horas.total_minutos
            flash(f"Banco de horas de {banco_horas.funcionario.nome} deferido com sucesso!", "success")

        elif action == 'indeferir':
            banco_horas.status = 'Indeferido'
            flash(f"Banco de horas de {banco_horas.funcionario.nome} indeferido.", "danger")

        try:
            db.session.commit()
            registros = BancoDeHoras.query.filter_by(status='Horas a Serem Deferidas').all()
            return render_template('deferir_horas.html', registros=registros)

        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar status: {str(e)}", "danger")
            return redirect(url_for('deferir_horas'))

    return render_template('deferir_horas.html', registros=registros)


# ===========================================
# PERFIL
# ===========================================
@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    usuario = current_user

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
            usuario.celular = request.form.get('celular') or None
            usuario.data_nascimento = request.form.get('data_nascimento') or None
            usuario.cpf = request.form.get('cpf') or None
            usuario.rg = request.form.get('rg') or None
            usuario.data_emissao_rg = request.form.get('data_emissao_rg') or None
            usuario.orgao_emissor = request.form.get('orgao_emissor') or None
            usuario.graduacao = request.form.get('graduacao') or None
            usuario.cargo = request.form.get('cargo') or None

            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar o perfil: {str(e)}', 'danger')

        return redirect(url_for('perfil'))

    return render_template('perfil.html', usuario=usuario, cargos=cargos)


# =========================================== 
# RELATÓRIO HORAS EXTRAS (ADMIN)
# ===========================================
@app.route('/relatorio_horas_extras')
@login_required
def relatorio_horas_extras():
    if current_user.tipo != 'administrador':
        flash("Acesso negado. Você não tem permissão para acessar este relatório.", "danger")
        return redirect(url_for('index'))

    # Apenas usuários ativos, ordenados por nome
    usuarios = (
        User.query
        .filter(User.ativo.is_(True))
        .order_by(User.nome.asc())
        .all()
    )

    usuarios_relatorio = []
    for usuario in usuarios:
        # Garante que None não quebre a conta
        total_minutos = usuario.banco_horas or 0

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

# ===========================================
# ADMIN AGENDAMENTOS (AJAX)
# ===========================================
from sqlalchemy.orm import joinedload


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

    # 🔹 base: SOMENTE usuários ativos
    query = (
        User.query
        .join(Agendamento)
        .options(joinedload(User.agendamentos))
        .filter(User.ativo.is_(True))       # <<<<<<<<<< AQUI o filtro de ativo
    )

    # filtro por nome
    if nome:
        query = query.filter(User.nome.ilike(f"%{nome}%"))

    # filtro por cargo
    if cargo:
        query = query.filter(User.cargo == cargo)

    query = query.order_by(User.nome.asc()).distinct()

    funcionarios = query.paginate(page=page, per_page=per_page, error_out=False)

    dados = []
    for func in funcionarios.items:
        ags = []
        for ag in func.agendamentos:
            ag_status = (ag.status or "").strip().lower()

            # filtros de status aplicados sobre cada agendamento
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

        # só entra se tiver pelo menos um agendamento visível
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


@app.route('/admin/delete_agendamento/<int:id>', methods=['POST'])
@login_required
def admin_delete_agendamento(id):
    if current_user.tipo != 'administrador':
        return jsonify({"error": "Acesso negado"}), 403

    agendamento = Agendamento.query.get_or_404(id)
    db.session.delete(agendamento)
    db.session.commit()
    return jsonify({"success": True, "message": "Agendamento excluído com sucesso."})

# ===========================================
# RESUMO DE USUÁRIOS / SALDOS (ADMIN)
# ===========================================
@app.route('/user_info_all', methods=['GET'])
@login_required
def user_info_all():
    if getattr(current_user, 'tipo', None) != 'administrador':
        flash("Acesso negado. Esta página é exclusiva para administradores.", "danger")
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)

    # 🔹 Agora o padrão é 10, com limites de segurança
    PER_PAGE_DEFAULT = 10
    per_page = request.args.get('per_page', PER_PAGE_DEFAULT, type=int)
    if not per_page:
        per_page = PER_PAGE_DEFAULT
    per_page = max(5, min(per_page, 50))  # entre 5 e 50

    q = request.args.get('q', '', type=str).strip()
    status_filtro = request.args.get('status', 'ativos')

    def col(Model, *names):
        for n in names:
            if hasattr(Model, n):
                return getattr(Model, n)
        return None

    user_q = User.query

    # filtro de ativos/inativos
    if hasattr(User, 'ativo'):
        if status_filtro == 'ativos':
            user_q = user_q.filter(User.ativo.is_(True))
        elif status_filtro == 'inativos':
            user_q = user_q.filter(User.ativo.is_(False))
        else:
            # 'todos' → não filtra
            pass

    # busca por nome
    if q:
        user_q = user_q.filter(User.nome.ilike(f'%{q}%'))

    pagination = user_q.order_by(User.nome.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    users = pagination.items
    user_ids = [u.id for u in users] or [-1]

    # 🔄 Garante que os campos de TRE estejam sincronizados para estes usuários
    for u in users:
        try:
            sync_tre_user(u.id)
        except Exception:
            current_app.logger.exception("Erro ao sincronizar TRE do usuário %s", u.id)

    ABONADAS_POR_ANO = 6
    ano_atual = datetime.date.today().year

    resumos = {}
    for u in users:
        total_tre = u.tre_total or 0
        usadas_tre = u.tre_usufruidas or 0
        saldo_tre = total_tre - usadas_tre
        if saldo_tre < 0:
            saldo_tre = 0

        resumos[u.id] = {
            "abonadas_total": ABONADAS_POR_ANO,
            "abonadas_usadas": 0,
            "abonadas_restantes": ABONADAS_POR_ANO,
            "abonadas": ABONADAS_POR_ANO,

            "tre_registros": int(total_tre),
            "tre_saldo_horas": float(saldo_tre),

            "bh_registros": 0,
            "bh_saldo_horas": 0.0,

            "tre_agendamentos": [],
            "bh_agendamentos": [],
        }

    # ========================
    # ABONADAS
    # ========================
    try:
        Ag = Agendamento
        ag_uid  = col(Ag, 'funcionario_id', 'user_id', 'usuario_id')
        ag_stat = col(Ag, 'status')
        ag_data = getattr(Ag, 'data', None)
        ag_mot  = getattr(Ag, 'motivo', None)
        ag_tipoF = getattr(Ag, 'tipo_folga', None)

        if ag_uid and ag_stat and ag_data is not None:
            status_cond = func.lower(ag_stat) == 'deferido'

            ab_conds = []
            if ag_tipoF is not None:
                ab_conds.append(func.upper(ag_tipoF) == 'AB')
            if ag_mot is not None:
                ab_conds.append(func.upper(ag_mot) == 'AB')

            ab_filter = True if not ab_conds else or_(*ab_conds)

            rows = (
                db.session.query(
                    ag_uid.label('uid'),
                    func.count(Ag.id)
                )
                .filter(ag_uid.in_(user_ids))
                .filter(status_cond)
                .filter(ab_filter)
                .filter(func.extract('year', ag_data) == ano_atual)
                .group_by(ag_uid)
                .all()
            )

            for uid, qtd_usadas in rows:
                if uid in resumos:
                    usadas = int(qtd_usadas or 0)
                    restante = ABONADAS_POR_ANO - usadas
                    if restante < 0:
                        restante = 0

                    resumos[uid]['abonadas_usadas'] = usadas
                    resumos[uid]['abonadas_restantes'] = restante
                    resumos[uid]['abonadas'] = restante
    except Exception as e:
        current_app.logger.exception("Erro ao calcular abonadas: %s", e)

    # ========================
    # TRE - AGENDAMENTOS
    # ========================
    try:
        Ag = Agendamento
        ag_uid  = col(Ag, 'funcionario_id', 'user_id', 'usuario_id')
        ag_stat = col(Ag, 'status')
        ag_data = getattr(Ag, 'data', None)
        ag_mot  = getattr(Ag, 'motivo', None)
        ag_tipoF = getattr(Ag, 'tipo_folga', None)

        if ag_uid and ag_stat:
            status_cond = func.lower(ag_stat) == 'deferido'

            tre_conds = []
            if ag_tipoF is not None:
                tre_conds.append(func.upper(ag_tipoF) == 'TRE')
            if ag_mot is not None:
                tre_conds.append(func.upper(ag_mot) == 'TRE')

            tre_filter = True if not tre_conds else or_(*tre_conds)

            query = Ag.query.filter(ag_uid.in_(user_ids)).filter(status_cond).filter(tre_filter)
            if ag_data is not None:
                query = query.order_by(ag_data.asc())
            tre_rows = query.all()

            uid_attr_name = getattr(ag_uid, 'key', 'funcionario_id')

            for ag in tre_rows:
                uid_val = getattr(ag, uid_attr_name, None)
                if uid_val in resumos:
                    resumos[uid_val].setdefault('tre_agendamentos', []).append(ag)
    except Exception as e:
        current_app.logger.exception("Erro ao listar TRE: %s", e)

    # ========================
    # BH - AGENDAMENTOS
    # ========================
    try:
        Ag = Agendamento
        ag_uid  = col(Ag, 'funcionario_id', 'user_id', 'usuario_id')
        ag_stat = col(Ag, 'status')
        ag_data = getattr(Ag, 'data', None)
        ag_mot  = getattr(Ag, 'motivo', None)
        ag_tipoF = getattr(Ag, 'tipo_folga', None)

        if ag_uid and ag_stat:
            status_cond = func.lower(ag_stat) == 'deferido'

            bh_conds = []
            if ag_tipoF is not None:
                bh_conds.append(func.upper(ag_tipoF) == 'BH')
            if ag_mot is not None:
                bh_conds.append(func.upper(ag_mot) == 'BH')

            bh_filter = True if not bh_conds else or_(*bh_conds)

            query = Ag.query.filter(ag_uid.in_(user_ids)).filter(status_cond).filter(bh_filter)
            if ag_data is not None:
                query = query.order_by(ag_data.asc())
            bh_rows = query.all()

            uid_attr_name = getattr(ag_uid, 'key', 'funcionario_id')

            for ag in bh_rows:
                uid_val = getattr(ag, uid_attr_name, None)
                if uid_val in resumos:
                    resumos[uid_val].setdefault('bh_agendamentos', []).append(ag)
    except Exception as e:
        current_app.logger.exception("Erro ao listar Banco de Horas: %s", e)

    return render_template(
        'user_info_all.html',
        users=users,
        resumos=resumos,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=pagination.pages,
        total=pagination.total,
        q=q,
        status=status_filtro
    )

# ===========================================
# TOGGLE ATIVO / INATIVO
# ===========================================
@app.route('/toggle_user_ativo/<int:user_id>', methods=['POST'])
@login_required
def toggle_user_ativo(user_id):
    if getattr(current_user, 'tipo', None) != 'administrador':
        return jsonify(success=False, error='Acesso negado.'), 403

    user = User.query.get_or_404(user_id)

    current_app.logger.info(
        "Alterando status do usuário %s (antes: %s)",
        user.id, user.ativo
        )

    payload = request.get_json(silent=True) or {}
    novo_ativo = payload.get('ativo', None)

    if novo_ativo is not None:
        try:
            if isinstance(novo_ativo, (int, str)):
                user.ativo = bool(int(novo_ativo))
            else:
                user.ativo = bool(novo_ativo)
        except Exception:
            # fallback: inverte
            user.ativo = not bool(user.ativo)
    else:
        # sem campo 'ativo' explícito → apenas alterna
        user.ativo = not bool(user.ativo)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Erro ao salvar status do usuário %s: %s", user.id, e)
        return jsonify(success=False, error='Erro ao salvar no banco.'), 500

    current_app.logger.info(
        "Status do usuário %s alterado para %s",
        user.id, user.ativo
    )

    return jsonify(success=True, ativo=bool(user.ativo)), 200

# ===========================================
# CHECK UNIQUE
# ===========================================
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


# ===========================================
# AUXILIARES TRE / UPLOAD
# ===========================================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def sync_tre_user(usuario_id):
    """
    Sincroniza os campos tre_total / tre_usufruidas do usuário com base em:
      - TRE deferidas (tabela TRE)
      - Agendamentos de TRE deferidos (tabela Agendamento)
    """
    usuario = User.query.get(usuario_id)
    if not usuario:
        return 0, 0, 0

    # Total de dias deferidos (créditos) a partir da tabela TRE
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

    # Quantidade de dias já utilizados (agendamentos TRE deferidos)
    tre_usufruidas = db.session.query(
        func.count(Agendamento.id)
    ).filter(
        Agendamento.funcionario_id == usuario_id,
        Agendamento.motivo == "TRE",
        Agendamento.status == "deferido"
    ).scalar()

    tre_restantes = max((tre_total or 0) - (tre_usufruidas or 0), 0)

    usuario.tre_total = tre_total or 0
    usuario.tre_usufruidas = tre_usufruidas or 0
    db.session.commit()

    return usuario.tre_total, usuario.tre_usufruidas, tre_restantes


# ===========================================
# TRE - USUÁRIO
# ===========================================
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

        filename = secure_filename(f"{current_user.id}_{datetime.datetime.now():%Y%m%d%H%M%S}_{arquivo.filename}")
        save_path = os.path.join(app.root_path, UPLOAD_FOLDER)
        os.makedirs(save_path, exist_ok=True)
        arquivo.save(os.path.join(save_path, filename))

        nova = TRE(
            funcionario_id=current_user.id,
            dias_folga=dias_folga,
            arquivo_pdf=filename,
            status="pendente"
        )
        db.session.add(nova)
        db.session.commit()

        sync_tre_user(current_user.id)

        flash("TRE enviada para análise do administrador.", "success")
        return redirect(url_for("historico"))

    tres_ultimas = (TRE.query.filter_by(funcionario_id=current_user.id)
                    .order_by(TRE.data_envio.desc()).limit(3).all())
    return render_template("adicionar_tre.html", user=current_user, tres=tres_ultimas)


@app.route("/minhas_tres", methods=["GET"])
@login_required
def minhas_tres():
    minhas_tres = (TRE.query
                   .filter_by(funcionario_id=current_user.id)
                   .order_by(TRE.data_envio.desc())
                   .all())

    sync_tre_user(current_user.id)

    return render_template("minhas_tres.html", tres=minhas_tres, user=current_user)


@app.route("/download_tre/<int:tre_id>", methods=["GET"])
@login_required
def download_tre(tre_id):
    tre = TRE.query.get_or_404(tre_id)

    if tre.funcionario_id != current_user.id and current_user.tipo != "administrador":
        flash("Você não tem permissão para acessar este arquivo.", "danger")
        return redirect(url_for("minhas_tres"))

    directory = os.path.join(app.root_path, UPLOAD_FOLDER)
    return send_from_directory(directory, tre.arquivo_pdf, as_attachment=True)


# ===========================================
# TRE - ADMIN
# ===========================================
@app.route("/admin/tres", methods=["GET"])
@login_required
def admin_tres_list():
    if current_user.tipo != "administrador":
        flash("Acesso negado.", "danger")
        return redirect(url_for("index"))

    status = request.args.get("status", "pendente")
    busca = request.args.get("q", "").strip()

    # 🔹 Base: TRE apenas de usuários ATIVOS
    q = (
        TRE.query
        .join(User, User.id == TRE.funcionario_id)
        .filter(User.ativo.is_(True))          # <<--- filtro de ativos
    )

    if status in ("pendente", "deferida", "indeferida"):
        q = q.filter(TRE.status == status)

    if busca:
        like = f"%{busca}%"
        q = q.filter(or_(User.nome.ilike(like), User.registro.ilike(like)))

    tres = q.order_by(TRE.data_envio.desc()).all()
    return render_template("admin_tres.html", tres=tres, status=status)


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
        sync_tre_user(user.id)
        return jsonify({"success": True})
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Falha ao excluir a TRE."}), 500

# ===========================================
# CRIAR BANCO (UTILIDADE)
# ===========================================
@app.route('/criar_banco')
def criar_banco():
    try:
        db.create_all()
        return "Banco de dados criado com sucesso!"
    except Exception as e:
        return f"Erro ao criar o banco: {str(e)}"


# ===========================================
# HELPERS PDF
# ===========================================
def find_logo(filename: str):
    base = current_app.root_path
    candidatos = [
        os.path.join(base, filename),
        os.path.join(base, "static", filename),
        os.path.join(base, "static", "img", filename),
    ]
    for path in candidatos:
        if os.path.exists(path):
            return path
    return None


def format_banco_horas(minutos: int) -> str:
    minutos = minutos or 0
    sinal = "-" if minutos < 0 else ""
    m = abs(minutos)
    h = m // 60
    mi = m % 60
    return f"{sinal}{h}h {mi:02d}min"


def get_tre_agendamentos(user_id: int):
    Ag = Agendamento
    rows = (
        Ag.query
        .filter(Ag.funcionario_id == user_id)
        .filter(func.lower(Ag.status) == "deferido")
        .filter(
            or_(
                func.upper(Ag.motivo) == "TRE",
                func.upper(Ag.tipo_folga) == "TRE",
            )
        )
        .order_by(Ag.data.asc())
        .all()
    )
    result = []
    for ag in rows:
        data_str = ag.data.strftime("%d/%m/%Y") if ag.data else ""
        situacao = (ag.status or "").capitalize()
        result.append((data_str, situacao))
    return result


def get_bh_agendamentos(user_id: int):
    Ag = Agendamento
    rows = (
        Ag.query
        .filter(Ag.funcionario_id == user_id)
        .filter(func.lower(Ag.status) == "deferido")
        .filter(
            or_(
                func.upper(Ag.motivo) == "BH",
                func.upper(Ag.tipo_folga) == "BH",
            )
        )
        .order_by(Ag.data.asc())
        .all()
    )
    result = []
    for ag in rows:
        data_str = ag.data.strftime("%d/%m/%Y") if ag.data else ""
        situacao = (ag.status or "").capitalize()
        result.append((data_str, situacao))
    return result


def draw_header_footer(c, width, height):
    margin_x = 20 * mm
    margin_right = width - margin_x

    header_center_y = height - 20 * mm
    azul = colors.HexColor("#1a73e8")

    logo_h = 16 * mm
    escola_logo = find_logo("escola.png")
    municipio_logo = find_logo("municipio.png")

    logo_y = header_center_y - logo_h / 2

    if escola_logo:
        c.drawImage(
            escola_logo,
            margin_x,
            logo_y,
            width=logo_h,
            height=logo_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    if municipio_logo:
        c.drawImage(
            municipio_logo,
            margin_right - logo_h,
            logo_y,
            width=logo_h,
            height=logo_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    titulo_y = header_center_y + 6 * mm
    subtitulo_y = header_center_y
    data_y = header_center_y + 12 * mm

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(azul)
    c.drawCentredString(
        width / 2,
        titulo_y,
        "E.M. José Padin Mouta - Secretaria",
    )

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawCentredString(
        width / 2,
        subtitulo_y,
        "Relatório de Servidores - Portal do Servidor",
    )

    c.setFont("Helvetica", 8)
    c.drawRightString(
        margin_right,
        data_y,
        datetime.datetime.now().strftime("Emitido em %d/%m/%Y %H:%M"),
    )

    line_y = header_center_y - 10 * mm
    c.setStrokeColor(azul)
    c.setLineWidth(0.8)
    c.line(margin_x, line_y, margin_right, line_y)

    footer_base_y = 15 * mm
    footer_line_y = footer_base_y + 4 * mm

    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.6)
    c.line(margin_x, footer_line_y, margin_right, footer_line_y)

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    footer_text = (
        "E.M. José Padin Mouta • R. Bororós, 150 - Vila Tupi, "
        "Praia Grande - SP, 11703-390"
    )
    c.drawCentredString(width / 2, footer_base_y + 1 * mm, footer_text)

    c.drawRightString(
        margin_right,
        footer_base_y - 2 * mm,
        f"Página {c.getPageNumber()}",
    )

    content_start_y = line_y - 8 * mm
    return content_start_y


def draw_simple_table(c, x, y, col_widths, headers, rows):
    row_height = 6 * mm
    total_width = sum(col_widths)
    total_rows = 1 + len(rows)
    table_height = total_rows * row_height

    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.5)
    c.rect(x, y - table_height, total_width, table_height, stroke=1, fill=0)

    for i in range(total_rows + 1):
        c.line(x, y - i * row_height, x + total_width, y - i * row_height)

    running_x = x
    for w in col_widths[:-1]:
        running_x += w
        c.line(running_x, y, running_x, y - table_height)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    header_y = y - 0.75 * row_height
    col_x = x + 2 * mm
    for idx, h in enumerate(headers):
        c.drawString(col_x, header_y, h)
        col_x += col_widths[idx]

    c.setFont("Helvetica", 8)
    for idx, row in enumerate(rows):
        row_y = y - (idx + 1.75) * row_height
        col_x = x + 2 * mm
        for col_idx, value in enumerate(row):
            c.drawString(col_x, row_y, str(value))
            col_x += col_widths[col_idx]

    return y - table_height


def draw_user_page(c: canvas.Canvas, user: User, width, height):
    margin_left = 20 * mm
    margin_right = width - 20 * mm

    azul = colors.HexColor("#1a73e8")
    roxo = colors.HexColor("#7b3fe0")

    y = draw_header_footer(c, width, height)

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)
    c.drawString(margin_left, y, f"Servidor: {user.nome or '—'}")
    y -= 6 * mm

    c.setFont("Helvetica", 9)
    campos = [
        ("Registro funcional", user.registro or "—"),
        ("CPF", user.cpf or "—"),
        ("Cargo", user.cargo or "—"),
        (
            "Data de nascimento",
            user.data_nascimento.strftime("%d/%m/%Y")
            if user.data_nascimento
            else "—",
        ),
        ("RG", user.rg or "—"),
        (
            "Data emissão RG",
            user.data_emissao_rg.strftime("%d/%m/%Y")
            if user.data_emissao_rg
            else "—",
        ),
        ("Órgão emissor", user.orgao_emissor or "—"),
        ("Celular", user.celular or "—"),
        ("E-mail", user.email or "—"),
        ("Graduação", user.graduacao or "—"),
    ]

    for label, valor in campos:
        c.drawString(margin_left, y, f"{label}: {valor}")
        y -= 4.5 * mm

    y -= 3 * mm
    c.setStrokeColor(azul)
    c.setLineWidth(0.6)
    c.line(margin_left, y, margin_right, y)
    y -= 6 * mm

    total_tre = user.tre_total or 0
    usadas_tre = user.tre_usufruidas or 0
    saldo_tre = max(total_tre - usadas_tre, 0)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(azul)
    c.drawString(margin_left, y, "TRE")
    y -= 5 * mm

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    c.drawString(
        margin_left,
        y,
        f"Total: {total_tre} dias | A usufruir: {saldo_tre} dias | Usadas: {usadas_tre} dias",
    )
    y -= 7 * mm

    tre_rows = get_tre_agendamentos(user.id)
    if tre_rows:
        y = draw_simple_table(
            c,
            margin_left,
            y,
            [35 * mm, (margin_right - margin_left) - 35 * mm],
            ["Data", "Situação"],
            tre_rows,
        )
        y -= 6 * mm
    else:
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(
            margin_left, y, "Nenhum agendamento TRE deferido cadastrado."
        )
        y -= 8 * mm

    y -= 4 * mm
    c.setStrokeColor(roxo)
    c.setLineWidth(0.6)
    c.line(margin_left, y, margin_right, y)
    y -= 6 * mm

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(roxo)
    c.drawString(margin_left, y, "Banco de Horas")
    y -= 5 * mm

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    saldo_bh_str = format_banco_horas(user.banco_horas)
    c.drawString(margin_left, y, f"Saldo atual: {saldo_bh_str}")
    y -= 7 * mm

    bh_rows = get_bh_agendamentos(user.id)
    if bh_rows:
        y = draw_simple_table(
            c,
            margin_left,
            y,
            [35 * mm, (margin_right - margin_left) - 35 * mm],
            ["Data", "Situação"],
            bh_rows,
        )
    else:
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(
            margin_left, y, "Nenhum agendamento BH deferido cadastrado."
        )


# ===========================================
# RELATÓRIO PDF (ADMIN)
# ===========================================
@app.route('/user_info_report')
@login_required
def user_info_report():
    if getattr(current_user, 'tipo', None) != 'administrador':
        flash("Acesso negado. Esta página é exclusiva para administradores.", "danger")
        return redirect(url_for('index'))

    users = User.query.order_by(User.nome.asc()).all()
    if not users:
        flash("Nenhum usuário encontrado para gerar o relatório.", "warning")
        return redirect(url_for('user_info_all'))

    # 🔄 Antes de gerar o PDF, garante que os saldos de TRE estejam atualizados
    for u in users:
        try:
            sync_tre_user(u.id)
        except Exception:
            current_app.logger.exception(
                "Erro ao sincronizar TRE do usuário %s no relatório.", u.id
            )

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    total = len(users)
    for idx, user in enumerate(users):
        draw_user_page(c, user, width, height)
        if idx < total - 1:
            c.showPage()

    c.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="relatorio_servidores.pdf",
        mimetype="application/pdf"
    )

# ===========================================
# LOGIN MANAGER
# ===========================================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ===========================================
# MAIN
# ===========================================
if __name__ == '__main__':
    app.run(debug=True)
