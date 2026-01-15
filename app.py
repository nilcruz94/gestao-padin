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
import ssl
import calendar
import datetime
from datetime import timedelta, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy import func, or_, case, asc
from sqlalchemy.orm import joinedload, selectinload

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors

# ======== CSRF / Segurança =========
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from markupsafe import Markup

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

# Proteções de cookie/sessão recomendadas
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# Em produção, ative Secure (HTTPS): app.config['SESSION_COOKIE_SECURE'] = True

# Flask-WTF CSRF
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 60 * 60 * 8  # 8 horas
csrf = CSRFProtect(app)

# Torna csrf_token() e csrf_field() disponíveis nos templates Jinja
@app.context_processor
def inject_csrf_token():
    return dict(
        csrf_token=lambda: generate_csrf(),
        csrf_field=lambda: Markup(
            f'<input type="hidden" name="csrf_token" value="{generate_csrf()}">'
        ),
    )

# Segurança/Links externos para e-mail
app.config.setdefault("SECURITY_PASSWORD_SALT", "senha-reset-salt-robusta")
app.config.setdefault("PREFERRED_URL_SCHEME", "https")

# ===========================================
# Config Uploads (Ajustado p/ TRE persistente)
# ===========================================
from pathlib import Path

ALLOWED_EXTENSIONS = {"pdf"}

_raw_env_upload = os.getenv("UPLOAD_FOLDER")
if _raw_env_upload:
    _env_upload = _raw_env_upload
    if not _env_upload.startswith("/"):
        _env_upload = "/" + _env_upload.lstrip("/")
else:
    _env_upload = "uploads/tre"

BASE_UPLOAD_DIR = Path(_env_upload).resolve()
BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.config["UPLOAD_FOLDER"] = str(BASE_UPLOAD_DIR)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB

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
SMTP_PASS = "smqvqabjbgoyzhml"   # 🔒 Ideal: usar variável de ambiente!
MAIL_FROM = f"Portal do Servidor <{SMTP_USER}>"

# --- Diag rápido de SMTP (opcional) ---
@app.route("/_smtp_diag")
def _smtp_diag():
    ctx = ssl.create_default_context()
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=25) as s:
            s.ehlo()
            s.starttls(context=ctx)
            s.ehlo()
            s.login(SMTP_USER, SMTP_PASS)
        return "SMTP OK (587/STARTTLS)"
    except smtplib.SMTPAuthenticationError as e:
        return f"SMTP FAIL AUTH (587): {e}", 500
    except Exception as e:
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, 465, context=ctx, timeout=25) as s:
                s.ehlo()
                s.login(SMTP_USER, SMTP_PASS)
            return "SMTP OK (465/SSL) — fallback"
        except Exception as e2:
            return f"SMTP FAIL: {type(e).__name__}: {e} | Fallback: {type(e2).__name__}: {e2}", 500

# ===========================================
# TERMO DE USO — versão vigente
# ===========================================
TERMO_VERSION = "2025-01-15"

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
    versao_termo = db.Column(db.String(20), default=None)

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
    status = db.Column(db.String(50), default="Pendente")
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

    funcionario = db.relationship(
        'User',
        backref=db.backref('tres', lazy=True),
        foreign_keys=[funcionario_id],
        lazy=True
    )
    validador = db.relationship(
        'User',
        backref=db.backref('tres_validadas', lazy=True),
        foreign_keys=[validado_por_id],
        lazy=True
    )

# ===========================================
# E-MAIL — Função genérica (corrigida e robusta)
# ===========================================
def enviar_email(destinatario, assunto, mensagem_html, mensagem_texto=None):
    """
    Envia um e-mail via Gmail:
      - 587 + STARTTLS (padrão), com fallback para 465/SSL
      - Envelope sender = SMTP_USER (sem 'Display Name')
      - Header From = MAIL_FROM (com nome amigável)
    Lança exceção em falha.
    """
    if not destinatario:
        raise ValueError("destinatario vazio")

    msg = MIMEMultipart("alternative")
    msg['From'] = MAIL_FROM
    msg['To'] = destinatario
    msg['Subject'] = assunto or "(sem assunto)"

    if not mensagem_texto:
        mensagem_texto = "Por favor, visualize este e-mail em um cliente que suporte HTML."

    msg.attach(MIMEText(mensagem_texto, 'plain', 'utf-8'))
    msg.attach(MIMEText(mensagem_html or "", 'html', 'utf-8'))

    ctx = ssl.create_default_context()

    # Tentativa 1: 587 + STARTTLS
    try:
        current_app.logger.info("SMTP[TLS587] host=%s port=%s user=%s from=%s",
                                SMTP_SERVER, SMTP_PORT, SMTP_USER, MAIL_FROM)
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=25) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            # Envelope sender precisa ser o e-mail puro, sem display name
            server.sendmail(SMTP_USER, [destinatario], msg.as_string())
            return
    except smtplib.SMTPAuthenticationError as e:
        # Falha de autenticação (535, etc.) — não adianta fallback
        current_app.logger.error("SMTP auth error (587/TLS): %s", e)
        raise
    except Exception as e:
        # Timeout, network reset, etc. — tenta 465/SSL
        current_app.logger.warning("SMTP 587/TLS falhou, tentando 465/SSL: %s", e)

    # Tentativa 2: 465 + SSL
    with smtplib.SMTP_SSL(SMTP_SERVER, 465, context=ctx, timeout=25) as server:
        current_app.logger.info("SMTP[SSL465] host=%s port=%s user=%s from=%s",
                                SMTP_SERVER, 465, SMTP_USER, MAIL_FROM)
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [destinatario], msg.as_string())

# ===== Helpers de TERMO =====
def _tem_termo_vigente(user) -> bool:
    return bool(user) and (user.versao_termo or "").strip() == TERMO_VERSION

# ===========================================
# Middlewares de segurança e CSRF
# ===========================================
@app.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    token = generate_csrf()
    resp = jsonify({'csrf_token': token})
    resp.set_cookie('csrf_token', token, samesite='Lax', secure=False, httponly=False)
    return resp

from urllib.parse import urlparse

@app.before_request
def _enforce_same_origin_on_unsafe():
    if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
        origin = request.headers.get('Origin')
        referer = request.headers.get('Referer')
        host = request.host_url.rstrip('/')
        if origin and not origin.startswith(host):
            abort(403)
        if referer:
            parsed = urlparse(referer)
            ref = f"{parsed.scheme}://{parsed.netloc}"
            if not ref.startswith(request.host_url.rstrip('/')):
                abort(403)

@app.after_request
def _set_security_headers(resp):
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    return resp

