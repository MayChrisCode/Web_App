from flask import Flask, redirect, url_for
from modules.quiz.routes import quiz_bp

app = Flask(__name__)

# Modul 1 registrieren unter der URL /quiz
app.register_blueprint(quiz_bp, url_prefix='/quiz')

@app.route('/')
def home():
    # Startseite leitet direkt zum ersten Modul weiter (später kommt hier dein Dashboard hin)
    return redirect(url_for('quiz.index'))

if __name__ == '__main__':
    # host='0.0.0.0' erlaubt später auch den Zugriff im Heimnetzwerk/Docker
    app.run(host='0.0.0.0', port=5000, debug=True)