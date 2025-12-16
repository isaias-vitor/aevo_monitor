import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
from flask import flash

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY') 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def search_login(user):
    try:
        verification = supabase.table('usuarios').select('*').eq('email', user).execute()
        print(verification.data)
        return verification.data[0] if verification.data else False
    except Exception as e:
        flash(f'Erro ao acessar o banco de dados: {str(e)}', 'danger')

def search_id_login(id):
    try:
        search = supabase.table('usuarios').select('*').eq('id', id).execute()
        return search.data[0]
    except:
        flash('Usuário não encontrado no banco de dados')

def search_name_user(id_user):
    names = supabase.table('usuarios').select('nome').eq('id', id_user).execute()
    return names.data[0]['nome']

def search_ufvs():
    try:
        ufvs = supabase.table('usinas').select('nome', 'empresa').execute()
        return ufvs.data
    except Exception as e:
        print(e)

def qtd_pages():
    qtd = supabase.table('relatorios').select('*', count='exact').limit(0).execute()
    qtd = int(qtd.count)
    i = 1
    for i in range (1, 11):
        if (i * 25) > qtd:
            return i

def data_for_copy_report(ufv):
    try:
        cams = supabase.table('cameras').select('nome', 'status').eq('usina', ufv).order('id', desc=True).execute()
        return cams.data
    except Exception as e:
        print(e)

def data_for_copy_reports():
    try:
        cams = supabase.table('cameras').select('nome', 'status', 'usina').order('usina', desc=False).execute()
        return cams.data
    except Exception as e:
        print(e)

def data_for_copy_report_specific(ufvs_list):
    try:
        cams = supabase.table('cameras').select('nome', 'status', 'usina').in_('usina', ufvs_list).order('usina', desc=False).execute()
        return cams.data
    except Exception as e:
        print(e)

def switch_status_ufv(ufv, status):
    supabase.table('usinas').update({'online':status}).eq('nome', ufv).execute()

# Busca por relatório aberto em nome do usuário
def show_open_report(user_id):
    try:
        report = supabase.table('relatorios').select('dia').eq('responsavel', user_id).eq('status', 'TRUE').limit(1).execute()
        return report.data
    except Exception as e:
        error_message = f'Erro ao verificar se o usuario ja tem relatorio aberto: {str(e)}'
        flash(error_message)
        print(error_message)

# Busca por relatórios abertos
def show_all_open_reports():
    try:
        report = supabase.table('relatorios').select('*').eq('status', 'TRUE').order('id', desc=False).execute()
        return report.data
    except Exception as e:
        error_message = f'Erro ao buscar relatórios abertos no banco de dados: {str(e)}'
        flash(error_message)
        print(error_message)

# Busca todos os registros de um relatório, em um local específico
def show_record(id_report, local_name):
    try:
        records = supabase.table('registros_elipse').select('*').eq('id_relatorio', id_report).eq('local', local_name).order('id', desc=False).execute()
        return records.data
    except Exception as e:
        flash(f'Erro ao buscar no banco de dados: {str(e)}')

# Busca registros de relatorios fechados, limitando a quantidade a buscada. É ordenado de maneira a mostrar o mais recente
def show_closed_reports(amount):
    try:
        reports = supabase.table('relatorios').select('*').order('id', desc=True).eq('status', 'FALSE').limit(amount).execute()
        return reports.data
    except Exception as e:
        flash(f'Erro ao buscar no banco de dados: {str(e)}')

# Busca todos os relatorios fechados
def show_all_closed_reports():
    try:
        reports = supabase.table('relatorios').select('*').order('id', desc=True).eq('status', 'FALSE').execute()
        return reports.data
    except Exception as e:
        flash(f'Erro ao buscar no banco de dados: {str(e)}')

# Busca o relatório de câmeras para relatórios fechados
def show_cams_closed_report(id_relatorio):
    try:
        cams = supabase.table('relatorios_cameras').select('dados').eq('id_relatorio', id_relatorio).execute()
        return cams.data
    except Exception as e:
        flash(f'Erro ao buscar relatório de câmeras: {str(e)}')

# Busca todas as câmeras da usina
def show_cams(ufv):
    try:
        cams = supabase.table('cameras').select('*').eq('usina', ufv).order('id', desc=False).execute()
        return cams.data
    except Exception as e:
        flash(f'Erro ao buscar câmeras: {str(e)}')

# Busca o nome de todas as UFVs de uma empresa
def show_ufvs(empresa):
    try:
        ufvs = supabase.table('usinas').select('nome').eq('empresa', empresa).order('id', desc=False).execute()
        return ufvs.data
    except Exception as e:
        flash(f'Erro ao buscar UFVs: {str(e)}')