# Garante um cookie csrf_token disponível para front-end (AJAX)
@app.after_request
def _ensure_csrf_cookie(resp):
    try:
        token = generate_csrf()
        resp.set_cookie('csrf_token', token, samesite='Lax', secure=False, httponly=False)
    except Exception:
        pass
    return resp

@app.before_request
def _require_terms_acceptance():
    try:
        is_auth = getattr(current_user, "is_authenticated", False)
    except Exception:
        is_auth = False

    if not is_auth:
        return

    endpoint = (request.endpoint or "").lower()
    rotas_livres = {
        "login",
        "logout",
        "termo_uso",
        "aceitar_termo",
        "get_csrf_token",
        "recuperar_senha",
        "redefinir_senha",
        "static",
        "_smtp_diag",
    }
    if endpoint in rotas_livres:
        return

    if _tem_termo_vigente(current_user):
        return

    try:
        if current_user.aceitou_termo:
            current_user.aceitou_termo = False
            db.session.commit()
    except Exception:
        db.session.rollback()

    return redirect(url_for("termo_uso"))

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

            if not _tem_termo_vigente(user):
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
            current_user.versao_termo = TERMO_VERSION
            db.session.commit()
            flash("Termo aceito com sucesso.", "success")
            return redirect(url_for('index'))

        elif acao == 'nao_aceito':
            flash("Você precisa aceitar o termo para usar o sistema.", "danger")
            logout_user()
            return redirect(url_for('login'))

    if _tem_termo_vigente(current_user):
        return redirect(url_for('index'))

    return render_template('termo_uso.html', termo_versao=TERMO_VERSION)


@app.route('/aceitar_termo', methods=['POST'])
@login_required
def aceitar_termo():
    current_user.aceitou_termo = True
    current_user.versao_termo = TERMO_VERSION
    db.session.commit()
    flash('Termo de uso aceito com sucesso.', 'success')
    return redirect(url_for('index'))

# ======================================================
# RECUPERAÇÃO / REDEFINIÇÃO DE SENHA POR E-MAIL (Gmail)
# ======================================================
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

RESET_TOKEN_MAX_AGE = int(os.getenv("RESET_TOKEN_MAX_AGE", "3600"))  # 1 hora

def _get_serializer() -> URLSafeTimedSerializer:
    secret_key = app.config["SECRET_KEY"]
    return URLSafeTimedSerializer(secret_key)

def generate_reset_token(user_id: int) -> str:
    s = _get_serializer()
    return s.dumps({"uid": user_id}, salt=app.config["SECURITY_PASSWORD_SALT"])

def verify_reset_token(token: str) -> int | None:
    s = _get_serializer()
    try:
        data = s.loads(
            token,
            salt=app.config["SECURITY_PASSWORD_SALT"],
            max_age=RESET_TOKEN_MAX_AGE
        )
        return int(data.get("uid", 0))
    except SignatureExpired:
        flash("O link de redefinição expirou. Solicite um novo.", "warning")
        return None
    except BadSignature:
        flash("Link de redefinição inválido. Solicite um novo.", "danger")
        return None
    except Exception:
        flash("Não foi possível validar o link de redefinição.", "danger")
        return None

def send_password_reset_email(user) -> None:
    token = generate_reset_token(user.id)
    reset_url = url_for("redefinir_senha", token=token, _external=True)

    subject = "Redefinição de Senha — Portal do Servidor"
    text_body = (
        "Você solicitou a redefinição de senha.\n\n"
        f"Acesse o link abaixo para criar uma nova senha (válido por {RESET_TOKEN_MAX_AGE//60} minutos):\n"
        f"{reset_url}\n\n"
        "Se você não solicitou, ignore este e-mail."
    )
    html_body = f"""
      <p>Olá, <strong>{user.nome or 'Servidor(a)'}</strong>.</p>
      <p>Recebemos um pedido para redefinir sua senha do <strong>Portal do Servidor</strong>.</p>
      <p>Use o botão/link abaixo (válido por <strong>{RESET_TOKEN_MAX_AGE//60} minutos</strong>):</p>
      <p>
        <a href="{reset_url}" style="display:inline-block;background:#2563eb;color:#fff;
           text-decoration:none;padding:10px 16px;border-radius:8px;font-weight:700">
          Redefinir senha
        </a>
      </p>
      <p>Se preferir, copie e cole esta URL no navegador:</p>
      <p style="word-break:break-all;"><a href="{reset_url}">{reset_url}</a></p>
      <hr>
      <p style="color:#6b7280;font-size:12px">Mensagem automática • Não responder</p>
    """
    enviar_email(user.email, subject, html_body, text_body)

@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    """
    Formulário (e-mail + registro). Se POST válido, envia e-mail com link.
    Resposta sempre genérica (não revela se usuário existe).
    """
    if request.method == 'POST':
        email = (request.form.get('email') or "").strip().lower()
        registro = (request.form.get('registro') or "").strip()

        usuario = User.query.filter(
            User.email.ilike(email),
            User.registro == registro
        ).first()

        try:
            if usuario and usuario.email:
                send_password_reset_email(usuario)
            flash("Se os dados conferirem, enviaremos um e-mail com instruções.", "info")
            return redirect(url_for('login'))
        except smtplib.SMTPAuthenticationError:
            current_app.logger.exception("SMTPAuthenticationError ao enviar e-mail de redefinição")
            flash("Não foi possível enviar o e-mail no momento. Verifique as credenciais SMTP.", "danger")
        except Exception:
            current_app.logger.exception("Erro ao enviar e-mail de redefinição")
            flash("Não foi possível enviar o e-mail no momento. Tente novamente.", "danger")

    return render_template('recuperar_senha.html')

@app.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    """
    Valida o token e permite a redefinição da senha sem autenticação prévia.
    """
    user_id = verify_reset_token(token)
    if not user_id:
        return redirect(url_for('recuperar_senha'))

    usuario = User.query.get(user_id)
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for('recuperar_senha'))

    if request.method == 'POST':
        nova_senha = (request.form.get('nova_senha') or "").strip()
        confirmar  = (request.form.get('confirmar_senha') or "").strip()

        if len(nova_senha) < 6:
            flash("A nova senha deve ter pelo menos 6 caracteres.", "warning")
        elif nova_senha != confirmar:
            flash("As senhas não coincidem.", "danger")
        else:
            usuario.senha = generate_password_hash(nova_senha)
            db.session.commit()
            flash("Senha redefinida com sucesso! Faça login.", "success")
            return redirect(url_for('login'))

    return render_template('redefinir_senha.html', token=token)

