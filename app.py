import bcrypt
import json
from flask import *
from forms import *
from roles import *
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import database as db
import os
import pyperclip

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, nome, password, level, company):
        self.id = id
        self.email = email
        self.password = password  
        self.nome = nome 
        self.level = level
        self.company = company 

@login_manager.user_loader
def load_user(user_id):
    user_data = db.search_id_login(int(user_id))
    if user_data:
        return User(user_data['id'], user_data['email'], user_data['nome'], user_data['senha'], user_data['nivel'], user_data['empresa'])
    return None

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    open_report = db.show_open_report(current_user.id)
    open_reports = db.show_all_open_reports()
    closed_reports = db.show_closed_reports(10 - len(open_reports))
    reports = open_reports + closed_reports
    form = CreateReport()
    session['ufv_aberto'] = 'Brasilia 100'

    for report in reports:
        report['responsavel'] = db.search_name_user(report['responsavel'])

    if form.validate_on_submit():
        db.create_report(current_user.id, current_user.nome)
        flash('Login bem sucedido!', 'success')
        return redirect(url_for('home'))
    
    return render_template('index.html', form = form, reports = reports, open_report = open_report)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = Login()
    if form_login.validate_on_submit():
        user = form_login.username.data
        senha = form_login.password.data
        login_unlock = db.search_login(user)
        print(login_unlock)
        if login_unlock:
            senha.encode("utf-8")
            if bcrypt.checkpw(senha.encode("utf-8"), login_unlock['senha'].encode("utf-8")):  
                user_obj = User(login_unlock['id'], login_unlock['email'], login_unlock['nome'], login_unlock['senha'], login_unlock['nivel'], login_unlock['empresa'])
                login_user(user_obj)
                if login_unlock['nivel'] == 'gestor':
                    return redirect(url_for('gestor', empresa = login_unlock['empresa']))
                else:
                    return redirect(url_for('home'))
        print("Usuário ou senha inválidos!", "danger")
    return render_template('login.html', form=form_login)

