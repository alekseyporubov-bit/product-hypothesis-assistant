"""
Product Hypothesis Assistant - Web Application
Flask веб-приложение с графическим интерфейсом
"""

from dotenv import load_dotenv

# Загружаем переменные окружения из .env (если файл существует).
# Важно: вызывать до чтения GOOGLE_CLIENT_ID / SESSION_SECRET / DATABASE_URL.
load_dotenv()

from flask import Flask, render_template, request, jsonify, session
from functools import wraps
from product_hypothesis_assistant import (
    HypothesisManager, Evidence, EvidenceType, RealWorldOutcome
)
from auth import UserManager, verify_google_id_token
import json
import uuid
import os

app = Flask(__name__)
app.json.ensure_ascii = False
# Секрет для подписи Flask-сессии (задайте в окружении, напр. SESSION_SECRET)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-change-me")

# Глобальный менеджер гипотез
manager = HypothesisManager()

# Глобальный менеджер пользователей (Google OAuth + логин/пароль)
user_manager = UserManager()
DEFAULT_GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip() or None

# Глобальная переменная для текущей гипотезы
current_hypothesis_id = None


def login_required(f):
    """Пропускает только авторизованных пользователей (иначе 401)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"success": False, "error": "Требуется авторизация"}), 401
        return f(*args, **kwargs)
    return decorated


def _establish_session(user, is_first: bool) -> None:
    """Записывает пользователя в сессию и привязывает легаси-гипотезы первому."""
    if is_first:
        claimed = manager.claim_orphaned_hypotheses(user.id)
        if claimed:
            print(f"♻️ Привязано «сиротских» гипотез к первому пользователю: {claimed}")
    # Очищаем сессию перед входом (защита от session fixation).
    session.clear()
    session["user_id"] = user.id


@app.route('/')
def index():
    """Главная страница"""
    return render_template(
        'index.html',
        google_client_id=os.environ.get("GOOGLE_CLIENT_ID", "").strip(),
    )


# ============================================================================
# Аутентификация (Google + логин/пароль)
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    """Обменивает Google ID token на сессию пользователя (JIT-создание учётки)."""
    data = request.get_json(silent=True) or {}
    id_token = (data.get('credential') or data.get('id_token') or '').strip()
    if not id_token:
        return jsonify({"success": False, "error": "Отсутствует Google ID token"}), 400

    try:
        profile = verify_google_id_token(id_token, DEFAULT_GOOGLE_CLIENT_ID)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 401

    user, _created, is_first = user_manager.ensure_user(
        google_sub=profile.get("sub", ""),
        email=profile.get("email", ""),
        name=profile.get("name", ""),
        avatar_url=profile.get("picture", ""),
    )

    _establish_session(user, is_first)
    return jsonify({
        "success": True,
        "user": user.to_dict(),
        "is_first_user": is_first,
    })


@app.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    """Создаёт нового пользователя по логину и паролю."""
    data = request.get_json(silent=True) or {}
    login = (data.get('login') or data.get('username') or '').strip()
    password = data.get('password') or ''
    if not login or not password:
        return jsonify({"success": False, "error": "Укажите логин и пароль"}), 400

    try:
        user, _created, is_first = user_manager.register_user(login, password)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    _establish_session(user, is_first)
    return jsonify({
        "success": True,
        "user": user.to_dict(),
        "is_first_user": is_first,
    })


@app.route('/api/auth/password-login', methods=['POST'])
def api_auth_password_login():
    """Вход по логину и паролю."""
    data = request.get_json(silent=True) or {}
    login = (data.get('login') or data.get('username') or '').strip()
    password = data.get('password') or ''
    if not login or not password:
        return jsonify({"success": False, "error": "Укажите логин и пароль"}), 400

    user = user_manager.authenticate_user(login, password)
    if user is None:
        return jsonify({"success": False, "error": "Неверный логин или пароль"}), 401

    _establish_session(user, False)
    return jsonify({
        "success": True,
        "user": user.to_dict(),
        "is_first_user": False,
    })


@app.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    session.pop("user_id", None)
    return jsonify({"success": True})


@app.route('/api/auth/status', methods=['GET'])
def api_auth_status():
    if not session.get("user_id"):
        return jsonify({"success": True, "authenticated": False, "user": None})
    user = user_manager.get_user(session["user_id"])
    if user is None:
        session.pop("user_id", None)
        return jsonify({"success": True, "authenticated": False, "user": None})
    return jsonify({"success": True, "authenticated": True, "user": user.to_dict()})


@app.route('/api/create-hypothesis', methods=['POST'])
@login_required
def create_hypothesis():
    """Создать новую гипотезу"""
    global current_hypothesis_id
    
    data = request.json
    
    try:
        hypothesis = manager.create_hypothesis(
            title=data.get('title', ''),
            description=data.get('description', ''),
            problem_statement=data.get('problem_statement', ''),
            target_users=data.get('target_users', ''),
            expected_outcome=data.get('expected_outcome', ''),
            user_id=session.get("user_id", "")
        )
        
        current_hypothesis_id = hypothesis.id
        
        return jsonify({
            'success': True,
            'hypothesis_id': hypothesis.id,
            'message': f'Гипотеза "{hypothesis.title}" создана'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/get-hypothesis/<hypothesis_id>', methods=['GET'])
@login_required
def get_hypothesis(hypothesis_id):
    """Получить гипотезу"""
    hypothesis = manager.get_hypothesis(hypothesis_id, session.get("user_id"))
    
    if not hypothesis:
        return jsonify({'success': False, 'error': 'Гипотеза не найдена'}), 404
    
    return jsonify({
        'success': True,
        'hypothesis': hypothesis.to_dict()
    })


@app.route('/api/add-evidence', methods=['POST'])
@login_required
def add_evidence():
    """Добавить доказательство"""
    data = request.json
    hypothesis_id = data.get('hypothesis_id')
    
    try:
        evidence = Evidence(
            evidence_type=EvidenceType[data.get('evidence_type', 'MARKET_RESEARCH')],
            title=data.get('title', ''),
            description=data.get('description', ''),
            source=data.get('source', ''),
            confidence=float(data.get('confidence', 0.5)),
            supports=data.get('supports', True)
        )
        
        success = manager.add_evidence(hypothesis_id, evidence, session.get("user_id"))
        
        if not success:
            return jsonify({'success': False, 'error': 'Ошибка добавления'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Доказательство добавлено',
            'evidence_id': evidence.id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/validate-hypothesis/<hypothesis_id>', methods=['POST'])
@login_required
def validate_hypothesis(hypothesis_id):
    """Валидировать гипотезу и получить score"""
    try:
        success, score = manager.validate_hypothesis(hypothesis_id, session.get("user_id"))
        
        if not success:
            return jsonify({'success': False, 'error': 'Ошибка валидации'}), 400
        
        return jsonify({
            'success': True,
            'score': score.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/research-sources/<hypothesis_id>', methods=['GET'])
@login_required
def get_research_sources(hypothesis_id):
    """Получить список найденных исследований из открытых источников"""
    try:
        hypothesis = manager.get_hypothesis(hypothesis_id, session.get("user_id"))
        
        if not hypothesis:
            return jsonify({'success': False, 'error': 'Гипотеза не найдена'}), 404
        
        if not hypothesis.score or not hypothesis.score.research_sources:
            return jsonify({
                'success': True,
                'research_sources': [],
                'message': 'Исследования не найдены. Сначала валидируйте гипотезу.'
            })
        
        return jsonify({
            'success': True,
            'hypothesis_id': hypothesis_id,
            'hypothesis_title': hypothesis.title,
            'problem_statement': hypothesis.problem_statement,
            'target_users': hypothesis.target_users,
            'research_count': len(hypothesis.score.research_sources),
            'research_sources': hypothesis.score.research_sources,
            'message': f'Найдено {len(hypothesis.score.research_sources)} исследований'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/record-outcome', methods=['POST'])
@login_required
def record_outcome():
    """Записать исход фичи"""
    data = request.json
    hypothesis_id = data.get('hypothesis_id')
    
    try:
        outcome = RealWorldOutcome(
            was_successful=data.get('was_successful', False),
            actual_impact=data.get('actual_impact', ''),
            lessons_learned=data.get('lessons_learned', '')
        )
        
        success = manager.record_outcome(hypothesis_id, outcome, session.get("user_id"))
        
        if not success:
            return jsonify({'success': False, 'error': 'Ошибка записи'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Исход записан'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/correlation-analysis', methods=['GET'])
@login_required
def correlation_analysis():
    """Анализ корреляции"""
    try:
        analysis = manager.get_correlation_analysis(session.get("user_id"))
        return jsonify({'success': True, 'analysis': analysis})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/list-hypotheses', methods=['GET'])
@login_required
def list_hypotheses():
    """Список всех гипотез"""
    try:
        hypotheses = manager.list_hypotheses(session.get("user_id"))
        data = [h.to_dict() for h in hypotheses]
        return jsonify({'success': True, 'hypotheses': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/export-hypothesis/<hypothesis_id>', methods=['GET'])
@login_required
def export_hypothesis(hypothesis_id):
    """Экспортировать гипотезу в JSON"""
    try:
        data = manager.export_hypothesis(hypothesis_id, session.get("user_id"))
        
        if not data:
            return jsonify({'success': False, 'error': 'Гипотеза не найдена'}), 404
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/evidence-types', methods=['GET'])
def get_evidence_types():
    """Получить список типов доказательств"""
    types = [
        {'value': 'MARKET_RESEARCH', 'label': 'Исследование рынка'},
        {'value': 'USER_FEEDBACK', 'label': 'Обратная связь пользователей'},
        {'value': 'COMPETITOR_ANALYSIS', 'label': 'Анализ конкурентов'},
        {'value': 'ANALYTICS', 'label': 'Данные аналитики'},
        {'value': 'EXPERT_OPINION', 'label': 'Мнение эксперта'},
        {'value': 'CASE_STUDY', 'label': 'Case study'},
    ]
    return jsonify({'success': True, 'types': types})


# ============================================================================
# 🔥 НОВАЯ ФУНКЦИОНАЛЬНАЯ ВОЗМОЖНОСТЬ: Автоматический поиск исследований
# ============================================================================

@app.route('/api/scan-research/<hypothesis_id>', methods=['POST'])
@login_required
def scan_research(hypothesis_id):
    """
    🔥 НОВАЯ ФУНКЦИОНАЛЬНАЯ ВОЗМОЖНОСТЬ:
    Автоматически ищет исследования в открытых источниках по теме гипотезы.
    Результаты сохраняются в auto_research_sources (максимум 5).
    """
    try:
        result = manager.scan_auto_research(hypothesis_id, session.get("user_id"))

        if not result.get('success'):
            return jsonify(result), 404

        return jsonify({
            'success': True,
            'hypothesis_id': result['hypothesis_id'],
            'hypothesis_title': result['hypothesis_title'],
            'research_count': result['research_count'],
            'research_sources': result['research_sources'],
            'average_relevance': result['average_relevance'],
            'message': result['message']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=False, host='localhost', port=5000, threaded=True)
