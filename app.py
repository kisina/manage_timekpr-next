from flask import Flask, render_template, request, redirect, url_for
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
    # Traitez la valeur de selected_user ici, par exemple, en l'affichant ou en l'utilisant dans une commande.
    print("Utilisateur sélectionné:", selected_user)

    command = f"sudo timekpra --settimeleft '{selected_user}' '+' 30"
    execute_command2(command)

    return redirect(url_for('index'))  # Redirige vers la page principale après traitement


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)