# Busca dados de localição da usina
def show_local_ufv(ufv):
    try:
        local = supabase.table('usinas').select('endereco', 'geolocalizacao').eq('nome', ufv).execute()
        return local.data[0]
    except Exception as e:
        flash(f'Erro ao dados de localização: {str(e)}')

# Busca contatos de UFV
def show_contacts_ufv(ufv):
    try:
        contacts = supabase.table('contatos').select('*').eq('usina', ufv).order('id', desc=False).execute()
        return contacts.data
    except Exception as e:
        flash(f'Erro ao buscar contatos da UFV: {str(e)}')
    
# Busca credenciais
def show_passwords():
    try:
        passwords = supabase.table('senhas').select('*').execute()
        return passwords.data    
    except Exception as e:
        flash(f'Erro ao buscar credenciais: {str(e)}')

# Busca usuários
def show_users():
    users = supabase.table('usuarios').select('*').order('id', desc=False).execute()
    return users.data

# Busca o id do responsável pelo relatório
def id_responsible(id_report):
    responsible = supabase.table('relatorios').select('responsavel').eq('id', id_report).execute()
    return responsible.data[0]

# Busca as ocorrencias de um relatorio
def show_occurrences_report(id_report):
    try:
        occurrences = supabase.table('ocorrencias').select('*').eq('id_relatorio', id_report).order('id', desc=False).execute()
        return occurrences.data
    except Exception as e:
        flash(f'Erro ao buscar ocorrencias: {str(e)}')
        print(f'Erro ao buscar ocorrencias: {str(e)}')

# Busca relatorios de uma pagina
def show_report_page(page):
    try:
        page_number = int(page)
        initial_number = (page_number - 1) * 24
        final_number = page_number * 24
        reports = supabase.table('relatorios').select('*').order('id', desc=True).range(initial_number, final_number).execute()
        return reports.data
    except Exception as e:
        flash(f'Erro ao buscar relatórios: {str(e)}')
        print(f'Erro ao buscar relatórios: {str(e)}')

# Busca logs
def show_logs():
    try:
        logs = supabase.table('logs').select('*').order('id', desc=True).execute()
        return logs.data
    except Exception as e:
        pass

# Bususca todas ufvs
def show_all_ufvs():
    ufvs = supabase.table('usinas').select('nome', 'empresa').execute()
    return ufvs.data

# Busca status de usina
def show_status_ufv(ufv):
    status = supabase.table('usinas').select('online').eq('nome', ufv).execute()
    return status.data[0]

# Cria um relatório aberto associado ao usuário
def create_report(user, user_name):
    try:
        # Insere registro com informações do formulário
        data_atual = datetime.now()
        data_atual = data_atual.strftime('%d/%m/%Y')
        hora_atual = datetime.now().hour
        minuto_atual = datetime.now().minute
        turno = 'noturno' if hora_atual in [19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6] else 'diurno'
        supabase.table('relatorios').insert({'dia':data_atual, 'responsavel':user, 'status':'TRUE', 'turno':turno}).execute()
        supabase.table('logs').insert({
            'data':data_atual, 
            'horario':f'{hora_atual}:{minuto_atual}',
            'acao':f'Criação de novo relatório',
            'usuario':user_name}).execute()
    except Exception as e:
        flash(f'Erro ao criar relatório: {str(e)}')

# Cria um registro no relatório de determinada UFV
def create_record_elipse(id_report, time, place, status, obs):
    try:
        # Cria registro com dados do formulário
        supabase.table('registros_elipse').insert({
            'local':place,
            'horario':time,
            'status':status,
            'observacao':obs,
            'id_relatorio':id_report,
            'referencia':'Usina'
        }).execute()

        # Insere registro com informações das câmeras
        cams = supabase.table('cameras').select('nome', 'status').eq('usina', place).order('id', desc=False).execute()
        cams = cams.data

        online = 0
        cams_off = []

        for cam in cams:
            if cam['status'] == 'online': 
                online += 1
            else:
                cams_off.append(cam['nome'])


        if len(cams) == online:
            supabase.table('registros_elipse').insert({
                'local':place,
                'horario':time,
                'status':'Ok',
                'observacao':'',
                'id_relatorio':id_report,
                'referencia':'Câmeras'
            }).execute()
        elif online != 0 and len(cams) > online:

            text_cams = 'Câmeras Offline: '
            text_list_off = ', '.join(cams_off)
            text_cams += text_list_off

            supabase.table('registros_elipse').insert({
                'local':place,
                'horario':time,
                'status':f'{online}/{len(cams)}',
                'observacao':text_cams,
                'id_relatorio':id_report,
                'referencia':'Câmeras'
            }).execute()
        elif online == 0:
            supabase.table('registros_elipse').insert({
            'local':place,
            'horario':time,
            'status':'Offline',
            'observacao':'Todas as câmeras estão Offlines',
            'id_relatorio':id_report,
            'referencia':'Câmeras'
        }).execute()
            

    except Exception as e:
        flash(f'Erro ao criar registro: {str(e)}')
    
