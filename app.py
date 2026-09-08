"""
Product Hypothesis Assistant - Web Application
Flask веб-приложение с графическим интерфейсом
"""

from flask import Flask, render_template, request, jsonify
from product_hypothesis_assistant import (
    HypothesisManager, Evidence, EvidenceType, RealWorldOutcome
)
import json
import uuid

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Глобальный менеджер гипотез
manager = HypothesisManager()

# Глобальная переменная для текущей гипотезы
current_hypothesis_id = None


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/api/create-hypothesis', methods=['POST'])
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
            expected_outcome=data.get('expected_outcome', '')
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
def get_hypothesis(hypothesis_id):
    """Получить гипотезу"""
    hypothesis = manager.get_hypothesis(hypothesis_id)
    
    if not hypothesis:
        return jsonify({'success': False, 'error': 'Гипотеза не найдена'}), 404
    
    return jsonify({
        'success': True,
        'hypothesis': hypothesis.to_dict()
    })


@app.route('/api/add-evidence', methods=['POST'])
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
        
        success = manager.add_evidence(hypothesis_id, evidence)
        
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
def validate_hypothesis(hypothesis_id):
    """Валидировать гипотезу и получить score"""
    try:
        success, score = manager.validate_hypothesis(hypothesis_id)
        
        if not success:
            return jsonify({'success': False, 'error': 'Ошибка валидации'}), 400
        
        return jsonify({
            'success': True,
            'score': score.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/research-sources/<hypothesis_id>', methods=['GET'])
def get_research_sources(hypothesis_id):
    """Получить список найденных исследований из открытых источников"""
    try:
        hypothesis = manager.get_hypothesis(hypothesis_id)
        
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
        
        success = manager.record_outcome(hypothesis_id, outcome)
        
        if not success:
            return jsonify({'success': False, 'error': 'Ошибка записи'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Исход записан'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/correlation-analysis', methods=['GET'])
def correlation_analysis():
    """Анализ корреляции"""
    try:
        analysis = manager.get_correlation_analysis()
        return jsonify({'success': True, 'analysis': analysis})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/list-hypotheses', methods=['GET'])
def list_hypotheses():
    """Список всех гипотез"""
    try:
        hypotheses = manager.list_hypotheses()
        data = [h.to_dict() for h in hypotheses]
        return jsonify({'success': True, 'hypotheses': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/export-hypothesis/<hypothesis_id>', methods=['GET'])
def export_hypothesis(hypothesis_id):
    """Экспортировать гипотезу в JSON"""
    try:
        data = manager.export_hypothesis(hypothesis_id)
        
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


if __name__ == '__main__':
    app.run(debug=False, host='localhost', port=5000, threaded=True)