@app.route('/relatorio/<int:id_relatorio>/<empresa>/<ufv>', methods=['GET', 'POST'])
@login_required
def relatorio(id_relatorio, empresa, ufv):
    status = db.status_report(id_relatorio)['status']
    reports = db.show_record(str(id_relatorio), ufv)
    id_responsible = int(db.id_responsible(id_relatorio)['responsavel'])
    cams = db.show_cams(ufv)
    cams_closed_report = db.show_cams_closed_report(id_relatorio)[0]['dados'] if not status else []
    occurrences_report = db.show_occurrences_report(id_relatorio)
    all_ufvs = db.show_all_ufvs()
    status_ufv = db.show_status_ufv(ufv)['online']

    form_elipse = CreateRecord()
    form_close_report = CloseReport()
    form_edit_record = EditRecord()
    form_delete_record = DeleteRecord()
    form_edit_cam_record = EditCamRecord()
    form_add_occurrence = AddOccurrence()
    form_edit_occurrence = EditOccurrence()
    form_delete_occurrence = DeleteOccurrence()
    form_copy_report_local = CopyReportLocal()
    form_no_connect_ufv = NoConnectUFV()

    empresas = {}

    for usina in all_ufvs:
        nome_empresa = usina['empresa']
        nome_usina = usina['nome']

        if nome_empresa not in empresas:
            empresas[nome_empresa] = []

        if nome_usina not in empresas[nome_empresa]:
            empresas[nome_empresa].append(nome_usina)

    if form_elipse.validate_on_submit() and form_elipse.submit_create_report.data:
        horario = form_elipse.time.data
        status = form_elipse.status.data
        obs = form_elipse.observation.data
        db.create_record_elipse(id_relatorio, horario, ufv, status, obs)
        return redirect(url_for('relatorio', id_relatorio = id_relatorio, empresa = empresa, ufv=ufv))
    
    elif form_edit_record.validate_on_submit() and form_edit_record.submit_edit_record.data:
        horario = form_edit_record.timeEditElipse.data
        status = form_edit_record.statusEditElipse.data
        obs = form_edit_record.observationEditElipse.data
        id_record = form_edit_record.id_recordEditElipse.data
        db.edit_record_elipse(id_record, horario, ufv, status, obs)
        return redirect(url_for('relatorio', id_relatorio = id_relatorio, empresa = empresa, ufv=ufv))
    
    elif form_close_report.validate_on_submit() and form_close_report.submit_close_report.data:
        db.close_report(str(id_relatorio))
        db.close_cams_report(empresas, id_relatorio)
        return redirect(url_for('home'))
    
    elif form_no_connect_ufv.submit_no_connect_ufv and form_no_connect_ufv.submit_no_connect_ufv.data:
        db.switch_status_ufv(ufv, not status_ufv)
        return redirect(url_for('relatorio', id_relatorio = id_relatorio, empresa = empresa, ufv=ufv))
        
    elif form_delete_record.validate_on_submit() and form_delete_record.submit_delete_record.data:
        db.delete_record_elipse(form_delete_record.id_recordDeleteElipse.data)
        return redirect(url_for('relatorio', id_relatorio = id_relatorio, empresa = empresa, ufv=ufv))
    
    elif form_edit_cam_record.validate_on_submit() and form_edit_cam_record.submit_edit_cam_record.data:
        id_edit_cam = form_edit_cam_record.id_cam_edit_record.data
        status = form_edit_cam_record.status_edit_cam_record.data
        obs = form_edit_cam_record.obs_edit_cam_record.data
        db.edit_cam_report(id_edit_cam, status, obs)
        return redirect(url_for('relatorio', id_relatorio = id_relatorio, empresa = empresa, ufv=ufv))
    
    elif form_add_occurrence.validate_on_submit() and form_add_occurrence.submit_add_occurrence.data:
        data = str(form_add_occurrence.date_add_occurrence.data)
        horario = str(form_add_occurrence.hour_add_occurrence.data)[:5]
        status = form_add_occurrence.status_add_occurrence.data
        acoes = form_add_occurrence.actions_add_occurrence.data
        observacoes = form_add_occurrence.observations_add_occurrence.data
        db.add_occurrence(horario, status, acoes, observacoes, id_relatorio, empresa, ufv, data, current_user.nome)
        return redirect(url_for('relatorio', id_relatorio = id_relatorio, empresa = empresa, ufv=ufv))
    
    elif form_edit_occurrence.validate_on_submit() and form_edit_occurrence.submit_edit_occurrence.data:
        id_edit_occurrence = form_edit_occurrence.id_edit_occurrence.data
        data = str(form_edit_occurrence.date_edit_occurrence.data)
        horario = str(form_edit_occurrence.hour_edit_occurrence.data)[:5]
        status = form_edit_occurrence.status_edit_occurrence.data
        acoes = form_edit_occurrence.actions_edit_occurrence.data
        observacoes = form_edit_occurrence.observations_edit_occurrence.data
        db.edit_occurrence(id_edit_occurrence, data, horario, status, acoes, observacoes)
        return redirect(url_for('relatorio', id_relatorio = id_relatorio, empresa = empresa, ufv=ufv))
    
    elif form_delete_occurrence.submit_delete_occurrence.data and form_delete_occurrence.validate_on_submit():
        id_delete_occurence = form_delete_occurrence.id_delete_occurrence.data
        db.delete_occurrence(id_delete_occurence)
        return redirect(url_for('relatorio', id_relatorio = id_relatorio, empresa = empresa, ufv=ufv))
    
    elif form_copy_report_local.submit_copy_report_local.data and form_copy_report_local.validate_on_submit():
        mensagemTitulo = '*RELATÓRIO DE CÂMERAS*\n\n'
        mensagemStatus = ''
        mensagemCameras = ''
        mensagem = ''
        onlines = 0
        cameras = db.data_for_copy_report(ufv)
        
        for camera in cameras: 
            if camera['status'] == 'online': onlines += 1
            mensagemCameras += f'\n- *{camera["nome"]}:* {camera["status"].capitalize()}'

        if len(cameras) == onlines: mensagemStatus = f'🟢 *{ufv}*'
        elif onlines > 0 and len(cameras) > onlines: mensagemStatus = f'🟡 *{ufv} - {onlines}/{len(cameras)}*'
        elif onlines == 0: mensagemStatus = f'🔴 *{ufv} - Offline*'

        mensagem += mensagemTitulo
        mensagem += mensagemStatus
        mensagem += mensagemCameras



        pyperclip.copy(mensagem)
        return redirect(url_for('relatorio', id_relatorio = id_relatorio, empresa = empresa, ufv=ufv))


    print(status)
    return render_template('relatorio_aberto.html', 
                           reports = reports, 
                           form_elipse = form_elipse, 
                           empresas = empresas, 
                           ufv_aberto = ufv,
                           empresa = empresa,
                           id_relatorio = id_relatorio, 
                           form_close_report = form_close_report, 
                           form_edit_record = form_edit_record, 
                           form_delete_record = form_delete_record,
                           form_edit_cam_record = form_edit_cam_record,
                           form_no_connect_ufv = form_no_connect_ufv,
                           status = status,
                           cams = cams,
                           cams_closed_report = cams_closed_report,
                           id_responsible = id_responsible,
                           form_add_occurrence = form_add_occurrence,
                           form_edit_occurrence = form_edit_occurrence,
                           form_delete_occurrence = form_delete_occurrence,
                           form_copy_report_local = form_copy_report_local,
                           occurrences_report = occurrences_report,
                           status_ufv = status_ufv) 