# Retorna o status do relatório (Aberto oU Fechado)
def status_report(id):
    try:
        status = supabase.table('relatorios').select('status').eq('id', id).execute()
        return status.data[0]
    except Exception as e:
        flash(f'Erro ao buscar status do relatório: {str(e)}')

# Adiciona nova câmera a usina
def add_cam(ufv, nome, tipo, obs, status, user):
    try:
        supabase.table('cameras').insert({
            'usina':ufv,
            'nome':nome,
            'tipo':tipo,
            'observacao':obs,
            'status':status
        }).execute()

        # Configuração de log
        data_atual = datetime.now()
        data_atual = data_atual.strftime('%d/%m/%Y')
        hora_atual = datetime.now().hour
        minuto_atual = datetime.now().minute
        supabase.table('logs').insert({
            'data':data_atual, 
            'horario':f'{hora_atual}:{minuto_atual}',
            'acao':f'Criação de nova câmera, com nome {nome}, do tipo {tipo}, na usina {ufv}',
            'usuario':user}).execute()
    except Exception as e:
        flash(f'Erro ao adicionar nova câmera: {str(e)}')

# Adiciona UFV
def add_ufv(nome, empresa, user):
    try:
        supabase.table('usinas').insert({
            'nome':nome,
            'empresa':empresa
        }).execute()

        # Configuração de log
        data_atual = datetime.now()
        data_atual = data_atual.strftime('%d/%m/%Y')
        hora_atual = datetime.now().hour
        minuto_atual = datetime.now().minute
        supabase.table('logs').insert({
            'data':data_atual, 
            'horario':f'{hora_atual}:{minuto_atual}',
            'acao':f'Criação de nova UFV, com nome {nome}, da empresa {empresa}',
            'usuario':user}).execute()
    except Exception as e:
        flash(f'Erro ao adicionar nova UFV: {str(e)}')

# Adiciona contato a UFV
def add_contact_ufv(ufv, nome, empresa, telefone):
    try:
        supabase.table('contatos').insert({
            'nome':nome,
            'usina':ufv,
            'empresa':empresa,
            'telefone':telefone
        }).execute()
    except Exception as e:
        flash(f'Erro ao inserir informações de contato no banco de dados: {str(e)}')

# Adicionar credencial
def add_password(software, usuario, senha, descricao, observacao):
    try:
        supabase.table('senhas').insert({
            'software':software,
            'usuario':usuario,
            'senha':senha,
            'descricao':descricao,
            'observacao':observacao
        }).execute()
    except Exception as e:
        flash(f'Erro ao inserir crendenciais no banco de dados: {str(e)}')

# Adiciona usuário
def add_user(nome, email, senha, nivel, empresa):
    try:
        supabase.table('usuarios').insert({
            'nome':nome,
            'email':email,
            'senha':senha,
            'nivel':nivel,
            'empresa':empresa
        }).execute()
    except Exception as e:
        print(f'Erro ao inserir usuário no banco de dados: {str(e)}')

# Adicionar ocorrencia
def add_occurrence(horario, status, acoes, observacoes, id_relatorio, empresa, usina, data, responsavel):
    try:
        data_br = data.split('-')
        day = data_br[2]
        month = data_br[1]
        year = data_br[0]
        data = f'{day}/{month}/{year}'
        horario = horario[0:6]
        supabase.table('ocorrencias').insert({
            'horario':horario,
            'status':status,
            'acoes':acoes, 
            'observacoes':observacoes,
            'id_relatorio':id_relatorio,
            'empresa':empresa,
            'usina':usina,
            'data':data,
            'responsavel':responsavel
        }).execute()
    except Exception as e:
        print(f'Erro ao editar ocorrencia: {e}')
        flash(f'Erro ao editar ocorrencia! {e}')



# Edita registro de relatório Elipse
def edit_record_elipse(id_report, time, place, status, obs):
    try:    
        supabase.table('registros_elipse').update({
            'local':place,
            'horario':time,
            'status':status,
            'observacao':obs
        }).eq('id', id_report).execute()
    except Exception as e:
        flash(f'Erro ao editar registro: {str(e)}')

# Edita câmera
def edit_cam(id_cam, nome, tipo, status, obs):
    try:
        supabase.table('cameras').update({
            'nome':nome,
            'tipo':tipo,
            'status':status,
            'observacao':obs
        }).eq('id', id_cam).execute()    
    except Exception as e:
        flash(f'Erro ao editar câmera: {str(e)}')    

