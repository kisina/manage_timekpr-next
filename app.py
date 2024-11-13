from flask import Flask, render_template, request, redirect, url_for, jsonify
import subprocess

app = Flask(__name__)

def execute_command2(command):
    try:
        # Exécute la commande en utilisant subprocess
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        
    except subprocess.CalledProcessError as e:
        # En cas d'erreur, on retourne l'erreur
        result = f"Erreur lors de l'exécution de la commande : {e.output}"
    return result

def get_timeleft(user):
    time_left = execute_command2(f"sudo timekpra --userinfo {user}")
    userinfo = time_left.split("\n")[1:-1]
    dictionnaire = {item.split(":")[0]: item.split(":")[1] for item in userinfo}
    time_left = (dictionnaire['TIME_LEFT_DAY'])
    return time_left

def get_users():
    users = execute_command2("sudo timekpra --userlist")
    users = users.split("\n")
    users = users[1:-1]

    list_users = {}
    for user in users:
        timeleft = get_timeleft(user)
        list_users[user] = timeleft

    return list_users

# Route principale qui affiche la page avec le bouton
@app.route('/', methods=['GET'])
def index():
    users = get_users()

    result = ""
    for user, timeleft in users.items():
        result += f"Il reste {formater_duree(int(timeleft))} à {user} \r\n"
    return render_template('index.html', timeleft=result, users=[user for user in users])

def formater_duree(secondes):
    heures = secondes // 3600
    minutes = (secondes % 3600) // 60
    secondes_restantes = secondes % 60
    
    resultat = f"{heures}h {minutes} minutes et {secondes_restantes} secondes"
    return resultat


# Route pour ajouter du temps
@app.route('/add_time', methods=['POST'])
def add_time():
    selected_user = request.form.get('selected_user')
    selected_mode = request.form.get('selected_mode')
    selected_time = request.form.get('selected_time')
    selected_time = 60 * int(selected_time) # Conversion en secondes
    # Traitez la valeur de selected_user ici, par exemple, en l'affichant ou en l'utilisant dans une commande.
    print("Utilisateur sélectionné:", selected_user)

    command = f"sudo timekpra --settimeleft '{selected_user}' '{selected_mode}' {selected_time}"
    execute_command2(command)

    return redirect(url_for('index'))  # Redirige vers la page principale après traitement


@app.route('/add_time_jeedom', methods=['GET'])
def add_time_jeedom():
    # Récupération des paramètres
    selected_user = request.args.get('selected_user')
    selected_mode = request.args.get('selected_mode')
    selected_time = request.args.get('selected_time')
    selected_time = 60 * int(selected_time) # Conversion en secondes

    selected_mode = '+' if selected_mode == 'ajout' else '-'

    # Vérification que tous les paramètres sont bien présents
    if not all([selected_user, selected_mode, selected_time]):
        return jsonify({"error": "Tous les paramètres sont requis"}), 400

    # Action avec les paramètres - ici on affiche simplement les paramètres
    command = f"sudo timekpra --settimeleft '{selected_user}' '{selected_mode}' {selected_time}"
    execute_command2(command)
    # Tu peux remplacer ce bloc par l'action que tu souhaites
    result = {
        "selected_user": selected_user,
        "selected_mode": selected_mode,
        "selected_time": selected_time,
        "message": f"Action effectuée avec succès pour l'utilisateur {selected_user} en mode {selected_mode} à {selected_time}."
    }

    # Retourner le résultat en JSON
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


# Exemple test API jeedom: http://127.0.0.1:5000/add_time_jeedom?selected_user=test_timekpr&selected_mode=ajout&selected_time=11