@app.route('/logout', methods=['POST'])
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
                func.extract('year', Agendamento.data) == data_folga.year,
                func.extract('month', Agendamento.data) == data_folga.month
            ).first()
            if agendamento_existente and agendamento_existente.status != 'indeferido':
                flash("Você já possui um agendamento 'AB' aprovado ou em análise neste mês.", "danger")
                return render_template('agendar.html')

            agendamentos_ab_deferidos = Agendamento.query.filter(
                Agendamento.funcionario_id == current_user.id,
                Agendamento.motivo == 'AB',
                func.extract('year', Agendamento.data) == data_folga.year,
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

    estados_validos = ['em_espera', 'deferido', 'indeferido']

    agendamentos = (
        Agendamento.query
        .filter(Agendamento.data >= first_day_of_month,
                Agendamento.data <= last_day_of_month)
        .filter(Agendamento.status.in_(estados_validos))
        .filter(~func.lower(Agendamento.motivo).like('%ajuste%'))
        .filter(~func.lower(Agendamento.motivo).like('%recuper%'))
        .all()
    )

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
# Helpers (relatórios; CSRF para AJAX)
# ===========================================
try:
    from flask_wtf.csrf import validate_csrf
except Exception:
    validate_csrf = None

def _periodo_pagamento_10a9(mes: int, ano: int) -> tuple[datetime.datetime, datetime.datetime]:
    if mes < 1 or mes > 12:
        raise ValueError("Mês inválido (1-12)")
    if mes == 1:
        mes_anterior = 12
        ano_anterior = ano - 1
    else:
        mes_anterior = mes - 1
        ano_anterior = ano
    inicio = datetime.datetime(ano_anterior, mes_anterior, 10, 0, 0, 0)
    fim    = datetime.datetime(ano, mes, 9, 23, 59, 59)
    return inicio, fim

def _csrf_ok_from_header(req: request) -> bool:
    if validate_csrf is None:
        return True
    token = req.headers.get("X-CSRFToken") or req.headers.get("X-CSRF-Token")
    if not token:
        return False
    try:
        validate_csrf(token)
        return True
    except Exception:
        return False

# ===========================================
# RELATÓRIO PONTO (10 a 9)
# ===========================================
@app.route('/relatorio_ponto')
@login_required
def relatorio_ponto():
    if getattr(current_user, "tipo", "").lower() != 'administrador':
        flash("Acesso negado.", "danger")
        return redirect(url_for('index'))

    mes_selecionado = request.args.get('mes', type=int)
    ano_selecionado = request.args.get('ano', type=int) or datetime.datetime.now().year

    registros = []
    periodo_inicio = periodo_fim = None

    if mes_selecionado:
        try:
            periodo_inicio, periodo_fim = _periodo_pagamento_10a9(mes_selecionado, ano_selecionado)
        except ValueError:
            flash("Parâmetros de mês/ano inválidos.", "danger")
            return redirect(url_for('relatorio_ponto'))

        agendamentos = (
            Agendamento.query
            .join(Agendamento.funcionario)
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
                'conferido': bool(getattr(ag, "conferido", False))
            })

        esquecimentos = (
            EsquecimentoPonto.query
            .join(EsquecimentoPonto.usuario)
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
                'conferido': bool(getattr(esc, "conferido", False))
            })

        registros.sort(
            key=lambda r: (
                (r['usuario'].nome or '').casefold().strip(),
                r['data'] or datetime.datetime.min
            )
        )

    return render_template(
        'relatorio_ponto.html',
        registros=registros,
        mes_selecionado=mes_selecionado,
        ano_selecionado=ano_selecionado,
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim
    )

# Exempt + check manual de CSRF via header
@csrf.exempt
@app.route('/atualizar_conferido', methods=['POST'])
@login_required
def atualizar_conferido():
    if getattr(current_user, "tipo", "").lower() != 'administrador':
        return jsonify({"success": False, "error": "Acesso negado."}), 403

    if not _csrf_ok_from_header(request):
        return jsonify({"success": False, "error": "CSRF inválido ou ausente."}), 400

    data_json = request.get_json(silent=True) or {}
    registro_id = data_json.get("id")
    tipo = data_json.get("tipo")
    status = data_json.get("conferido")

    if not registro_id or not tipo or status is None:
        return jsonify({"success": False, "error": "Dados inválidos."}), 400

    tipo_norm = str(tipo).strip().lower()
    if tipo_norm in ("agendamento",):
        registro = Agendamento.query.get(registro_id)
    elif tipo_norm in ("esquecimento de ponto", "esquecimento", "esquecimento_ponto"):
        registro = EsquecimentoPonto.query.get(registro_id)
    else:
        return jsonify({"success": False, "error": "Tipo inválido."}), 400

    if not registro:
        return jsonify({"success": False, "error": "Registro não encontrado."}), 404

    registro.conferido = bool(status)
    db.session.commit()

    return jsonify({
        "success": True,
        "id": registro_id,
        "tipo": tipo,
        "conferido": bool(registro.conferido)
    })

# ===========================================
# DEFERIR FOLGAS
# ===========================================
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
                    </p>
                    <p>Agradecemos a colaboração e estamos à disposição para quaisquer esclarecimentos adicionais.</p>
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

Informamos que a sua solicitação de FOLGA para o dia {folga.data.strftime('%d/%m/%Y')} foi DEFERIDA pela direção da unidade escolar.

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
                  <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5%;">
                    <p>Prezado(a) Senhor(a) <strong>{usuario.nome}</strong>,</p>
                    <p>
                      Após análise criteriosa, a sua solicitação de 
                      <strong style="color: #007bff;">FOLGA</strong> para o dia 
                      <strong style="color: #007bff;">{folga.data.strftime('%d/%m/%Y')}</strong> não pôde ser 
                      <strong style="color: #d9534f;">DEFERIDA</strong>.
                    </p>
                    <p>Estamos à disposição para eventuais esclarecimentos.</p>
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

Após análise criteriosa, a sua solicitação de FOLGA para o dia {folga.data.strftime('%d/%m/%Y')} não pôde ser DEFERIDA.

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

    for registro in registros:
        h = registro.horas or 0
        m = registro.minutos or 0

        if registro.status == 'Deferido':
            horas_deferidas += h
            minutos_deferidos += m
        elif registro.status == 'Horas a Serem Deferidas':
            horas_em_espera += h
            minutos_em_espera += m

    horas_deferidas += minutos_deferidos // 60
    minutos_deferidos = minutos_deferidos % 60

    horas_em_espera += minutos_em_espera // 60
    minutos_em_espera = minutos_em_espera % 60

    saldo_min = int(current_user.banco_horas or 0)
    total_deferidas_min = horas_deferidas * 60 + minutos_deferidos

    usadas_min = max(total_deferidas_min - saldo_min, 0)
    horas_usufruidas = usadas_min // 60
    minutos_usufruidos = usadas_min % 60

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

# ============================
# INSERIR BANCO DE HORAS (ADMIN)
# ============================
import datetime as dt