# Edita informações de localização da UFV
def edit_local_ufv(ufv, endereco, maps):
    try:
        supabase.table('usinas').update({
            'endereco':endereco,
            'geolocalizacao':maps
        }).eq('nome', ufv).execute()
    except Exception as e:
        flash(f'Erro ao editar localização: {str(e)}') 

# Edita informações de contato da UFV
def edit_contact_ufv(id_edit_contact, ufv, nome, empresa, telefone):
    try:
        supabase.table('contatos').update({
            'nome':nome,
            'usina':ufv,
            'empresa':empresa,
            'telefone':telefone
        }).eq('id', id_edit_contact).execute()
    except Exception as e:
        flash(f'Erro ao editar contato: {str(e)}')

# Edita credencial
def edit_credential(id_credentials, software, usuario, senha, descricao, observacao):
    try:
        supabase.table('senhas').update({
            'software':software,
            'usuario':usuario,
            'senha':senha,
            'descricao':descricao,
            'observacao':observacao
        }).eq('id', id_credentials).execute()
    except Exception as e:
        flash(f'Erro ao editar credencial: {str(e)}')

# Edita câmera pelo relatório
def edit_cam_report(id_cam, status, obs):
    try:
        supabase.table('cameras').update({
            'status':status,
            'observacao':obs}).eq('id', id_cam).execute()
    except Exception as e:
        flash(f'Erro ao editar câmera: {str(e)}')

# Edita usuário
def edit_user(id_user, nome, email, nivel, empresa):
    try:
        supabase.table('usuarios').update({
            'nome':nome,
            'email':email,
            'nivel':nivel,
            'empresa':empresa
        }).eq('id', id_user).execute()
    except Exception as e:
        flash(f'Erro ao editar usuário: {str(e)}')

# Edita senha do usuário
def edit_new_password(id_user, senha):
    print(senha)
    try:
        supabase.table('usuarios').update({'senha': senha}).eq('id', id_user).execute()
    except Exception as e:
        print(f'Erro ao alterar senha: {str(e)}')

# Edita ocorrência
def edit_occurrence(id_ocorrencia, data, horario, status, acoes, observacoes):
    print('entrou')
    try:
        data_br = data.split('-')
        day = data_br[2]
        month = data_br[1]
        year = data_br[0]
        data = f'{day}/{month}/{year}'
        horario = horario[0:6]
        supabase.table('ocorrencias').update({
            'data':data,
            'horario':horario,
            'status':status,
            'acoes':acoes, 
            'observacoes':observacoes,
        }).eq('id', id_ocorrencia).execute()
    except Exception as e:
        print(f'Erro ao editar ocorrencia: {e}')
        flash(f'Erro ao editar ocorrencia! {e}')



# Exclui registro Elipse
def delete_record_elipse(id_report):    
    try:
        result = supabase.table('registros_elipse').delete().eq('id', id_report).execute()
    except Exception as e:
        print(f"ERRO: {e}")

# Exclui câmera
def delete_cam(id_cam):
    try:
        supabase.table('cameras').delete().eq('id', id_cam).execute()
    except Exception as e:
        flash(f'Erro ao excluir câmera: {str(e)}')

# Exclui contato de UFV
def delete_contact_ufv(id_contact):
    try:
        supabase.table('contatos').delete().eq('id', id_contact).execute()
    except Exception as e:
        flash(f'Erro ao excluir contato: {str(e)}')

# Exclui credencial
def delete_credential(id_credential):
    try:
        supabase.table('senhas').delete().eq('id', id_credential).execute()
    except Exception as e:
        flash(f'Erro ao excluir credencial: {str(e)}')

# Exclui usuário
def delete_user(id_user):
    try:
        supabase.table('usuarios').delete().eq('id', id_user).execute()
    except Exception as e:
        flash(f'Erro ao excluir usuário: {str(e)}')

# Exclui ocorrência
def delete_occurrence(id_occurrence):
    try:
        supabase.table('ocorrencias').delete().eq('id', id_occurrence).execute()
    except Exception as e:
        print(f'Erro ao excluir a ocorrência: {str(e)}')
        flash(f'Erro ao excluir a ocorrência: {str(e)}')


# Fecha o relatório
def close_report(id_report):
    try:
        supabase.table('relatorios').update({'status':'FALSE'}).eq('id', id_report).execute()
    except Exception as e:
        flash(f'Erro ao fechar relatório: {str(e)}')

# Armazena uma cópia do último estado das câmeras antes de fechar o relatório
def close_cams_report(empresas, id_relatorio):
    try:
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
    except Exception as e:
        flash(f'Erro ao gravar o relatório das câmeras: {str(e)}')
