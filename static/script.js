/* ============================================================================
   Product Hypothesis Assistant - JavaScript
   ============================================================================ */

let currentHypothesisId = null;
let evidenceTypes = [];

// ============================================================================
// Инициализация
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    // Загружаем типы доказательств
    await loadEvidenceTypes();
    
    // Загружаем список гипотез
    await loadHypotheses();
    
    // Настраиваем обработчики форм
    setupFormHandlers();
    
    // Показываем welcome страницу
    showSection('welcome');
});

// ============================================================================
// API Запросы
// ============================================================================

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (!response.ok && result.error) {
            showNotification(result.error, 'error');
            return null;
        }
        
        return result;
    } catch (error) {
        showNotification(`Ошибка: ${error.message}`, 'error');
        return null;
    }
}

async function loadEvidenceTypes() {
    const result = await apiCall('/api/evidence-types');
    if (result && result.success) {
        evidenceTypes = result.types;
        populateEvidenceTypeSelect();
    }
}

async function loadHypotheses() {
    const result = await apiCall('/api/list-hypotheses');
    if (result && result.success) {
        displayHypotheses(result.hypotheses);
    }
}

// ============================================================================
// UI Функции
// ============================================================================

function showSection(sectionId) {
    // Скрываем все секции
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Показываем нужную секцию
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 4000);
}

function populateEvidenceTypeSelect() {
    const select = document.getElementById('evidence-type');
    select.innerHTML = '';
    
    evidenceTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type.value;
        option.textContent = type.label;
        select.appendChild(option);
    });
}

function displayHypotheses(hypotheses) {
    const list = document.getElementById('hypotheses-list');
    list.innerHTML = '';
    
    if (hypotheses.length === 0) {
        list.innerHTML = '<p style="color: #999; font-size: 13px;">Нет гипотез</p>';
        return;
    }
    
    hypotheses.forEach(hyp => {
        const item = document.createElement('div');
        item.className = `hypothesis-item ${hyp.id === currentHypothesisId ? 'active' : ''}`;
        item.setAttribute('data-hypothesis-id', hyp.id);
        item.innerHTML = `
            <span class="hypothesis-item-title">${hyp.title}</span>
            <span class="hypothesis-item-status">${getStatusLabel(hyp.status)}</span>
        `;
        item.onclick = () => selectHypothesis(hyp.id);
        list.appendChild(item);
    });
}

function getStatusLabel(status) {
    const labels = {
        'draft': '📝 Черновик',
        'in_research': '🔍 На исследовании',
        'validated': '✓ Валидирована',
        'rejected': '✗ Отклонена',
        'in_development': '⚙️ На разработке',
        'released': '🚀 В продакшене',
        'completed': '✅ Завершена'
    };
    return labels[status] || status;
}

function getStatusClass(status) {
    const classes = {
        'draft': 'draft',
        'validated': 'validated',
        'rejected': 'rejected',
        'in_research': 'in-research'
    };
    return classes[status] || '';
}

// ============================================================================
// Форма создания гипотезы
// ============================================================================

async function createHypothesis(event) {
    event.preventDefault();
    
    const data = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        problem_statement: document.getElementById('problem_statement').value,
        target_users: document.getElementById('target_users').value,
        expected_outcome: document.getElementById('expected_outcome').value
    };
    
    const result = await apiCall('/api/create-hypothesis', 'POST', data);
    
    if (result && result.success) {
        showNotification(result.message, 'success');
        document.getElementById('create-form').reset();
        
        currentHypothesisId = result.hypothesis_id;
        
        // Перезагружаем список и показываем детали
        await loadHypotheses();
        await displayHypothesisDetail(currentHypothesisId);
    }
}

// ============================================================================
// Просмотр деталей гипотезы
// ============================================================================