@app.route('/relatorios/<int:page>', methods=['GET', 'POST'])
@login_required
def relatorios(page):
    qtd_pages = db.qtd_pages()
    reports_in_page = db.show_report_page(page)

    for report in reports_in_page:
        report['responsavel'] = db.search_name_user(report['responsavel'])

    return render_template('relatorios.html', reports_in_page = reports_in_page, page = page, qtd_pages = qtd_pages)

@app.route('/usina/<ufv>', methods=['GET', 'POST'])
@login_required
def usina(ufv):
    cams = db.show_cams(ufv)
    local = db.show_local_ufv(ufv)
    contacts = db.show_contacts_ufv(ufv)
    form_add_cam = AddCam()
    form_edit_cam = EditCam()
    form_edit_local = EditLocal()
    form_delete_cam = DeleteCam()
    form_add_contact = AddContact()
    form_edit_contact = EditContact()
    form_delete_contact = DeleteContact()

    session['pagina_atual'] = 'usina'


    if form_add_cam.validate_on_submit() and form_add_cam.submit.data: 
        nome = form_add_cam.name.data
        tipo = form_add_cam.tipo.data
        obs = form_add_cam.obs.data
        status = form_add_cam.status.data
        db.add_cam(ufv, nome, tipo, obs, status, current_user.nome)
        return redirect(url_for('usina', ufv = ufv))

    if form_edit_cam.validate_on_submit() and form_edit_cam.submit_edit_cam.data:
        id_cam = form_edit_cam.id_cam_edit.data
        nome = form_edit_cam.name_edit_cam.data
        tipo = form_edit_cam.tipo_edit_cam.data
        obs = form_edit_cam.obs_edit_cam.data
        status = form_edit_cam.status_edit_cam.data
        db.edit_cam(id_cam, nome, tipo, status, obs)
        return redirect(url_for('usina', ufv = ufv))
    
    if form_delete_cam.validate_on_submit() and form_delete_cam.submit_delete_cam.data:
        id_cam = form_delete_cam.id_cam_delete.data
        db.delete_cam(id_cam)
        return redirect(url_for('usina', ufv = ufv))

    if form_edit_local.validate_on_submit() and form_edit_local.submit_edit_local.data:
        endereco = form_edit_local.endereco_edit_local.data
        maps = form_edit_local.maps_edit_local.data
        db.edit_local_ufv(ufv, endereco, maps)
        return redirect(url_for('usina', ufv = ufv))
    
    if form_add_contact.validate_on_submit() and form_add_contact.submit_add_contact.data:
        nome = form_add_contact.name_add_contact.data
        empresa = form_add_contact.company_add_contact.data
        telefone = form_add_contact.phone_add_contact.data
        db.add_contact_ufv(ufv, nome, empresa, telefone)
        return redirect(url_for('usina', ufv = ufv))
    
    if form_edit_contact.validate_on_submit() and form_edit_contact.submit_edit_contact.data:
        id_edit_contact = form_edit_contact.id_edit_contact.data
        nome = form_edit_contact.name_edit_contact.data
        empresa = form_edit_contact.company_edit_contact.data
        telefone = form_edit_contact.phone_edit_contact.data
        db.edit_contact_ufv(id_edit_contact, ufv, nome, empresa, telefone)
        return redirect(url_for('usina', ufv = ufv))
    
    if form_delete_contact.validate_on_submit() and form_delete_contact.submit_delete_contact.data:
        id_contact = form_delete_contact.id_contact_delete.data
        db.delete_contact_ufv(id_contact)
        return redirect(url_for('usina', ufv = ufv))
    

    return render_template('usina.html', 
                           ufv = ufv, 
                           form_add_cam = form_add_cam, 
                           form_edit_cam = form_edit_cam, 
                           form_delete_cam = form_delete_cam, 
                           cams = cams,
                           form_edit_local = form_edit_local,
                           local = local,
                           form_add_contact = form_add_contact,
                           form_edit_contact = form_edit_contact,
                           form_delete_contact = form_delete_contact,
                           contacts = contacts)

