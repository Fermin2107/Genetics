from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://animalesdb_user:z1xIETnjgzHv4GZXEDNQlRC9Cq0tDJfX@dpg-d29unpndiees738f42u0-a.oregon-postgres.render.com/animalesdb_6g2y'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secreto_muy_fuerte'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# MODELOS

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    razas = db.relationship('Raza', backref='usuario', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Raza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    animales = db.relationship('Animal', backref='raza', lazy=True)
    __table_args__ = (db.UniqueConstraint('nombre', 'user_id', name='uq_raza_nombre_user'),)

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raza_id = db.Column(db.Integer, db.ForeignKey('raza.id'), nullable=False)
    rp = db.Column(db.String(50), nullable=False)
    hba = db.Column(db.String(50))
    nombre = db.Column(db.String(100))
    sexo = db.Column(db.String(10))
    fecha_nac = db.Column(db.Date)
    nacimiento = db.Column(db.String(10))
    color = db.Column(db.String(50))
    padre = db.Column(db.String(100))
    madre = db.Column(db.String(100))
    abuelo_paterno = db.Column(db.String(100))
    abuelo_materno = db.Column(db.String(100))
    familia = db.Column(db.String(100))
    f = db.Column(db.String(20))
    tamano = db.Column(db.String(30))
    pezuñas = db.Column(db.Float)
    articulacion = db.Column(db.Float)
    ap_delanteros = db.Column(db.String(50))
    ap_traseros = db.Column(db.String(50))
    curv_garrones = db.Column(db.String(50))
    apert_posterior = db.Column(db.String(50))
    ubres_pezones = db.Column(db.String(50))
    forma_testicular = db.Column(db.String(50))
    desplazamiento = db.Column(db.String(50))
    clase = db.Column(db.Float)
    impresion_general = db.Column(db.String(100))
    musculatura = db.Column(db.String(50))
    anchura = db.Column(db.String(50))
    costilla = db.Column(db.String(50))
    docilidad = db.Column(db.String(50))
    valoracion = db.Column(db.String(50))
    observaciones = db.Column(db.Text)
    premios = db.Column(db.Text)
    # EPDs
    epd_nac = db.Column(db.String(50))
    epd_dest = db.Column(db.String(50))
    epd_leche = db.Column(db.String(50))
    epd_18m = db.Column(db.String(50))
    epd_pa_v = db.Column(db.String(50))
    epd_ce = db.Column(db.String(50))
    epd_aob = db.Column(db.String(50))
    epd_egs = db.Column(db.String(50))
    epd_marb = db.Column(db.String(50))
    val_14m = db.Column(db.String(100))
    val_18m = db.Column(db.String(100))
    val_ternero = db.Column(db.String(100))
    val_adulto = db.Column(db.String(100))
    __table_args__ = (db.UniqueConstraint('rp', 'raza_id', name='uq_animal_rp_raza'),)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def fix_decimal(val):
    val = (val or '').strip()
    return val.replace(',', '.') if val else None

# RUTAS DE USUARIO

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('razas'))
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        if not username or not password:
            flash('Usuario y contraseña requeridos.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe.', 'warning')
            return render_template('register.html')
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registro exitoso, ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('razas'))
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Bienvenido.', 'success')
            return redirect(url_for('razas'))
        else:
            flash('Usuario o contraseña inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('login'))

# RUTAS DE APP

@app.route('/')
@login_required
def index():
    return redirect(url_for('razas'))

@app.route('/razas')
@login_required
def razas():
    razas = Raza.query.filter_by(user_id=current_user.id).order_by(Raza.nombre.asc()).all()
    return render_template('razas.html', razas=razas)

@app.route('/agregar_raza', methods=['GET', 'POST'])
@login_required
def agregar_raza():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip().capitalize()
        if not nombre:
            flash('Nombre no válido.', 'danger')
            return render_template('agregar_raza.html')
        if Raza.query.filter_by(nombre=nombre, user_id=current_user.id).first():
            flash('La raza ya existe.', 'warning')
            return render_template('agregar_raza.html')
        db.session.add(Raza(nombre=nombre, user_id=current_user.id))
        db.session.commit()
        flash('Raza agregada correctamente.', 'success')
        return redirect(url_for('razas'))
    return render_template('agregar_raza.html')

@app.route('/eliminar_raza/<int:raza_id>', methods=['POST'])
@login_required
def eliminar_raza(raza_id):
    raza = Raza.query.filter_by(id=raza_id, user_id=current_user.id).first_or_404()
    if raza.animales:
        flash('No se puede eliminar la raza porque tiene animales registrados.', 'danger')
    else:
        db.session.delete(raza)
        db.session.commit()
        flash('Raza eliminada.', 'success')
    return redirect(url_for('razas'))

@app.route('/raza/<int:raza_id>')
@login_required
def ver_raza(raza_id):
    raza = Raza.query.filter_by(id=raza_id, user_id=current_user.id).first_or_404()
    query = Animal.query.filter_by(raza_id=raza_id)
    sexo = request.args.get('sexo')
    if sexo:
        query = query.filter_by(sexo=sexo)

    def filtrar_rango(query, campo, numeric=False):
        min_val = request.args.get(f'{campo}_min')
        max_val = request.args.get(f'{campo}_max')
        if numeric:
            try:
                if min_val: min_val = float(min_val.replace(',', '.'))
                if max_val: max_val = float(max_val.replace(',', '.'))
            except Exception: min_val = max_val = None
        if min_val is not None and min_val != '':
            query = query.filter(getattr(Animal, campo) >= min_val)
        if max_val is not None and max_val != '':
            query = query.filter(getattr(Animal, campo) <= max_val)
        return query

    for campo in ['pezuñas', 'articulacion', 'clase']:
        query = filtrar_rango(query, campo, numeric=True)

    animales = query.all()
    orden = request.args.get('orden', 'asc')
    def rp_key(animal):
        rp = animal.rp
        if rp.isdigit():
            return (0, int(rp))
        else:
            return (1, rp)
    animales = sorted(animales, key=rp_key, reverse=(orden == 'desc'))

    return render_template('raza.html', raza=raza, animales=animales, total=len(animales), orden=orden)

@app.route('/raza/<int:raza_id>/registrar', methods=['GET', 'POST'])
@login_required
def registrar_animal(raza_id):
    raza = Raza.query.filter_by(id=raza_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        data = request.form
        def get_val(key, numeric=False):
            val = (data.get(key, '') or '').strip()
            if not val or val.lower() == 'none':
                return None
            if numeric:
                try:
                    return float(val.replace(',', '.'))
                except ValueError:
                    return None
            return val
        def get_date(key):
            val = data.get(key, '').strip()
            try: return datetime.strptime(val, '%Y-%m-%d') if val else None
            except ValueError: flash(f'Formato de fecha incorrecto para {key}.', 'danger'); return None
        rp = get_val('rp')
        if not rp:
            flash('El RP es obligatorio.', 'danger')
            return render_template('registrar.html', raza=raza)
        if Animal.query.filter_by(rp=rp, raza_id=raza.id).first():
            flash('Animal con ese RP ya registrado.', 'warning')
            return render_template('registrar.html', raza=raza)
        nuevo_animal = Animal(
            raza_id=raza.id,
            rp=rp,
            hba=get_val('hba'),
            nombre=get_val('nombre'),
            sexo=get_val('sexo'),
            fecha_nac=get_date('fecha_nac'),
            nacimiento=get_val('nacimiento'),
            color=get_val('color'),
            padre=get_val('padre'),
            madre=get_val('madre'),
            abuelo_paterno=get_val('abuelo_paterno'),
            abuelo_materno=get_val('abuelo_materno'),
            familia=get_val('familia'),
            f=get_val('f'),
            tamano=get_val('tamano'),
            pezuñas=get_val('pezuñas', numeric=True),
            articulacion=get_val('articulacion', numeric=True),
            ap_delanteros=get_val('ap_delanteros'),
            ap_traseros=get_val('ap_traseros'),
            curv_garrones=get_val('curv_garrones'),
            apert_posterior=get_val('apert_posterior'),
            ubres_pezones=get_val('ubres_pezones'),
            forma_testicular=get_val('forma_testicular'),
            desplazamiento=get_val('desplazamiento'),
            clase=get_val('clase', numeric=True),
            impresion_general=get_val('impresion_general'),
            musculatura=get_val('musculatura'),
            anchura=get_val('anchura'),
            costilla=get_val('costilla'),
            docilidad=get_val('docilidad'),
            valoracion=get_val('valoracion'),
            observaciones=get_val('observaciones'),
            premios=get_val('premios'),
            epd_nac=get_val('epd_nac'),
            epd_dest=get_val('epd_dest'),
            epd_leche=get_val('epd_leche'),
            epd_18m=get_val('epd_18m'),
            epd_pa_v=get_val('epd_pa_v'),
            epd_ce=get_val('epd_ce'),
            epd_aob=get_val('epd_aob'),
            epd_egs=get_val('epd_egs'),
            epd_marb=get_val('epd_marb'),
            val_14m=get_val('val_14m'),
            val_18m=get_val('val_18m'),
            val_ternero=get_val('val_ternero'),
            val_adulto=get_val('val_adulto')
        )
        db.session.add(nuevo_animal)
        db.session.commit()
        flash('Animal registrado con éxito.', 'success')
        return redirect(url_for('ver_raza', raza_id=raza.id))
    return render_template('registrar.html', raza=raza)

@app.route('/raza/<int:raza_id>/buscar', methods=['GET'])
@login_required
def buscar_animales(raza_id):
    raza = Raza.query.filter_by(id=raza_id, user_id=current_user.id).first_or_404()
    filtros = request.args
    query = Animal.query.filter(Animal.raza_id == raza_id)

    for campo in ['rp', 'nombre', 'padre', 'madre']:
        valor = filtros.get(campo, '').strip()
        if valor:
            query = query.filter(getattr(Animal, campo).ilike(f'%{valor}%'))
    sexo = filtros.get('sexo', '').strip()
    if sexo:
        query = query.filter(Animal.sexo == sexo)

    for campo in ['pezuñas', 'articulacion', 'clase']:
        min_v = filtros.get(f'{campo}_min', '').strip()
        max_v = filtros.get(f'{campo}_max', '').strip()
        if min_v:
            try:
                query = query.filter(getattr(Animal, campo) >= float(min_v.replace(',', '.')))
            except: pass
        if max_v:
            try:
                query = query.filter(getattr(Animal, campo) <= float(max_v.replace(',', '.')))
            except: pass

    fecha_min = filtros.get('fecha_nac_min', '').strip()
    fecha_max = filtros.get('fecha_nac_max', '').strip()
    if fecha_min:
        try:
            fecha_min_dt = datetime.strptime(fecha_min, '%Y-%m-%d')
            query = query.filter(Animal.fecha_nac >= fecha_min_dt)
        except: pass
    if fecha_max:
        try:
            fecha_max_dt = datetime.strptime(fecha_max, '%Y-%m-%d')
            query = query.filter(Animal.fecha_nac <= fecha_max_dt)
        except: pass

    animales = query.all()

    def rp_key(animal):
        rp = animal.rp
        if rp.isdigit():
            return (0, int(rp))
        else:
            return (1, rp)

    orden = filtros.get('orden', 'asc')
    animales = sorted(animales, key=rp_key, reverse=(orden == 'desc'))

    cantidad = len(animales)
    return render_template('buscar.html', animales=animales, cantidad=cantidad, raza=raza)

@app.route('/animal/<int:id>')
@login_required
def ficha_animal(id):
    animal = Animal.query.get_or_404(id)
    if animal.raza.usuario.id != current_user.id:
        flash('No tienes permiso para ver este animal.', 'danger')
        return redirect(url_for('razas'))
    # Producción: hijos donde padre o madre coinciden con el NOMBRE del animal actual
    hijos = Animal.query.filter(
        (Animal.padre == animal.nombre) | (Animal.madre == animal.nombre)
    ).all()
    return render_template('ficha.html', animal=animal, hijos=hijos)

@app.route('/animal/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_animal(id):
    animal = Animal.query.get_or_404(id)
    if animal.raza.usuario.id != current_user.id:
        flash('No tienes permiso para editar este animal.', 'danger')
        return redirect(url_for('razas'))
    raza = animal.raza
    if request.method == 'POST':
        data = request.form
        def get_val(key, numeric=False):
            val = (data.get(key, '') or '').strip()
            if not val or val.lower() == 'none':
                return None
            if numeric:
                try:
                    return float(val.replace(',', '.'))
                except ValueError:
                    return None
            return val
        def get_date(key):
            val = data.get(key, '').strip()
            try: return datetime.strptime(val, '%Y-%m-%d') if val else None
            except: flash(f'Formato de fecha incorrecto para {key}.', 'danger'); return None
        animal.rp = get_val('rp')
        animal.hba = get_val('hba')
        animal.nombre = get_val('nombre')
        animal.sexo = get_val('sexo')
        animal.fecha_nac = get_date('fecha_nac')
        animal.nacimiento = get_val('nacimiento')
        animal.color = get_val('color')
        animal.padre = get_val('padre')
        animal.madre = get_val('madre')
        animal.abuelo_paterno = get_val('abuelo_paterno')
        animal.abuelo_materno = get_val('abuelo_materno')
        animal.familia = get_val('familia')
        animal.f = get_val('f')
        animal.tamano = get_val('tamano')
        animal.pezuñas = get_val('pezuñas', numeric=True)
        animal.articulacion = get_val('articulacion', numeric=True)
        animal.ap_delanteros = get_val('ap_delanteros')
        animal.ap_traseros = get_val('ap_traseros')
        animal.curv_garrones = get_val('curv_garrones')
        animal.apert_posterior = get_val('apert_posterior')
        animal.ubres_pezones = get_val('ubres_pezones')
        animal.forma_testicular = get_val('forma_testicular')
        animal.desplazamiento = get_val('desplazamiento')
        animal.clase = get_val('clase', numeric=True)
        animal.impresion_general = get_val('impresion_general')
        animal.musculatura = get_val('musculatura')
        animal.anchura = get_val('anchura')
        animal.costilla = get_val('costilla')
        animal.docilidad = get_val('docilidad')
        animal.valoracion = get_val('valoracion')
        animal.observaciones = get_val('observaciones')
        animal.premios = get_val('premios')
        animal.epd_nac = get_val('epd_nac')
        animal.epd_dest = get_val('epd_dest')
        animal.epd_leche = get_val('epd_leche')
        animal.epd_18m = get_val('epd_18m')
        animal.epd_pa_v = get_val('epd_pa_v')
        animal.epd_ce = get_val('epd_ce')
        animal.epd_aob = get_val('epd_aob')
        animal.epd_egs = get_val('epd_egs')
        animal.epd_marb = get_val('epd_marb')
        animal.val_14m = get_val('val_14m')
        animal.val_18m = get_val('val_18m')
        animal.val_ternero = get_val('val_ternero')
        animal.val_adulto = get_val('val_adulto')
        db.session.commit()
        flash('Animal actualizado correctamente.', 'success')
        return redirect(url_for('ficha_animal', id=animal.id))
    return render_template('editar.html', animal=animal, raza=raza)

@app.route('/animal/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_animal(id):
    animal = Animal.query.get_or_404(id)
    if animal.raza.usuario.id != current_user.id:
        flash('No tienes permiso para eliminar este animal.', 'danger')
        return redirect(url_for('razas'))
    raza_id = animal.raza_id
    db.session.delete(animal)
    db.session.commit()
    flash('Animal eliminado correctamente.', 'success')
    return redirect(url_for('ver_raza', raza_id=raza_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