async function selectHypothesis(hypothesisId) {
    currentHypothesisId = hypothesisId;
    
    // Обновляем активный элемент в списке
    document.querySelectorAll('.hypothesis-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const activeItem = document.querySelector(`[data-hypothesis-id="${hypothesisId}"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
    
    await displayHypothesisDetail(hypothesisId);
}

async function displayHypothesisDetail(hypothesisId) {
    const result = await apiCall(`/api/get-hypothesis/${hypothesisId}`);
    
    if (!result || !result.success) {
        showNotification('Ошибка загрузки гипотезы', 'error');
        return;
    }
    
    const hyp = result.hypothesis;
    
    // Заполняем основную информацию
    document.getElementById('hyp-title').textContent = hyp.title;
    document.getElementById('hyp-status').textContent = getStatusLabel(hyp.status);
    document.getElementById('hyp-status').className = `status-badge ${getStatusClass(hyp.status)}`;
    
    document.getElementById('hyp-description').textContent = hyp.description;
    document.getElementById('hyp-problem').textContent = hyp.problem_statement;
    document.getElementById('hyp-users').textContent = hyp.target_users;
    document.getElementById('hyp-outcome').textContent = hyp.expected_outcome;
    
    // Показываем доказательства
    displayEvidenceList(hyp.evidence);
    
    // Если есть score, показываем его
    if (hyp.score) {
        displayScore(hyp.score);
    } else {
        document.getElementById('score-section').classList.add('hidden');
    }
    
    showSection('hypothesis-detail');
}

// ============================================================================
// Доказательства
// ============================================================================

function displayEvidenceList(evidences) {
    const list = document.getElementById('evidence-list');
    list.innerHTML = '';
    
    if (evidences.length === 0) {
        list.innerHTML = '<p style="color: #999; padding: 20px;">Доказательства не добавлены</p>';
        return;
    }
    
    evidences.forEach(ev => {
        const item = document.createElement('div');
        item.className = 'evidence-item';
        
        const badgeClass = ev.supports ? 'supports' : 'contradicts';
        const badgeText = ev.supports ? '✓ Поддерживает' : '✗ Опровергает';
        
        item.innerHTML = `
            <div class="evidence-info">
                <div class="evidence-title">${ev.title}</div>
                <span class="evidence-type">${getEvidenceTypeLabel(ev.evidence_type)}</span>
                <div class="evidence-description">${ev.description}</div>
                <small style="color: #999;">Источник: ${ev.source} | Уверенность: ${(ev.confidence * 100).toFixed(0)}%</small>
            </div>
            <span class="evidence-badge ${badgeClass}">${badgeText}</span>
        `;
        
        list.appendChild(item);
    });
}

function getEvidenceTypeLabel(type) {
    const found = evidenceTypes.find(t => t.value === type);
    return found ? found.label : type;
}

async function addEvidence(event) {
    event.preventDefault();
    
    if (!currentHypothesisId) {
        showNotification('Сначала создайте гипотезу', 'error');
        return;
    }
    
    const data = {
        hypothesis_id: currentHypothesisId,
        evidence_type: document.getElementById('evidence-type').value,
        title: document.getElementById('evidence-title').value,
        description: document.getElementById('evidence-description').value,
        source: document.getElementById('evidence-source').value,
        confidence: parseFloat(document.getElementById('evidence-confidence').value),
        supports: document.getElementById('evidence-supports').value === 'true'
    };
    
    const result = await apiCall('/api/add-evidence', 'POST', data);
    
    if (result && result.success) {
        showNotification('Доказательство добавлено', 'success');
        document.getElementById('evidence-form').reset();
        
        // Перезагружаем гипотезу
        await displayHypothesisDetail(currentHypothesisId);
    }
}

// ============================================================================
// Валидация и скоринг
// ============================================================================

async function validateHypothesis() {
    if (!currentHypothesisId) {
        showNotification('Гипотеза не выбрана', 'error');
        return;
    }
    
    const result = await apiCall(`/api/validate-hypothesis/${currentHypothesisId}`, 'POST');
    
    if (result && result.success) {
        displayScore(result.score);
        showNotification('Валидация завершена', 'success');
        
        // Перезагружаем гипотезу для обновления статуса
        await loadHypotheses();
    }
}

function displayScore(score) {
    const section = document.getElementById('score-section');
    section.classList.remove('hidden');
    
    // Основной score
    document.getElementById('score-value').textContent = Math.round(score.overall_score);
    document.getElementById('score-recommendation').textContent = getRecommendationText(score.recommendation);
    document.getElementById('score-recommendation').className = `recommendation ${score.recommendation}`;
    document.getElementById('score-confidence').textContent = score.confidence_level.toUpperCase();
    document.getElementById('score-completeness').textContent = Math.round(score.data_completeness * 100);
    
    // Счётчики
    document.getElementById('supporting-count').textContent = score.supporting_evidence_count;
    document.getElementById('contradicting-count').textContent = score.contradicting_evidence_count;
    
    // Разложение по факторам
    const breakdown = document.getElementById('score-breakdown');
    breakdown.innerHTML = '';
    
    score.breakdown.forEach(item => {
        const div = document.createElement('div');
        div.className = 'breakdown-item';
        div.innerHTML = `
            <div class="breakdown-item-factor">${item.factor}</div>
            <div class="breakdown-item-score">${item.score.toFixed(1)}/10</div>
            <div class="breakdown-item-rationale">${item.rationale}</div>
        `;
        breakdown.appendChild(div);
    });
}

function getRecommendationText(rec) {
    const texts = {
        'proceed': '✓ ИДТИ В РАЗРАБОТКУ',
        'investigate': '⚠️ ТРЕБУЕТСЯ ДОИССЛЕДОВАНИЕ',
        'reject': '✗ ОТКЛОНИТЬ'
    };
    return texts[rec] || rec;
}

// ============================================================================
// Запись исхода
// ============================================================================

function showOutcomeForm() {
    if (!currentHypothesisId) {
        showNotification('Гипотеза не выбрана', 'error');
        return;
    }
    showSection('outcome');
}

async function recordOutcome(event) {
    event.preventDefault();
    
    if (!currentHypothesisId) {
        showNotification('Гипотеза не выбрана', 'error');
        return;
    }
    
    const data = {
        hypothesis_id: currentHypothesisId,
        was_successful: document.getElementById('outcome-success').value === 'true',
        actual_impact: document.getElementById('outcome-impact').value,
        lessons_learned: document.getElementById('outcome-lessons').value
    };
    
    const result = await apiCall('/api/record-outcome', 'POST', data);
    
    if (result && result.success) {
        showNotification('Исход записан', 'success');
        document.getElementById('outcome-form').reset();
        
        // Возвращаемся к гипотезе
        await displayHypothesisDetail(currentHypothesisId);
    }
}

// ============================================================================
// Экспорт
// ============================================================================

async function exportHypothesis() {
    if (!currentHypothesisId) {
        showNotification('Гипотеза не выбрана', 'error');
        return;
    }
    
    const result = await apiCall(`/api/export-hypothesis/${currentHypothesisId}`);
    
    if (result && result.success) {
        const jsonStr = JSON.stringify(result.data, null, 2);
        
        // Создаём и скачиваем файл
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(jsonStr));
        element.setAttribute('download', `hypothesis-${currentHypothesisId.substring(0, 8)}.json`);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
        
        showNotification('Гипотеза экспортирована', 'success');
    }
}