def _normalize_status_bh(raw: str) -> str:
    s = (raw or "").strip().lower()
    if s.startswith("deferid") or s in {"aprovado", "aprovada"}:
        return "Deferido"
    if s.startswith("indeferid") or s in {"rejeitado", "rejeitada", "negado", "negada"}:
        return "Indeferido"
    if any(x in s for x in ["anal", "espera", "aguard", "pendent"]):
        return "Em análise"
    return "Em análise"

def _recalcular_saldo_minutos(funcionario_id: int):
    creditos_min = (
        db.session.query(
            func.coalesce(func.sum(BancoDeHoras.horas * 60 + BancoDeHoras.minutos), 0)
        )
        .filter(BancoDeHoras.funcionario_id == funcionario_id)
        .filter(func.lower(BancoDeHoras.status).like('deferid%'))
        .filter(func.upper(BancoDeHoras.motivo) != 'BH')
        .scalar()
    )

    debitos_min = (
        db.session.query(
            func.coalesce(func.sum(Agendamento.horas * 60 + Agendamento.minutos), 0)
        )
        .filter(Agendamento.funcionario_id == funcionario_id)
        .filter(func.lower(Agendamento.status).like('deferid%'))
        .filter(func.lower(Agendamento.motivo) == 'bh')
        .scalar()
    )

    saldo = int(creditos_min) - int(debitos_min)
    u = User.query.get(funcionario_id)
    if u:
        u.banco_horas = saldo
        db.session.commit()
    return saldo

