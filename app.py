import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from databasemanager import DatabaseManager
from forms import LoginForm
from navigation import navigation as nav_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = "adsajdaskj"
database = DatabaseManager("db_prova.db")

@app.route('/login', methods=['POST'])
def login():
    login_form = LoginForm()
    username = request.form['username']
    password = request.form['password']
    validation = database.check_access(username, password)
    if validation:
        session['logged_in'] = True  # Imposta la sessione per l'utente autenticato
        flash('Accesso effettuato correttamente')
        return redirect(url_for('access.homepage'))  # Reindirizza alla homepage
    else:
        flash('Nome utente o password non validi')
        return render_template('index.html', form=login_form)

@app.route('/prodotti')
def prodotti():
    if not session.get('logged_in'):
        flash('Devi effettuare il login per accedere a questa pagina.')
        return redirect(url_for('index'))
    return render_template('prodotti.html', prodotti=database.get_prodotti())

# Route per visualizzare un prodotto
@app.route('/visualizza_prodotto/<barcode>', methods=['GET'])
def visualizza_prodotto(barcode):
    prodotto = database.get_prodotto(barcode)
    return render_template('visualizza_prodotto.html', prodotto=prodotto)

@app.route('/check_aggiunta_prodotto', methods=['POST'])
def check_aggiunta_prodotto():
    return jsonify("ciao")

@app.route('/elimina_prodotto', methods=['POST'])
def elimina_prodotto():
    barcode = request.form['barcode']
    conn = database.create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Prodotto WHERE Barcode = ?", (barcode,))
    conn.commit()
    conn.close()
    return render_template('prodotti.html', prodotti=database.get_prodotti())

# Route per modificare un prodotto
@app.route('/modifica_prodotto', methods=['POST'])
def modifica_prodotto():
    barcode = request.form['barcode']
    return jsonify(database.get_prodotto(barcode))

@app.route('/view_modifica_prodotto', methods=['GET'])
def view_modifica_prodotto():
    prodotto = request.args.get('prodotto')
    return prodotto

@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Rimuove l'utente dalla sessione
    flash('Sei stato disconnesso.')
    return redirect(url_for('index'))  # Reindirizza alla pagina di login

@app.route('/add_user', methods=['POST'])
def add_user():
    email = request.form['email']
    token = request.form['adminToken']
    if token != database.special_token:
        flash('Token non valido')
        return redirect(url_for("access.view_add_user"))
    check_if_user_can_added = database.check_if_user_can_added(email)
    if not check_if_user_can_added:
        flash('Email già esistente')
        return redirect(url_for("access.view_add_user"))
    else:
        database.insert_user(email)
        flash('Utente inserito correttamente')
        return redirect(url_for("access.view_add_user"))

@app.route('/register_user', methods=['POST'])
def register():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    res = database.update_user(email, username, password)
    if res:
        flash(res)
        return redirect(url_for("access.view_register"))
    else:
        flash("utente registrato correttamente")
        return redirect(url_for("access.view_register"))

if __name__ == '__main__':
    app.register_blueprint(nav_blueprint)
    app.run(debug=True)