@app.route('/empresas', methods=['GET', 'POST'])
@login_required
def empresas():
    return render_template('empresas.html')

@app.route('/empresa/<empresa>', methods=['GET', 'POST'])
@login_required
def empresa(empresa):
    form_add_ufv = AddUFV()
    ufvs = db.show_ufvs(empresa)

    session['pagina_atual'] = 'empresa'

    if form_add_ufv.validate_on_submit():
        nome = form_add_ufv.name_add_ufv.data
        db.add_ufv(nome, empresa, current_user.nome)
        return redirect(url_for('empresa', empresa = empresa))

    return render_template('empresa.html', empresa = empresa, form_add_ufv = form_add_ufv, ufvs = ufvs)

@app.route('/senhas', methods=['GET', 'POST'])
@login_required
def senhas():
    passwords = db.show_passwords()

    form_add_password = AddPassword()
    form_edit_password = EditPassword()
    form_delete_credential = DeleteCrendential()

    if form_add_password.validate_on_submit() and form_add_password.submit_add_password.data:
        software = form_add_password.software_add_password.data
        usuario = form_add_password.user_add_password.data
        senha = form_add_password.password_add_password.data
        descricao = form_add_password.description_add_password.data
        observacao = form_add_password.obs_add_password.data
        db.add_password(software, usuario, senha, descricao, observacao)
        return redirect(url_for('senhas'))
    
    elif form_edit_password.validate_on_submit() and form_edit_password.submit_edit_password.data:
        id_edit_credential = form_edit_password.id_edit_password.data
        software = form_edit_password.software_edit_password.data
        usuario = form_edit_password.user_edit_password.data
        senha = form_edit_password.password_edit_password.data
        descricao = form_edit_password.description_edit_password.data
        observacao = form_edit_password.obs_edit_password.data
        db.edit_credential(id_edit_credential, software, usuario, senha, descricao, observacao)
        return redirect(url_for('senhas'))
    
    elif form_delete_credential.validate_on_submit() and form_delete_credential.submit_delete_credential.data:
        id_delete_credential = form_delete_credential.id_credential_delete.data
        db.delete_credential(id_delete_credential)
        return redirect(url_for('senhas'))


    return render_template('senhas.html', 
                           form_add_password = form_add_password, 
                           form_edit_password = form_edit_password,
                           form_delete_credential = form_delete_credential,
                           passwords = passwords)