// ============================================================================
// Анализ корреляции
// ============================================================================

async function showCorrelationAnalysis() {
    const result = await apiCall('/api/correlation-analysis');
    
    if (!result || !result.success) {
        showNotification('Ошибка загрузки анализа', 'error');
        return;
    }
    
    const analysis = result.analysis;
    
    // Проверяем, достаточно ли данных
    if (analysis.status === 'insufficient_data') {
        document.getElementById('correlation-content').innerHTML = `
            <div style="padding: 20px; background: #fef3c7; border-radius: 8px; color: #92400e;">
                <strong>⚠️ Недостаточно данных</strong>
                <p>${analysis.message}</p>
            </div>
        `;
    } else {
        displayCorrelationAnalysis(analysis);
    }
    
    showSection('correlation');
}

function displayCorrelationAnalysis(analysis) {
    const content = document.getElementById('correlation-content');
    
    const accuracyColor = analysis.accuracy_percentage >= 75 ? '#16a34a' : '#dc2626';
    
    content.innerHTML = `
        <div class="correlation-summary">
            <div class="correlation-stat">
                <div class="correlation-stat-value">${analysis.total_completed}</div>
                <div class="correlation-stat-label">Завершённых гипотез</div>
            </div>
            <div class="correlation-stat">
                <div class="correlation-stat-value">${analysis.correct_predictions}</div>
                <div class="correlation-stat-label">Точных предсказаний</div>
            </div>
            <div class="correlation-stat">
                <div class="correlation-stat-value" style="color: ${accuracyColor};">
                    ${analysis.accuracy_percentage.toFixed(1)}%
                </div>
                <div class="correlation-stat-label">Точность</div>
            </div>
        </div>

        <h4>📊 Детали</h4>
        <table class="correlation-table">
            <thead>
                <tr>
                    <th>Гипотеза</th>
                    <th>Score</th>
                    <th>Предсказание</th>
                    <th>Реальный результат</th>
                    <th>Соответствие</th>
                </tr>
            </thead>
            <tbody>
                ${analysis.data.map(item => `
                    <tr>
                        <td><strong>${item.title}</strong></td>
                        <td>${item.predicted_score.toFixed(1)}/100</td>
                        <td>${getRecommendationText(item.predicted_recommendation)}</td>
                        <td>${item.actual_outcome ? '✓ Успех' : '✗ Неудача'}</td>
                        <td>
                            <span class="${item.correlation_match ? 'match-true' : 'match-false'}">
                                ${item.correlation_match ? '✓ Совпадение' : '✗ Не совпадает'}
                            </span>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>

        <div style="margin-top: 20px; padding: 15px; background: #f0f9ff; border-radius: 8px; border-left: 4px solid #0891b2;">
            <strong>💡 Интерпретация:</strong>
            <p style="margin-top: 8px; font-size: 13px;">
                ${analysis.accuracy_percentage >= 75 
                    ? '✓ Система показывает хорошую точность предсказаний. Рекомендуется использовать для критических решений.' 
                    : '⚠️ Точность ниже целевого значения (75%). Рекомендуется отрегулировать веса факторов после анализа неточных предсказаний.'}
            </p>
        </div>
    `;
}

// ============================================================================
// Обработчики форм
// ============================================================================

function setupFormHandlers() {
    document.getElementById('create-form').addEventListener('submit', createHypothesis);
    document.getElementById('evidence-form').addEventListener('submit', addEvidence);
    document.getElementById('outcome-form').addEventListener('submit', recordOutcome);
}

// ============================================================================
// Утилиты
// ============================================================================

// Функция для переключения видимости (используется в onclick)
window.showSection = showSection;
window.validateHypothesis = validateHypothesis;
window.showOutcomeForm = showOutcomeForm;
window.exportHypothesis = exportHypothesis;
window.showCorrelationAnalysis = showCorrelationAnalysis;
