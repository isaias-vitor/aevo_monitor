import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
from flask import flash

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY') 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def show_all_open_reports():
    # Procura por relatorios abertos
    try:
        report = supabase.table('relatorios').select('*').eq('status', 'TRUE').order('id', desc=False).execute()
        return report.data
    except Exception as e:
        error_message = f'Erro ao buscar relatórios abertos no banco de dados: {str(e)}'
        flash(error_message)
        print(error_message)

def search_login(user):
    try:
        verification = supabase.table('usuarios').select('*').eq('email', user).execute()
        if verification.data: return verification.data[0]
        else: return False
    except Exception as e:
        flash(f'Erro ao acessar o banco de dados: {str(e)}', 'danger')

def search_id_login(id):
    search = supabase.table('usuarios').select('*').eq('id', id).execute()
    return search.data[0]

def show_record(id_report, local_name):
    # Busca todos os registros de um relatório, em um local específico
    records = supabase.table('registros_elipse').select('*').eq('ref', id_report).eq('local', local_name).order('id', desc=False).execute()
    return records.data

def show_closed_reports(amount):
    reports = supabase.table('relatorios').select('*').order('id', desc=True).eq('status', 'FALSE').limit(amount).execute()
    return reports.data

def show_all_closed_reports():
    reports = supabase.table('relatorios').select('*').order('id', desc=True).eq('status', 'FALSE').execute()
    return reports.data

def create_report(user):
    # Cria um relatório aberto para o usuário
    data_atual = datetime.now()
    data_atual = data_atual.strftime('%d/%m/%Y')
    hora_atual = datetime.now().hour
    turno = 'noturno' if hora_atual in [19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6] else 'diurno'
    supabase.table('relatorios').insert({'dia':data_atual, 'responsavel':user, 'status':'TRUE', 'turno':turno}, ).execute()

def create_record_elipse(id_report, time, place, status, obs):
    # Cria uma linha no relatório de determinada UFV
    supabase.table('registros_elipse').insert({
        'local':place,
        'horario':time,
        'status':status,
        'observacao':obs,
        'ref':id_report}).execute()
    
def close_report(id_report):
    # Fecha o relatório
    supabase.table('relatorios').update({'status':'FALSE'}).eq('id', id_report).execute()

def status_report(id):
    status = supabase.table('relatorios').select('status').eq('id', id).execute()
    return status.data[0]

def edit_record_elipse(id_report, time, place, status, obs):
    # Cria uma linha no relatório de determinada UFV
    supabase.table('registros_elipse').update({
        'local':place,
        'horario':time,
        'status':status,
        'observacao':obs}).eq('id', id_report).execute()
    
def delete_record_elipse(id_report):    
    try:
        result = supabase.table('registros_elipse').delete().eq('id', id_report).execute()
    except Exception as e:
        print(f"ERRO: {e}")

def close_cams_report(empresas, id_relatorio):
    dados = []
    for empresa, ufvs in empresas.items():
        for ufv in ufvs:
            cams = show_cams(ufv)
            cams_list = []
            for cam in cams:
                cams_list.append({
                    'nome':cam['nome'],
                    'status':cam['status'],
                    'obs':cam['observacao']
                })
            dados.append({ufv:cams_list})
    supabase.table('relatorios_cameras').insert({
        'dados':dados,
        'id_relatorio':id_relatorio
    }).execute()

def show_cams_closed_report(id_relatorio):
    cams = supabase.table('relatorios_cameras').select('dados').eq('id_relatorio', id_relatorio).execute()
    return cams.data

def add_cam(ufv, nome, tipo, obs, status):
    supabase.table('cameras').insert({
        'usina':ufv,
        'nome':nome,
        'tipo':tipo,
        'observacao':obs,
        'status':status}).execute()

def show_cams(ufv):
    cams = supabase.table('cameras').select('*').eq('usina', ufv).order('id', desc=False).execute()
    return cams.data

def edit_cam(id_cam, nome, tipo, status, obs):
    supabase.table('cameras').update({
        'nome':nome,
        'tipo':tipo,
        'status':status,
        'observacao':obs}).eq('id', id_cam).execute()
    
def delete_cam(id_cam):
    supabase.table('cameras').delete().eq('id', id_cam).execute()

def add_ufv(nome, empresa):
    supabase.table('usinas').insert({
        'nome':nome,
        'empresa':empresa
    }).execute()

def show_ufvs(empresa):
    ufvs = supabase.table('usinas').select('nome').eq('empresa', empresa).order('id', desc=False).execute()
    return ufvs.data

def edit_local_ufv(ufv, endereco, maps):
    supabase.table('usinas').update({
        'endereco':endereco,
        'geolocalizacao':maps
    }).eq('nome', ufv).execute()

def show_local_ufv(ufv):
    local = supabase.table('usinas').select('endereco', 'geolocalizacao').eq('nome', ufv).execute()
    return local.data[0]

def add_contact_ufv(ufv, nome, empresa, telefone):
    supabase.table('contatos').insert({
        'nome':nome,
        'usina':ufv,
        'empresa':empresa,
        'telefone':telefone
    }).execute()

def edit_contact_ufv(id_edit_contact, ufv, nome, empresa, telefone):
    supabase.table('contatos').update({
        'nome':nome,
        'usina':ufv,
        'empresa':empresa,
        'telefone':telefone
    }).eq('id', id_edit_contact).execute()

def show_contacts_ufv(ufv):
    contacts = supabase.table('contatos').select('*').eq('usina', ufv).order('id', desc=False).execute()
    return contacts.data

def delete_contact_ufv(id_contact):
    supabase.table('contatos').delete().eq('id', id_contact).execute()

def add_password(software, usuario, senha, descricao, observacao):
    supabase.table('senhas').insert({
        'software':software,
        'usuario':usuario,
        'senha':senha,
        'descricao':descricao,
        'observacao':observacao
    }).execute()

def show_passwords():
    passwords = supabase.table('senhas').select('*').execute()
    return passwords.data

def edit_credential(id_credentials, software, usuario, senha, descricao, observacao):
    supabase.table('senhas').update({
        'software':software,
        'usuario':usuario,
        'senha':senha,
        'descricao':descricao,
        'observacao':observacao
    }).eq('id', id_credentials).execute()

def delete_credential(id_credential):
    supabase.table('senhas').delete().eq('id', id_credential).execute()

def edit_cam_report(id_cam, status, obs):
    response = supabase.table('cameras').update({
        'status':status,
        'observacao':obs}).eq('id', id_cam).execute()
    print(response)

def add_user(nome, email, senha, nivel, empresa):
    supabase.table('usuarios').insert({
        'nome':nome,
        'email':email,
        'senha': senha,
        'nivel':nivel,
        'empresa':empresa
    }).execute()

def edit_user(id_user, nome, email, senha, nivel, empresa):
    supabase.table('usuarios').update({
        'nome':nome,
        'email':email,
        'senha': senha,
        'nivel':nivel,
        'empresa':empresa
    }).eq('id', id_user).execute()

def delete_user(id_user):
    supabase.table('usuarios').delete().eq('id', id_user).execute()

def show_users():
    users = supabase.table('usuarios').select('*').order('id', desc=False).execute()
    return users.data

