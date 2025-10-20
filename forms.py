from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, PasswordField, TelField, TimeField, DateField
from wtforms.validators import DataRequired

class CreateReport(FlaskForm):
    submit = SubmitField('Abrir')

class CreateRecord(FlaskForm):
    time = StringField('horario', render_kw={'class':'form-control', 'readonly':True})
    status = SelectField('status', choices=[
        ('Ok', 'Ok'),
        ('Sem conexão', 'Sem conexão'),
        ('Religamento', 'Religamento'),
        ('Incêndio', 'Incêndio'),
        ('Furto', 'Furto'),
        ('Invasão', 'Invasão')
    ], render_kw={'class':'form-select'})
    observation = TextAreaField('obs', render_kw={'class':'form-control'})
    submit_create_report = SubmitField('Criar', render_kw={'class':'btn btn-primary'})

class CloseReport(FlaskForm):
    submit_close_report = SubmitField('Fechar Relatório', render_kw={'class':'btn btn-outline-dark'})

class EditRecord(FlaskForm):
    timeEditElipse = StringField('horario', render_kw={'class':'form-control', 'readonly':True})
    statusEditElipse = SelectField('status', choices=[
        ('Ok', 'Ok'),
        ('Sem conexão', 'Sem conexão'),
        ('Religamento', 'Religamento'),
        ('Incêndio', 'Incêndio'),
        ('Furto', 'Furto'),
        ('Invasão', 'Invasão')
    ], render_kw={'class':'form-select'})
    observationEditElipse = TextAreaField('obs', render_kw={'class':'form-control'})
    id_recordEditElipse = StringField('id_record')
    submit_edit_record = SubmitField('Editar', render_kw={'class':'btn btn-primary'})

class DeleteRecord(FlaskForm):
    # Excluir registro de determinada UFV
    id_recordDeleteElipse = StringField('id_record')
    submit_delete_record = SubmitField('Deletar', render_kw={'class':'btn btn-danger'})

class Login(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Login")

class AddCam(FlaskForm):
    name = StringField('Nome')
    tipo = SelectField('tipo', choices=[
        ('Bullet', 'Bullet'),
        ('Dome', 'Dome'),
        ('Dome Speed', 'Dome Speed'),
        ('Térmica', 'Térmica'),
    ])
    obs = TextAreaField('obs')
    status = SelectField('Status', choices=[
        ('online', 'Online'),
        ('offline', 'Offline')
    ])
    submit = SubmitField('Adicionar')

class EditCam(FlaskForm):
    id_cam_edit = StringField()
    name_edit_cam = StringField('Nome')
    tipo_edit_cam = SelectField('tipo', choices=[
        ('Bullet', 'Bullet'),
        ('Dome', 'Dome'),
        ('Dome Speed', 'Dome Speed'),
        ('Térmica', 'Térmica'),
    ])
    obs_edit_cam = TextAreaField('obs')
    status_edit_cam = SelectField('Status', choices=[
        ('online', 'Online'),
        ('offline', 'Offline')
    ])
    submit_edit_cam = SubmitField('Editar')

class EditCamRecord(FlaskForm):
    id_cam_edit_record = StringField()
    obs_edit_cam_record = TextAreaField('obs')
    status_edit_cam_record = SelectField('Status', choices=[
        ('online', 'Online'),
        ('offline', 'Offline')
    ])
    submit_edit_cam_record = SubmitField('Editar')

class AddContact(FlaskForm):
    nameContact = StringField('Nome')
    enterpriseContact = StringField('Empresa')
    phoneContact = StringField('Telefone')
    submitContact = SubmitField('Adicionar Contato')

class DeleteCam(FlaskForm):
    id_cam_delete = StringField()
    submit_delete_cam = SubmitField('Excluir')

class AddUFV(FlaskForm):
    name_add_ufv = StringField()
    submit_add_ufv = SubmitField('Adicionar')

class EditLocal(FlaskForm):
    endereco_edit_local = StringField()
    maps_edit_local = StringField()
    submit_edit_local = SubmitField('Editar')

class AddContact(FlaskForm):
    name_add_contact = StringField()
    company_add_contact = StringField()
    phone_add_contact = TelField()
    submit_add_contact = SubmitField('Adicionar')

class EditContact(FlaskForm):
    id_edit_contact = StringField()
    name_edit_contact = StringField()
    company_edit_contact = StringField()
    phone_edit_contact = TelField()
    submit_edit_contact = SubmitField('Editar')

class DeleteContact(FlaskForm):
    id_contact_delete = StringField()
    submit_delete_contact = SubmitField('Excluir')

class AddPassword(FlaskForm):
    software_add_password = StringField()
    user_add_password = StringField()
    password_add_password = StringField()
    description_add_password = StringField()
    obs_add_password = StringField()
    submit_add_password = SubmitField('Adicionar')

class EditPassword(FlaskForm):
    id_edit_password = StringField()
    software_edit_password = StringField()
    user_edit_password = StringField()
    password_edit_password = StringField()
    description_edit_password = StringField()
    obs_edit_password = StringField()
    submit_edit_password = SubmitField('Editar')

class DeleteCrendential(FlaskForm):
    id_credential_delete = StringField()
    submit_delete_credential = SubmitField('Excluir')

class AddUser(FlaskForm):
    name_add_user = StringField()
    email_add_user = StringField()
    level_add_user = SelectField(choices=[
        ('monitor', 'Monitor'),
        ('gestor', 'Gestor'),
        ('adm', 'Administrador')
    ])
    company_add_user = StringField()
    submit_add_user = SubmitField('Adicionar')

class EditUser(FlaskForm):
    id_edit_user = StringField()
    name_edit_user = StringField()
    email_edit_user = StringField()
    level_edit_user = SelectField(choices=[
        ('monitor', 'Monitor'),
        ('gestor', 'Gestor'),
        ('adm', 'Administrador')
    ])
    company_edit_user = StringField()
    submit_edit_user = SubmitField('Editar')

class DeleteUser(FlaskForm):
    id_delete_user = StringField()
    submit_delete_user = SubmitField('Excluir')

class NewPassword(FlaskForm):
    id_new_password = StringField()
    new_password = StringField()
    submit_new_password = SubmitField('Salvar')

class AddOccurrence(FlaskForm):
    id_report = StringField()
    company_add_occurrence = StringField()
    ufv_add_occurrence = StringField()
    date_add_occurrence = DateField()
    hour_add_occurrence = TimeField()
    status_add_occurrence = SelectField(choices=[
        ('religamento', 'Religamento'),
        ('furto', 'Furto'),
        ('invasao', 'Invasao'),
        ('incendio', 'Incêndio'),
        ('outro', 'Outro')
    ])
    actions_add_occurrence = TextAreaField()
    observations_add_occurrence = TextAreaField()
    submit_add_occurrence = SubmitField('Salvar')

class EditOccurrence(FlaskForm):
    id_edit_occurrence = StringField()
    date_edit_occurrence = DateField()
    hour_edit_occurrence = TimeField()
    status_edit_occurrence = SelectField(choices=[
        ('religamento', 'Religamento'),
        ('furto', 'Furto'),
        ('invasao', 'Invasao'),
        ('incendio', 'Incêndio'),
        ('outro', 'Outro')
    ])
    actions_edit_occurrence = TextAreaField()
    observations_edit_occurrence = TextAreaField()
    submit_edit_occurrence = SubmitField('Editar')

class DeleteOccurrence(FlaskForm):
    id_delete_occurrence = StringField()
    submit_delete_occurrence = SubmitField('Excluir')