@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
@role_required('adm')
def usuarios():
    users = db.show_users()

    form_add_user = AddUser()
    form_edit_user = EditUser()
    form_delete_user = DeleteUser()
    form_new_password = NewPassword()

    if form_add_user.validate_on_submit() and form_add_user.submit_add_user.data:
        nome = form_add_user.name_add_user.data
        email = form_add_user.email_add_user.data
        nivel = form_add_user.level_add_user.data
        empresa = form_add_user.company_add_user.data
        senha = 'Aevo@123'
        senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        db.add_user(nome, email, senha.decode('utf-8'), nivel, empresa)
        return redirect(url_for('usuarios'))
    
    elif form_edit_user.validate_on_submit() and form_edit_user.submit_edit_user.data:
        id_edit_usuario = form_edit_user.id_edit_user.data
        nome = form_edit_user.name_edit_user.data
        email = form_edit_user.email_edit_user.data
        nivel = form_edit_user.level_edit_user.data
        empresa = form_edit_user.company_edit_user.data
        db.edit_user(id_edit_usuario, nome, email, nivel, empresa)
        return redirect(url_for('usuarios'))

    elif form_delete_user.validate_on_submit() and form_delete_user.submit_delete_user.data:
        id_delete_usuario = form_delete_user.id_delete_user.data
        db.delete_user(id_delete_usuario)
        return redirect(url_for('usuarios'))
    
    elif form_new_password.validate_on_submit() and form_new_password.submit_new_password.data:
        id_user = form_new_password.id_new_password.data
        new_password = form_new_password.new_password.data
        new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        db.edit_new_password(id_user, new_password.decode('utf-8'))
        return redirect(url_for('usuarios'))

    return render_template('usuarios.html', users = users,
                           form_add_user = form_add_user,
                           form_edit_user = form_edit_user,
                           form_delete_user = form_delete_user,
                           form_new_password = form_new_password
                           )

@app.route('/gestor', methods=['GET', 'POST'])
@login_required
@role_required('gestor')
def gestor():
    closed_reports = db.show_all_closed_reports()
    open_reports = db.show_all_open_reports()

    for report in closed_reports:
        report['responsavel'] = db.search_name_user(report['responsavel'])
    for report in open_reports:
        report['responsavel'] = db.search_name_user(report['responsavel'])

    return render_template('gestor.html', open_reports = open_reports, closed_reports = closed_reports)

@app.route('/ocorrencias', methods=['GET', 'POST'])
@login_required
def ocorrencias():
    form_add_occurrence = AddOccurrence()
    form_edit_occurrence = EditOccurrence()
    form_delete_occurrence = DeleteOccurrence()

    if form_add_occurrence.validate_on_submit() and form_add_occurrence.submit_add_occurrence.data():
        id_relatorio_add_occurence = form_add_occurrence.id_report.data
        horario_add_occurence = form_add_occurrence.hour_add_occurrence.data
        status_add_occurrence = form_add_occurrence.status_add_occurrence.data
        acoes_add_occurrence = form_add_occurrence.actions_add_occurrence.data
        observacoes_add_occurrence = form_add_occurrence.observations_add_occurrence.data
        db.add_occurrence(horario_add_occurence, status_add_occurrence, acoes_add_occurrence, observacoes_add_occurrence, id_relatorio_add_occurence)
        return redirect(url_for('ocorrencias'))
    
    elif form_edit_occurrence.validate_on_submit() and form_edit_occurrence.submit_edit_occurrence.data():
        id_relatorio_edit_occurence = form_edit_occurrence.id_report.data
        horario_edit_occurence = form_edit_occurrence.hour_edit_occurrence.data
        status_edit_occurrence = form_edit_occurrence.status_edit_occurrence.data
        acoes_edit_occurrence = form_edit_occurrence.actions_edit_occurrence.data
        observacoes_edit_occurrence = form_edit_occurrence.observations_edit_occurrence.data
        db.edit_occurrence(horario_edit_occurence, status_edit_occurrence, acoes_edit_occurrence, observacoes_edit_occurrence, id_relatorio_edit_occurence)
        return redirect(url_for('ocorrencias'))
    
    elif form_delete_occurrence.validate_on_submit() and form_delete_occurrence.submit_delete_occurrence.data():
        id_delete_occurence = form_delete_occurrence.id_delete_occurrence.data

        db.delete_occurrence(id_delete_occurence)
        return redirect(url_for('ocorrencias'))
    
    return render_template('ocorrencias.html')