@app.route('/banco_horas/inserir', methods=['GET', 'POST'])
@login_required
def inserir_bh_admin():
    if current_user.tipo != 'administrador':
        flash("Acesso negado.", "danger")
        return redirect(url_for('banco_horas'))

    if request.method == 'POST':
        try:
            funcionario_id = int(request.form.get('funcionario_id', '0') or 0)
        except ValueError:
            funcionario_id = 0

        data_realizacao_raw = request.form.get('data_realizacao', '')
        motivo = (request.form.get('motivo', '') or '').strip()
        status_raw = request.form.get('status', 'Deferido')
        horas_raw = request.form.get('horas', '0')
        minutos_raw = request.form.get('minutos', '0')

        if not funcionario_id:
            flash("Selecione um servidor.", "warning")
            return redirect(url_for('inserir_bh_admin'))

        try:
            data_realizacao = dt.datetime.strptime(data_realizacao_raw, "%Y-%m-%d").date()
        except Exception:
            flash("Data inválida.", "warning")
            return redirect(url_for('inserir_bh_admin'))

        try:
            horas = max(0, int(horas_raw or 0))
            minutos = max(0, int(minutos_raw or 0))
        except ValueError:
            flash("Informe horas e minutos válidos.", "warning")
            return redirect(url_for('inserir_bh_admin'))

        if minutos >= 60:
            flash("Minutos devem estar entre 0 e 59.", "warning")
            return redirect(url_for('inserir_bh_admin'))

        if horas == 0 and minutos == 0:
            flash("Informe uma quantidade de tempo maior que zero.", "warning")
            return redirect(url_for('inserir_bh_admin'))

        if not motivo:
            flash("Informe um motivo (evite usar 'BH' aqui).", "warning")
            return redirect(url_for('inserir_bh_admin'))

        if motivo.upper() == 'BH':
            flash("Motivo 'BH' é reservado para folgas/consumos. Use um motivo descritivo do crédito.", "warning")
            return redirect(url_for('inserir_bh_admin'))

        status = _normalize_status_bh(status_raw)

        novo = BancoDeHoras(
            funcionario_id=funcionario_id,
            horas=horas,
            minutos=minutos,
            total_minutos=horas * 60 + minutos,
            data_realizacao=data_realizacao,
            status=status,
            motivo=motivo,
            usufruido=False,
        )
        db.session.add(novo)
        db.session.commit()

        saldo = _recalcular_saldo_minutos(funcionario_id)

        flash(
            f"Crédito inserido com sucesso ({horas}h {minutos:02d}m para o servidor #{funcionario_id}). "
            f"Saldo atual (min): {saldo}.",
            "success"
        )
        return redirect(url_for('inserir_bh_admin'))

    usuarios = (
        User.query
        .filter(User.ativo.is_(True))
        .order_by(User.nome.asc())
        .all()
    )
    return render_template(
        'inserir_bh_admin.html',
        usuarios=usuarios,
        hoje=dt.date.today(),
        padrao_status='Deferido'
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
def _normalize_status(raw: str) -> str:
    s = (raw or "").strip().lower()
    if s.startswith("deferid") or s in {"aprovado", "aprovada"}:
        return "Deferido"
    if s.startswith("indeferid") or s in {"rejeitado", "rejeitada", "negado", "negada"}:
        return "Indeferido"
    if any(x in s for x in ["anal", "espera", "aguard", "pendent", "serem deferid", "deferir"]):
        return "Em análise"
    return "Em análise"

def _parse_date(s: str):
    if not s:
        return None
    try:
        return dt.datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None

def _in_range(date_obj: dt.date, inicio: dt.date | None, fim: dt.date | None) -> bool:
    if date_obj is None:
        return False
    if inicio and date_obj < inicio:
        return False
    if fim and date_obj > fim:
        return False
    return True

def _min_total(horas, minutos) -> int:
    return int(horas or 0) * 60 + int(minutos or 0)

@app.route('/relatorio_horas_extras')
@login_required
def relatorio_horas_extras():
    if current_user.tipo != 'administrador':
        flash("Acesso negado. Você não tem permissão para acessar este relatório.", "danger")
        return redirect(url_for('index'))

    inicio = _parse_date(request.args.get("inicio"))
    fim = _parse_date(request.args.get("fim"))
    if inicio and fim and fim < inicio:
        inicio, fim = fim, inicio

    usuarios = (
        User.query
        .options(selectinload(User.banco_de_horas))
        .filter(User.ativo.is_(True))
        .order_by(User.nome.asc())
        .all()
    )
    user_ids = [u.id for u in usuarios] or [-1]

    ags_all = (
        Agendamento.query
        .filter(Agendamento.funcionario_id.in_(user_ids))
        .filter(func.lower(func.trim(Agendamento.motivo)) == 'bh')
        .all()
    )
    ags_by_user = defaultdict(list)
    for a in ags_all:
        ags_by_user[a.funcionario_id].append(a)

    usuarios_relatorio = []

    for u in usuarios:
        regs = []
        total_cadastradas_min = 0

        for r in (u.banco_de_horas or []):
            motivo = (r.motivo or '').strip()
            motivo_norm = motivo.strip().lower()
            data_r = r.data_realizacao

            is_ajuste = bool(getattr(r, 'is_ajuste', False))
            if is_ajuste:
                continue

            if motivo_norm == 'bh':
                continue

            if (not inicio and not fim) or _in_range(data_r, inicio, fim):
                regs.append({
                    "data_realizacao": data_r,
                    "motivo": motivo,
                    "horas": int(r.horas or 0),
                    "minutos": int(r.minutos or 0),
                    "status_label": _normalize_status(getattr(r, 'status', '') or ''),
                })

            if _normalize_status(getattr(r, 'status', '') or '') == "Deferido":
                if (not inicio and not fim) or _in_range(data_r, inicio, fim):
                    total_cadastradas_min += _min_total(r.horas, r.minutos)

        regs.sort(key=lambda x: x["data_realizacao"] or dt.date.min, reverse=True)

        ag_rows = []
        total_usufruidas_min = 0

        for a in ags_by_user.get(u.id, []):
            st_raw = getattr(a, 'status', '') or ''
            st = _normalize_status(st_raw)
            data_a = a.data

            if (not inicio and not fim) or _in_range(data_a, inicio, fim):
                ag_rows.append({
                    "data": data_a,
                    "horas": int(a.horas or 0),
                    "minutos": int(a.minutos or 0),
                    "data_referencia": getattr(a, 'data_referencia', None),
                    "status": st_raw,
                })

            if st == "Deferido":
                if (not inicio and not fim) or _in_range(data_a, inicio, fim):
                    total_usufruidas_min += _min_total(a.horas, a.minutos)

        ag_rows.sort(key=lambda x: x["data"] or dt.date.min, reverse=True)

        saldo_min = max(0, total_cadastradas_min - total_usufruidas_min)

        usuarios_relatorio.append({
            "id": u.id,
            "nome": u.nome,
            "registro": u.registro,
            "email": u.email,
            "horas": saldo_min // 60,
            "minutos": saldo_min % 60,
            "total_cadastradas_min": total_cadastradas_min,
            "total_usufruidas_min": total_usufruidas_min,
            "registros": regs,
            "agendamentos_bh": ag_rows,
        })

    return render_template('relatorio_horas_extras.html', usuarios=usuarios_relatorio)

# ===========================================
# ADMIN AGENDAMENTOS (página + AJAX + excluir)
# ===========================================
def _get_ag_datetime(ag):
    for attr in ("data", "data_agendada", "data_inicio", "created_at"):
        val = getattr(ag, attr, None)
        if isinstance(val, datetime.datetime):
            return val
        if isinstance(val, datetime.date):
            return datetime.datetime(val.year, val.month, val.day)
    return None

def _ord_key(val_dt):
    if isinstance(val_dt, datetime.datetime):
        try:
            return int(val_dt.timestamp())
        except Exception:
            return int(val_dt.strftime("%Y%m%d%H%M%S"))
    return 0

def _fmt_br(val_dt):
    if isinstance(val_dt, (datetime.datetime, datetime.date)):
        return val_dt.strftime("%d/%m/%Y")
    return ""

@app.route('/admin/agendamentos', methods=['GET'])
@login_required
def admin_agendamentos():
    if getattr(current_user, 'tipo', None) != 'administrador':
        flash("Acesso negado.", "danger")
        return redirect(url_for('index'))
    return render_template("admin_agendamentos.html")

@app.route('/admin/agendamentos/ajax', methods=['GET'])
@login_required
def admin_agendamentos_ajax():
    if getattr(current_user, 'tipo', None) != 'administrador':
        return jsonify({"error": "Acesso negado"}), 403

    try:
        nome     = (request.args.get("nome") or "").strip()
        status   = (request.args.get("status") or "").strip().lower()
        cargo    = (request.args.get("cargo") or "").strip()
        page     = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        order    = (request.args.get("order") or "desc").lower()

        query = (
            User.query
            .join(Agendamento)
            .options(joinedload(User.agendamentos))
        )

        if hasattr(User, "ativo"):
            query = query.filter(User.ativo.is_(True))

        if nome:
            query = query.filter(User.nome.ilike(f"%{nome}%"))

        if cargo:
            query = query.filter(User.cargo == cargo)

        query = query.order_by(User.nome.asc()).distinct()

        funcionarios = query.paginate(page=page, per_page=per_page, error_out=False)

        dados = []
        espera_aliases = {"em_espera", "em espera", "pendente"}

        for func in funcionarios.items:
            ags_tmp = []

            for ag in (func.agendamentos or []):
                ag_status_raw = (getattr(ag, "status", "") or "").strip()
                ag_status = ag_status_raw.lower()

                if status:
                    if status == "deferido" and not ag_status.startswith("deferido"):
                        continue
                    if status == "indeferido" and not ag_status.startswith("indeferido"):
                        continue
                    if status == "em_espera" and (ag_status not in espera_aliases):
                        continue

                ag_dt = _get_ag_datetime(ag)
                ags_tmp.append({
                    "id": ag.id,
                    "data": _fmt_br(ag_dt),
                    "motivo": getattr(ag, "motivo", None),
                    "status": ag_status_raw.title() if ag_status_raw else "",
                    "delete_url": url_for('admin_delete_agendamento', id=ag.id),
                    "_ord": _ord_key(ag_dt)
                })

            reverse = (order != "asc")
            ags_tmp.sort(key=lambda x: x["_ord"], reverse=reverse)
            for item in ags_tmp:
                item.pop("_ord", None)

            if ags_tmp:
                dados.append({
                    "id": func.id,
                    "funcionario": (func.nome or "").title(),
                    "cargo": func.cargo,
                    "agendamentos": ags_tmp
                })

        return jsonify({
            "page": funcionarios.page,
            "pages": funcionarios.pages,
            "per_page": funcionarios.per_page,
            "total": funcionarios.total,
            "has_next": funcionarios.has_next,
            "has_prev": funcionarios.has_prev,
            "next_num": getattr(funcionarios, "next_num", (funcionarios.page + 1 if funcionarios.has_next else None)),
            "prev_num": getattr(funcionarios, "prev_num", (funcionarios.page - 1 if funcionarios.has_prev else None)),
            "filters": {"nome": nome, "status": status, "cargo": cargo, "order": order},
            "dados": dados
        })

    except Exception:
        app.logger.exception("Erro em /admin/agendamentos/ajax")
        return jsonify({"error": "Erro interno ao carregar agendamentos."}), 500

# Exempt + validação manual do header CSRF
@csrf.exempt
@app.route('/admin/delete_agendamento/<int:id>', methods=['POST'])
@login_required
def admin_delete_agendamento(id):
    if getattr(current_user, 'tipo', None) != 'administrador':
        return jsonify({"error": "Acesso negado"}), 403

    if not _csrf_ok_from_header(request):
        return jsonify({"error": "CSRF inválido ou ausente."}), 400

    try:
        agendamento = Agendamento.query.get_or_404(id)
        db.session.delete(agendamento)
        db.session.commit()
        return jsonify({"success": True, "message": "Agendamento excluído com sucesso."})
    except Exception:
        db.session.rollback()
        app.logger.exception("Erro ao excluir agendamento")
        return jsonify({"error": "Não foi possível excluir o agendamento."}), 500

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
    PER_PAGE_DEFAULT = 10
    per_page = request.args.get('per_page', PER_PAGE_DEFAULT, type=int)
    if not per_page:
        per_page = PER_PAGE_DEFAULT
    per_page = max(5, min(per_page, 50))

    q = request.args.get('q', '', type=str).strip()
    status_filtro = request.args.get('status', 'ativos')

    user_q = User.query

    if hasattr(User, 'ativo'):
        if status_filtro == 'ativos':
            user_q = user_q.filter(User.ativo.is_(True))
        elif status_filtro == 'inativos':
            user_q = user_q.filter(User.ativo.is_(False))

    if q:
        user_q = user_q.filter(User.nome.ilike(f'%{q}%'))

    pagination = user_q.order_by(User.nome.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    users = pagination.items
    user_ids = [u.id for u in users] or [-1]

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

    try:
        Ag = Agendamento
        ag_uid  = getattr(Ag, 'funcionario_id')
        ag_stat = getattr(Ag, 'status')
        ag_data = getattr(Ag, 'data')
        ag_mot  = getattr(Ag, 'motivo')
        ag_tipoF = getattr(Ag, 'tipo_folga')

        status_cond = func.lower(ag_stat) == 'deferido'

        ab_filter = or_(func.upper(ag_tipoF) == 'AB', func.upper(ag_mot) == 'AB')

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

    try:
        Ag = Agendamento
        ag_uid  = getattr(Ag, 'funcionario_id')
        ag_stat = getattr(Ag, 'status')
        ag_data = getattr(Ag, 'data')
        ag_mot  = getattr(Ag, 'motivo')
        ag_tipoF = getattr(Ag, 'tipo_folga')

        status_cond = func.lower(ag_stat) == 'deferido'
        tre_filter = or_(func.upper(ag_tipoF) == 'TRE', func.upper(ag_mot) == 'TRE')

        query = Ag.query.filter(ag_uid.in_(user_ids)).filter(status_cond).filter(tre_filter)
        if ag_data is not None:
            query = query.order_by(ag_data.asc())
        tre_rows = query.all()

        for ag in tre_rows:
            uid_val = getattr(ag, 'funcionario_id', None)
            if uid_val in resumos:
                resumos[uid_val].setdefault('tre_agendamentos', []).append(ag)
    except Exception as e:
        current_app.logger.exception("Erro ao listar TRE: %s", e)

    try:
        Ag = Agendamento
        ag_uid  = getattr(Ag, 'funcionario_id')
        ag_stat = getattr(Ag, 'status')
        ag_data = getattr(Ag, 'data')
        ag_mot  = getattr(Ag, 'motivo')
        ag_tipoF = getattr(Ag, 'tipo_folga')

        status_cond = func.lower(ag_stat) == 'deferido'
        bh_filter = or_(func.upper(ag_tipoF) == 'BH', func.upper(ag_mot) == 'BH')

        query = Ag.query.filter(ag_uid.in_(user_ids)).filter(status_cond).filter(bh_filter)
        if ag_data is not None:
            query = query.order_by(ag_data.asc())
        bh_rows = query.all()

        for ag in bh_rows:
            uid_val = getattr(ag, 'funcionario_id', None)
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

    current_app.logger.info("Alterando status do usuário %s (antes: %s)", user.id, user.ativo)

    payload = request.get_json(silent=True) or {}
    novo_ativo = payload.get('ativo', None)

    if novo_ativo is not None:
        try:
            if isinstance(novo_ativo, (int, str)):
                user.ativo = bool(int(novo_ativo))
            else:
                user.ativo = bool(novo_ativo)
        except Exception:
            user.ativo = not bool(user.ativo)
    else:
        user.ativo = not bool(user.ativo)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Erro ao salvar status do usuário %s: %s", user.id, e)
        return jsonify(success=False, error='Erro ao salvar no banco.'), 500

    current_app.logger.info("Status do usuário %s alterado para %s", user.id, user.ativo)
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
def allowed_file(filename: str) -> bool:
    return bool(filename) and "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def _ensure_upload_dir() -> Path:
    base_dir = Path(current_app.config.get("UPLOAD_FOLDER", "uploads/tre")).resolve()
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def _candidate_dirs_for_download() -> list[Path]:
    dirs = []
    cfg = Path(current_app.config.get("UPLOAD_FOLDER", "uploads/tre")).resolve()
    dirs.append(cfg)
    legacy_app = Path(current_app.root_path, "uploads", "tre").resolve()
    dirs.append(legacy_app)
    legacy_rel = Path("uploads/tre").resolve()
    dirs.append(legacy_rel)
    dirs.append(Path("/var/data/tre"))

    seen = set()
    uniq = []
    for p in dirs:
        rp = str(Path(p).resolve())
        if rp not in seen:
            uniq.append(Path(rp))
            seen.add(rp)
    return uniq

def _resolve_pdf_path(filename: str) -> Path | None:
    safe_name = os.path.basename(filename)
    for base in _candidate_dirs_for_download():
        candidate = (base / safe_name)
        if candidate.is_file():
            return candidate.resolve()
    return None

def sync_tre_user(usuario_id: int):
    usuario = User.query.get(usuario_id)
    if not usuario:
        return 0, 0, 0

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

        if not dias_folga or dias_folga < 1 or not arquivo or not arquivo.filename:
            flash("Preencha corretamente os campos e anexe o PDF.", "danger")
            return redirect(url_for("adicionar_tre"))

        if not allowed_file(arquivo.filename):
            flash("Somente PDF é permitido.", "danger")
            return redirect(url_for("adicionar_tre"))

        filename = secure_filename(
            f"{current_user.id}_{datetime.datetime.now():%Y%m%d%H%M%S}_{arquivo.filename}"
        )

        save_dir = _ensure_upload_dir()
        arquivo.save(str(save_dir / filename))

        nova = TRE(
            funcionario_id=current_user.id,
            dias_folga=dias_folga,
            arquivo_pdf=filename,
            status="pendente",
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
def download_tre(tre_id: int):
    tre = TRE.query.get_or_404(tre_id)

    if tre.funcionario_id != current_user.id and getattr(current_user, "tipo", "") != "administrador":
        flash("Você não tem permissão para acessar este arquivo.", "danger")
        return redirect(url_for("minhas_tres"))

    current_app.logger.warning("UPLOAD_FOLDER=%s", current_app.config.get("UPLOAD_FOLDER"))
    current_app.logger.warning("CANDIDATES=%s", [str(p) for p in _candidate_dirs_for_download()])

    pdf_path = _resolve_pdf_path(tre.arquivo_pdf)

    current_app.logger.info(
        "Download TRE id=%s filename=%s resolved_path=%s found=%s",
        tre_id, tre.arquivo_pdf, pdf_path, bool(pdf_path)
    )

    if not pdf_path:
        flash(
            "Arquivo de TRE não está disponível no servidor no momento. "
            "Isso pode ocorrer após atualização do sistema.",
            "warning"
        )
        return redirect(url_for("minhas_tres"))

    return send_file(
        path_or_file=str(pdf_path),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=os.path.basename(tre.arquivo_pdf),
        max_age=0
    )

# ===========================================
# TRE - ADMIN
# ===========================================
@app.route("/admin/tres", methods=["GET"])
@login_required
def admin_tres_list():
    if getattr(current_user, "tipo", "") != "administrador":
        flash("Acesso negado.", "danger")
        return redirect(url_for("index"))

    status = request.args.get("status", "pendente")
    busca = request.args.get("q", "").strip()

    q = (
        TRE.query
        .join(User, User.id == TRE.funcionario_id)
        .filter(User.ativo.is_(True))
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
def admin_tre_decidir(tre_id: int):
    if getattr(current_user, "tipo", "") != "administrador":
        return jsonify({"error": "Acesso negado"}), 403

    tre = TRE.query.get_or_404(tre_id)
    user = User.query.get_or_404(tre.funcionario_id)

    acao = request.form.get("acao")
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
def admin_tre_excluir(tre_id: int):
    if getattr(current_user, "tipo", "") != "administrador":
        return jsonify({"error": "Acesso negado"}), 403

    tre = TRE.query.get_or_404(tre_id)
    user = User.query.get_or_404(tre.funcionario_id)

    try:
        db.session.delete(tre)
        db.session.commit()
        sync_tre_user(user.id)
        return jsonify({"success": True})
    except Exception as e:
        current_app.logger.exception("Erro ao excluir TRE id=%s: %s", tre_id, e)
        db.session.rollback()
        return jsonify({"error": "Falha ao excluir a TRE."}), 500

# ===========================================
# RELATÓRIO PDF (ADMIN)
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
        .filter(or_(func.upper(Ag.motivo) == "TRE", func.upper(Ag.tipo_folga) == "TRE"))
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
        .filter(or_(func.upper(Ag.motivo) == "BH", func.upper(Ag.tipo_folga) == "BH"))
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

    header_center_y = height - 22 * mm
    azul_linha = colors.HexColor("#1a73e8")
    texto_cor = colors.HexColor("#111827")

    logo_h = 16 * mm
    escola_logo = find_logo("escola.png")
    municipio_logo = find_logo("municipio.png")
    logo_y = header_center_y - logo_h / 2

    if escola_logo:
        c.drawImage(escola_logo, margin_x, logo_y, width=logo_h, height=logo_h, preserveAspectRatio=True, mask="auto")
    if municipio_logo:
        c.drawImage(municipio_logo, margin_right - logo_h, logo_y, width=logo_h, height=logo_h, preserveAspectRatio=True, mask="auto")

    titulo_y = header_center_y + 6 * mm
    subtitulo_y = header_center_y
    data_y = header_center_y + 12 * mm

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(texto_cor)
    c.drawCentredString(width / 2, titulo_y, "FICHA CADASTRAL DO SERVIDOR")

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#4b5563"))
    c.drawCentredString(width / 2, subtitulo_y, "Portal do Servidor — Gestão de Ponto")

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#6b7280"))
    c.drawRightString(margin_right, data_y, datetime.datetime.now().strftime("Emitido em %d/%m/%Y %H:%M"))

    line_y = header_center_y - 10 * mm
    c.setStrokeColor(azul_linha)
    c.setLineWidth(0.8)
    c.line(margin_x, line_y, margin_right, line_y)

    footer_base_y = 15 * mm
    footer_line_y = footer_base_y + 4 * mm

    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.6)
    c.line(margin_x, footer_line_y, margin_right, footer_line_y)

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    footer_text = "E.M. José Padin Mouta • R. Bororós, 150 - Vila Tupi, Praia Grande - SP, 11703-390"
    c.drawCentredString(width / 2, footer_base_y + 1 * mm, footer_text)

    c.drawRightString(margin_right, footer_base_y - 2 * mm, f"Página {c.getPageNumber()}")

    content_start_y = line_y - 12 * mm
    return content_start_y

def draw_simple_table(c, x, y, col_widths, headers, rows):
    row_height = 6 * mm
    total_width = sum(col_widths)
    total_rows = 1 + len(rows)
    table_height = total_rows * row_height

    c.setStrokeColor(colors.HexColor("#d1d5db"))
    c.setLineWidth(0.6)
    c.rect(x, y - table_height, total_width, table_height, stroke=1, fill=0)

    header_bg_color = colors.HexColor("#eff6ff")
    c.setFillColor(header_bg_color)
    c.rect(x, y - row_height, total_width, row_height, stroke=0, fill=1)

    c.setStrokeColor(colors.HexColor("#e5e7eb"))
    for i in range(total_rows + 1):
        c.line(x, y - i * row_height, x + total_width, y - i * row_height)

    running_x = x
    for w in col_widths[:-1]:
        running_x += w
        c.line(running_x, y, running_x, y - table_height)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.HexColor("#111827"))
    header_y = y - 0.75 * row_height
    col_x = x + 2 * mm
    for idx, h in enumerate(headers):
        c.drawString(col_x, header_y, h)
        col_x += col_widths[idx]

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.black)
    for idx, row in enumerate(rows):
        row_y = y - (idx + 1.75) * row_height
        col_x = x + 2 * mm
        for col_idx, value in enumerate(row):
            c.drawString(col_x, row_y, str(value))
            col_x += col_widths[col_idx]

    return y - table_height

def _truncate_text(c, text, max_width, font_name="Helvetica-Bold", font_size=9):
    c.setFont(font_name, font_size)
    if not text:
        return ""
    text = str(text)
    w = c.stringWidth(text, font_name, font_size)
    if w <= max_width:
        return text
    ellipsis_w = c.stringWidth("...", font_name, font_size)
    max_content_width = max_width - ellipsis_w
    for i in range(len(text), 0, -1):
        chunk = text[:i]
        if c.stringWidth(chunk, font_name, font_size) <= max_content_width:
            return chunk + "..."
    return text

def draw_user_page(c: canvas.Canvas, user: User, width, height):
    margin_left = 20 * mm
    margin_right = width - 20 * mm
    content_width = margin_right - margin_left

    azul = colors.HexColor("#1a73e8")
    roxo = colors.HexColor("#2563eb")

    y = draw_header_footer(c, width, height)

    y -= 6 * mm

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawString(margin_left, y, "Dados do servidor")

    y -= 5 * mm

    campos_esquerda = [
        ("Servidor", user.nome or "—"),
        ("CPF", user.cpf or "—"),
        ("Data de nascimento", user.data_nascimento.strftime("%d/%m/%Y") if user.data_nascimento else "—"),
        ("Data emissão RG", user.data_emissao_rg.strftime("%d/%m/%Y") if user.data_emissao_rg else "—"),
        ("Celular", user.celular or "—"),
        ("Graduação", user.graduacao or "—"),
    ]

    campos_direita = [
        ("Registro funcional", user.registro or "—"),
        ("Cargo", user.cargo or "—"),
        ("RG", user.rg or "—"),
        ("Órgão emissor", user.orgao_emissor or "—"),
        ("E-mail", user.email or "—"),
    ]

    n_linhas = max(len(campos_esquerda), len(campos_direita))
    row_height = 5 * mm
    padding_top = 6 * mm
    padding_bottom = 6 * mm

    card_height = padding_top + n_linhas * row_height + padding_bottom
    card_top_y = y
    card_bottom_y = card_top_y - card_height

    c.setFillColor(colors.white)
    c.setStrokeColor(colors.HexColor("#d0d7e2"))
    c.setLineWidth(0.9)
    c.roundRect(margin_left, card_bottom_y, content_width, card_height, 4 * mm, stroke=1, fill=1)

    col_width = content_width / 2.0
    c.setStrokeColor(colors.HexColor("#e5e7eb"))
    c.setLineWidth(0.6)
    c.line(margin_left + col_width, card_top_y - 2 * mm, margin_left + col_width, card_bottom_y + 2 * mm)

    inner_top_y = card_top_y - padding_top
    for i in range(n_linhas + 1):
        y_line = inner_top_y - i * row_height
        c.setStrokeColor(colors.HexColor("#edf2f7"))
        c.line(margin_left + 2 * mm, y_line, margin_right - 2 * mm, y_line)

    label_left_x = margin_left + 3 * mm
    value_left_x = margin_left + 32 * mm
    label_right_x = margin_left + col_width + 3 * mm
    value_right_x = margin_left + col_width + 32 * mm

    current_y = inner_top_y - (row_height * 0.7)

    font_label = "Helvetica-Bold"
    font_valor = "Helvetica"
    size_label = 8.5
    size_valor = 8.5

    for idx in range(n_linhas):
        if idx < len(campos_esquerda):
            label, valor = campos_esquerda[idx]
            c.setFont(font_label, size_label)
            c.setFillColor(colors.HexColor("#4b5563"))
            c.drawString(label_left_x, current_y, f"{label}:")
            max_w = col_width - (value_left_x - margin_left) - 4 * mm
            text_valor = _truncate_text(c, valor, max_w, font_name=font_valor, font_size=size_valor)
            c.setFont(font_valor, size_valor)
            c.setFillColor(colors.HexColor("#111827"))
            c.drawString(value_left_x, current_y, text_valor)

        if idx < len(campos_direita):
            label, valor = campos_direita[idx]
            c.setFont(font_label, size_label)
            c.setFillColor(colors.HexColor("#4b5563"))
            c.drawString(label_right_x, current_y, f"{label}:")
            max_w = col_width - (value_right_x - (margin_left + col_width)) - 4 * mm
            text_valor = _truncate_text(c, valor, max_w, font_name=font_valor, font_size=size_valor)
            c.setFont(font_valor, size_valor)
            c.setFillColor(colors.HexColor("#111827"))
            c.drawString(value_right_x, current_y, text_valor)

        current_y -= row_height

    y = card_bottom_y - 10 * mm

    total_tre = user.tre_total or 0
    usadas_tre = user.tre_usufruidas or 0
    saldo_tre = max(total_tre - usadas_tre, 0)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(azul)
    c.drawString(margin_left, y, "FOLGAS TRE (TRIBUNAL REGIONAL ELEITORAL)")
    y -= 4.5 * mm

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#111827"))
    resumo_tre = f"Total: {total_tre} dia(s)  •  A usufruir: {saldo_tre} dia(s)  •  Usadas: {usadas_tre} dia(s)"
    c.drawString(margin_left, y, resumo_tre)
    y -= 7 * mm

    tre_rows = get_tre_agendamentos(user.id)
    if tre_rows:
        y = draw_simple_table(c, margin_left, y, [35 * mm, content_width - 35 * mm], ["Data", "Situação"], tre_rows)
        y -= 10 * mm
    else:
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.HexColor("#6b7280"))
        c.drawString(margin_left, y, "Nenhum agendamento TRE deferido cadastrado.")
        y -= 10 * mm

    c.setStrokeColor(colors.HexColor("#e5e7eb"))
    c.setLineWidth(0.6)
    c.line(margin_left, y, margin_right, y)
    y -= 7 * mm

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(roxo)
    c.drawString(margin_left, y, "BANCO DE HORAS")
    y -= 5 * mm

    saldo_min = user.banco_horas or 0
    saldo_bh_str = format_banco_horas(saldo_min)

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawString(margin_left, y, f"Saldo atual: {saldo_bh_str}")
    y -= 8 * mm

    bh_rows = get_bh_agendamentos(user.id)
    if bh_rows:
        y = draw_simple_table(c, margin_left, y, [35 * mm, content_width - 35 * mm], ["Data", "Situação"], bh_rows)
    else:
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.HexColor("#6b7280"))
        c.drawString(margin_left, y, "Nenhum agendamento BH deferido cadastrado.")

@app.route('/user_info_report')
@login_required
def user_info_report():
    if getattr(current_user, 'tipo', None) != 'administrador':
        flash("Acesso negado. Esta página é exclusiva para administradores.", "danger")
        return redirect(url_for('index'))

    users = (
        User.query
        .filter_by(ativo=True)
        .order_by(User.nome.asc())
        .all()
    )

    if not users:
        flash("Nenhum usuário ativo encontrado para gerar o relatório.", "warning")
        return redirect(url_for('user_info_all'))

    for u in users:
        try:
            sync_tre_user(u.id)
        except Exception:
            current_app.logger.exception("Erro ao sincronizar TRE do usuário %s no relatório.", u.id)

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

# --- HUB TRE ---
@app.route("/tre", methods=["GET"], strict_slashes=False)
@login_required
def tre_menu():
    return render_template("tre_menu.html")

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
