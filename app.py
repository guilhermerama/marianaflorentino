import os
import os.path as op

from flask import Flask, render_template, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.event import listens_for
from jinja2 import Markup
from flask_admin import Admin, form
from flask_admin.form import rules
from flask_admin.contrib import sqla

# Create application
app = Flask(__name__)

# Create dummy secrety key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

tipos_projetos = ['comercial','residencial', 'institucional', 'iluminacao']

# Create directory for file fields to use
file_path = op.join(op.dirname(__file__), 'static/files')
#try:
#    os.mkdir(file_path)
#except OSError:
#    print 'Erro ao tentar criar diretorio'

class Projeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.Unicode(64))
    cliente = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))#representa o thumb

    def __unicode__(self):
        return self.name

@listens_for(Projeto, 'after_delete')
def del_projeto(mapper, connection, target):
    if target.path:
        # Delete projeto
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass

        # Delete thumbnail
        try:
            os.remove(op.join(file_path,
                              form.thumbgen_filename(target.path)))
        except OSError:
            pass

class ProjetoView(sqla.ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        return Markup('<img src="%s">' % url_for('static', filename='files/' + form.thumbgen_filename(model.path)))

    column_formatters = {
        'path': _list_thumbnail
    }

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        'path': form.ImageUploadField('Image',
                                      base_path=file_path,
                                      thumbnail_size=(400, 300, True))
    }

# Create admin
admin = Admin(app, 'Administrador', template_mode='bootstrap3')

# Add views
admin.add_view(ProjetoView(Projeto, db.session))



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projetos/<tipo>')
def projetos(tipo):

    if tipo in tipos_projetos:	
    	projetos = Projeto.query.all();	
    	return render_template('projetos.html', projetos=projetos, tipo=tipo);
    else:
	return "" #TODO implementar tela de erro 404

@app.route("/upload", methods=["GET"])
def render_upload():
    return render_template('upload.html');

@app.route("/upload", methods=["POST"])
def upload():
    uploaded_files = request.files.getlist("file[]")
    print uploaded_files
    flash("sucesso")
    return ""

def thumb_name(name):
    return form.thumbgen_filename(name)

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    #app_dir = op.realpath(os.path.dirname(__file__))
    #database_path = op.join(app_dir, app.config['DATABASE_FILE'])
    db.create_all()	
    #if not os.path.exists(database_path):
    #    build_sample_db()
    
    
    app.jinja_env.globals.update(thumb_name=thumb_name)
    app.run(debug=True)