@app.route('/logs')
@login_required
@role_required('adm')
def logs():

    log = db.show_logs()

    return render_template('logs.html', logs = log)

@app.route('/copiar_relatorios', methods=['GET', 'POST'])
@csrf.exempt
def copiar_relatorios():

    ufvs_empresas = db.show_all_ufvs()
    dic_cams = {}

    for usina in ufvs_empresas:
        empresa = usina['empresa']
        nome_usina = usina['nome']

        if empresa not in dic_cams:
            dic_cams[empresa] = {}

        if nome_usina not in dic_cams[empresa]:
            dic_cams[empresa][nome_usina] = []
    
    mensagem = 'RELATÓRIO DE MONITORAMENTO\n'

    report_type = request.form.get('select-relatorio')
    ufvs = request.form.getlist('optionUFV')
    submit = request.form.get('submit')
    path = request.args.get("path")
    cams = None

    if report_type == 'all': cams = db.data_for_copy_reports()
    elif report_type == 'specific': cams =  db.data_for_copy_report_specific(ufvs)

    # Separa câmeras por usina
    for cam in cams:
        for empresa in dic_cams:
            if cam['usina'] in dic_cams[empresa]:
                dic_cams[empresa][cam['usina']].append({
                    'nome':cam['nome'],
                    'status':cam['status']
                })
                break

    print(dic_cams)

    # Ordena cameras de usina e ordem alfabética
    for empresa in dic_cams:
        for ufv in dic_cams[empresa]:
            dic_cams[empresa][ufv] = sorted(dic_cams[empresa][ufv], key=lambda x: x["nome"])

    for empresa in dic_cams:
        for usina in dic_cams[empresa]:
            onlines = 0
            mensagemTituloUsina = ''
            mensagemCamerasUsina = ''

            for cam in dic_cams[empresa][usina]:
                if cam['status'] == 'online': onlines += 1
                mensagemCamerasUsina += f'- *{cam["nome"]}:* {cam["status"].title()}\n'

            if len(dic_cams[empresa][usina]) == 0: continue
            elif len(dic_cams[empresa][usina]) == onlines and len(dic_cams[empresa][usina]) != 0: 
                mensagemTituloUsina = f'🟢 *{usina}*'
            elif onlines > 0 and len(dic_cams[empresa][usina]) > onlines: 
                mensagemTituloUsina = f'🟡 *{usina} - {onlines}/{len(dic_cams[empresa][usina])}*'
            elif onlines == 0: 
                mensagemTituloUsina = f'🔴 *{usina} - Offline*'

            mensagem += '\n' + mensagemTituloUsina
            if submit == 'completo': mensagem += '\n' + mensagemCamerasUsina + '\n'

    
    return jsonify({'mensagem':mensagem, 'redirect_to': path})
        
@app.route('/usinas_copia', methods=['GET', 'POST'])
@csrf.exempt
def usinas_copia():
    ufvs = db.search_ufvs()
    ufvs_in_company = {}

    for ufv in ufvs:
        if ufv['empresa'] not in ufvs_in_company:
            ufvs_in_company[ufv['empresa']] = [ufv['nome']]
        else:
            ufvs_in_company[ufv['empresa']].append(ufv['nome'])

    return jsonify(ufvs_in_company)

@app.route('/salvar_multi_relatorios', methods=['GET', 'POST'])
@csrf.exempt
def salvar_multi_relatorios():
    dados = request.get_json()
    path = request.args.get("path")
    for ufv, status in dados['multiUfvs'].items():
        db.create_record_elipse(id_report = dados['id_report'], time = dados['hora'], place = ufv, status = status, obs = '')
    return jsonify({'status':'ok', 'redirect_to': path})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
