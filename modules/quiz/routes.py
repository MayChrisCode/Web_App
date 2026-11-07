import json
import os
import random
from flask import Blueprint, render_template, jsonify, request

# Blueprint definieren: Name, Import-Name, eigener Template-Ordner
quiz_bp = Blueprint('quiz', __name__, template_folder='templates')

DATA_FILE = os.path.join('data', 'quiz_questions.json')

def load_questions():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_questions(questions):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

@quiz_bp.route('/')
def index():
    """Lädt die Quiz-Webseite."""
    return render_template('quiz.html')

@quiz_bp.route('/api/next', methods=['GET'])
def next_question():
    """Wählt eine Frage aus: Niedriger Streak = hohe Wahrscheinlichkeit."""
    questions = load_questions()
    
    # Gewichtungs-Tabelle nach Streak-Stufe (0 bis 4)
    # Streak 0 -> Gewicht 16 | Streak 4 (Volle Blume) -> Gewicht 1
    weight_map = {0: 16, 1: 8, 2: 4, 3: 2, 4: 1}
    weights = [weight_map.get(q.get('streak', 0), 1) for q in questions]
    
    # Ziehe eine Frage basierend auf den Gewichten
    chosen = random.choices(questions, weights=weights, k=1)[0]
    
    # Gesamtstatistik für den Garten berechnen
    total_Count = len(questions)
    full_flowers = sum(1 for q in questions if q.get('streak', 0) >= 4)
    
    return jsonify({
        "id": chosen["id"],
        "question": chosen["question"],
        "options": chosen["options"],
        "streak": chosen.get("streak", 0),
        "stats": {"total": total_Count, "mastered": full_flowers}
    })

@quiz_bp.route('/api/answer', methods=['POST'])
def check_answer():
    """Prüft die Antwort und lässt die Blume wachsen oder schrumpfen."""
    data = request.json
    q_id = data.get("id")
    selected = data.get("selected")
    
    questions = load_questions()
    for q in questions:
        if q["id"] == q_id:
            is_correct = (q["answer"] == selected)
            if is_correct:
                # Blume wächst um 1 (maximal bis Stufe 4)
                q["streak"] = min(4, q.get("streak", 0) + 1)
            else:
                # Bei Fehler fällt die Pflanze um 1 Stufe zurück (oder auf 0, je nach Wunsch)
                q["streak"] = max(0, q.get("streak", 0) - 1)
            
            save_questions(questions)
            return jsonify({
                "correct": is_correct,
                "correct_answer": q["answer"],
                "new_streak": q["streak"]
            })
            
    return jsonify({"error": "Frage nicht gefunden"}), 404