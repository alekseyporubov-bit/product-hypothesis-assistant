/* ============================================================================
   Product Hypothesis Assistant - JavaScript
   ============================================================================ */

let currentHypothesisId = null;
let evidenceTypes = [];
let currentUser = null;

// ============================================================================
// Инициализация
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    // Загружаем типы доказательств
    await loadEvidenceTypes();

    // Настраиваем обработчики форм
    setupFormHandlers();
    setupAuthHandlers();

    // Инициализируем Google Sign-In (если задан GOOGLE_CLIENT_ID)
    initGoogleSignIn();

    // Проверяем авторизацию: неавторизованные видят экран входа
    const authed = await checkAuth();
    if (authed) {
        await loadHypotheses();
        showSection('welcome');
    }
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

        // Сессия истекла или пользователь вышел — показываем экран входа
        if (response.status === 401) {
            currentUser = null;
            updateAuthUI();
            return null;
        }

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
// Аутентификация Google
// ============================================================================

function showAuthGate() {
    document.getElementById('auth-gate').classList.remove('hidden');
}

function hideAuthGate() {
    document.getElementById('auth-gate').classList.add('hidden');
}

function clearHypothesesList() {
    const list = document.getElementById('hypotheses-list');
    if (list) {
        list.innerHTML = '<p style="color: #999; font-size: 13px;">Нет гипотез</p>';
    }
    currentHypothesisId = null;
}

function updateAuthUI() {
    const userChip = document.getElementById('auth-user');

    if (currentUser) {
        document.getElementById('auth-name').textContent =
            currentUser.name || currentUser.email || 'Пользователь';
        document.getElementById('auth-email').textContent = currentUser.email || '';

        const avatar = document.getElementById('auth-avatar');
        if (currentUser.avatar_url) {
            avatar.textContent = '';
            avatar.style.backgroundImage = `url('${currentUser.avatar_url}')`;
        } else {
            avatar.style.backgroundImage = '';
            avatar.textContent = (currentUser.name || 'U').charAt(0).toUpperCase();
        }

        userChip.classList.remove('hidden');
        hideAuthGate();
    } else {
        userChip.classList.add('hidden');
        showAuthGate();
    }
}

async function checkAuth() {
    const result = await apiCall('/api/auth/status', 'GET');
    if (result && result.authenticated) {
        currentUser = result.user;
        updateAuthUI();
        return true;
    }
    currentUser = null;
    updateAuthUI();
    return false;
}

async function logout() {
    await apiCall('/api/auth/logout', 'POST');
    currentUser = null;
    updateAuthUI();
    clearHypothesesList();
    showSection('welcome');
}

async function handleGoogleCredential(response) {
    if (!response || !response.credential) {
        showAuthError('Не удалось получить Google ID token');
        return;
    }

    const result = await postAuth('/api/auth/login', {
        credential: response.credential,
    });

    if (result && result.success) {
        await onAuthSuccess(result);
    }
}

function initGoogleSignIn() {
    const hint = document.getElementById('auth-config-hint');
    const button = document.getElementById('g_id_signin');

    if (!window.GOOGLE_CLIENT_ID) {
        if (hint) hint.classList.remove('hidden');
        return;
    }

    if (!(window.google && window.google.accounts && window.google.accounts.id)) {
        if (hint) {
            hint.textContent = '⚠️ Не удалось загрузить Google Sign-In. Проверьте подключение к интернету.';
            hint.classList.remove('hidden');
        }
        return;
    }

    window.google.accounts.id.initialize({
        client_id: window.GOOGLE_CLIENT_ID,
        callback: handleGoogleCredential,
    });
    window.google.accounts.id.renderButton(button, {
        theme: 'outline',
        size: 'large',
        width: 260,
    });
}

// ============================================================================
// Логин / регистрация по логину и паролю
// ============================================================================

function switchAuthMode(mode) {
    const isLogin = mode === 'login';
    document.getElementById('auth-tab-login').classList.toggle('active', isLogin);
    document.getElementById('auth-tab-register').classList.toggle('active', !isLogin);
    document.getElementById('login-form').classList.toggle('hidden', !isLogin);
    document.getElementById('register-form').classList.toggle('hidden', isLogin);
    clearAuthError();
}

function showAuthError(message) {
    const el = document.getElementById('auth-error');
    if (el) {
        el.textContent = message;
        el.classList.remove('hidden');
    }
}

function clearAuthError() {
    const el = document.getElementById('auth-error');
    if (el) {
        el.textContent = '';
        el.classList.add('hidden');
    }
}

async function postAuth(endpoint, payload) {
    clearAuthError();
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json().catch(() => null);
        if (!response.ok) {
            showAuthError((result && result.error) || 'Ошибка входа');
            return null;
        }
        return result;
    } catch (error) {
        showAuthError('Ошибка сети: ' + error.message);
        return null;
    }
}

async function onAuthSuccess(result) {
    currentUser = result.user;
    updateAuthUI();
    clearAuthError();

    document.getElementById('login-password').value = '';
    document.getElementById('register-password').value = '';
    document.getElementById('register-password2').value = '';

    showNotification(
        `Добро пожаловать, ${currentUser.name || currentUser.email || currentUser.login || ''}!`,
        'success'
    );
    await loadHypotheses();
    showSection('welcome');
}

async function handlePasswordLogin(event) {
    event.preventDefault();
    const login = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    if (!login || !password) {
        showAuthError('Укажите логин и пароль');
        return;
    }

    const result = await postAuth('/api/auth/password-login', { login, password });
    if (result && result.success) {
        await onAuthSuccess(result);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const login = document.getElementById('register-username').value.trim();
    const password = document.getElementById('register-password').value;
    const password2 = document.getElementById('register-password2').value;

    if (!login || !password) {
        showAuthError('Укажите логин и пароль');
        return;
    }
    if (password !== password2) {
        showAuthError('Пароли не совпадают');
        return;
    }
    // Клиентская валидация сложности (дублирует серверную).
    if (password.length < 8) {
        showAuthError('Пароль должен быть не короче 8 символов');
        return;
    }
    if (!/[A-Za-zА-Яа-яЁё]/.test(password)) {
        showAuthError('Пароль должен содержать хотя бы одну букву');
        return;
    }
    if (!/[0-9]/.test(password)) {
        showAuthError('Пароль должен содержать хотя бы одну цифру');
        return;
    }

    const result = await postAuth('/api/auth/register', { login, password });
    if (result && result.success) {
        await onAuthSuccess(result);
    }
}

function setupAuthHandlers() {
    document.getElementById('login-form').addEventListener('submit', handlePasswordLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
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

    // Показываем автоматически собранные исследования
    if (hyp.auto_research_sources && hyp.auto_research_sources.length > 0) {
        displayAutoResearchList(hyp.auto_research_sources);
        document.getElementById('auto-research-empty').classList.add('hidden');
    } else {
        document.getElementById('auto-research-list').innerHTML = '';
        document.getElementById('auto-research-empty').classList.remove('hidden');
        document.getElementById('auto-research-empty').innerHTML =
            '<p>🔬 Нажмите кнопку выше, чтобы найти исследования</p>';
    }
    
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
// 🔥 НОВАЯ ФУНКЦИОНАЛЬНАЯ ВОЗМОЖНОСТЬ: Автоматический поиск исследований
// ============================================================================

async function scanResearch() {
    if (!currentHypothesisId) {
        showNotification('Сначала создайте гипотезу', 'error');
        return;
    }
    
    const btn = document.getElementById('btn-scan-research');
    const loading = document.getElementById('auto-research-loading');
    const emptyState = document.getElementById('auto-research-empty');
    
    btn.disabled = true;
    btn.textContent = '⏳ Поиск...';
    loading.classList.remove('hidden');
    emptyState.classList.add('hidden');
    document.getElementById('auto-research-list').innerHTML = '';
    
    showNotification('Ищем исследования в открытых источниках...', 'info');
    
    try {
        const result = await apiCall(`/api/scan-research/${currentHypothesisId}`, 'POST');
        
        if (result && result.success) {
            const count = result.research_count;
            showNotification(`Найдено ${count} исследований!`, 'success');
            
            if (count > 0) {
                displayAutoResearchList(result.research_sources);
                emptyState.classList.add('hidden');
            } else {
                emptyState.classList.remove('hidden');
                emptyState.innerHTML = '<p style="color: #999; padding: 20px;">Исследования не найдены.</p>';
            }
        } else {
            showNotification(result?.error || 'Ошибка поиска', 'error');
            emptyState.classList.remove('hidden');
        }
    } catch (error) {
        showNotification(`Ошибка: ${error.message}`, 'error');
        emptyState.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.textContent = '🔍 Найти исследования в открытых источниках';
        loading.classList.add('hidden');
    }
}

function displayAutoResearchList(sources) {
    const list = document.getElementById('auto-research-list');
    list.innerHTML = '';
    
    if (!sources || sources.length === 0) {
        list.innerHTML = '<p style="color: #999; padding: 20px;">Нет найденных исследований</p>';
        return;
    }
    
    sources.forEach((source) => {
        const item = document.createElement('div');
        item.className = 'auto-research-item';
        item.onclick = () => showResearchDetailModal(source);
        item.style.cursor = 'pointer';
        
        const relevance = source.relevance_score || 0;
        let verdict = '';
        let verdictClass = '';
        let trustLevel = '';
        let trustPercent = 0;
        
        if (relevance >= 0.8) {
            verdict = '✅ Сильное доказательство';
            verdictClass = 'verdict-strong';
            trustLevel = 'Высокая';
            trustPercent = Math.round(relevance * 100);
        } else if (relevance >= 0.6) {
            verdict = '⚠️ Умеренное доказательство';
            verdictClass = 'verdict-moderate';
            trustLevel = 'Средняя';
            trustPercent = Math.round(relevance * 100);
        } else if (relevance >= 0.4) {
            verdict = '❓ Слабое доказательство';
            verdictClass = 'verdict-weak';
            trustLevel = 'Низкая';
            trustPercent = Math.round(relevance * 100);
        } else {
            verdict = '❌ Незначительное';
            verdictClass = 'verdict-minimal';
            trustLevel = 'Очень низкая';
            trustPercent = Math.round(relevance * 100);
        }
        
        const year = source.year || 'N/A';
        const authors = source.authors && source.authors.length > 0 
            ? source.authors.join(', ').substring(0, 80) 
            : 'Авторы не указаны';
        
        item.innerHTML = `
            <div class="auto-research-info">
                <div class="auto-research-header">
                    <div class="auto-research-title">${source.title || 'Без названия'}</div>
                    <span class="verdict-badge ${verdictClass}">${verdict}</span>
                </div>
                <div class="auto-research-meta">
                    <span class="meta-item">📅 ${year}</span>
                    <span class="meta-item">👥 ${authors}</span>
                    <span class="meta-item">📊 Релевантность: ${(relevance * 100).toFixed(0)}%</span>
                </div>
                <div class="auto-research-abstract">${source.abstract ? source.abstract.substring(0, 150) + '...' : 'Нет аннотации'}</div>
                <div class="auto-research-trust">
                    <div class="trust-label">Доверие: ${trustLevel} (${trustPercent}%)</div>
                    <div class="trust-bar">
                        <div class="trust-fill" style="width: ${trustPercent}%; background: ${getTrustColor(trustPercent)}"></div>
                    </div>
                </div>
                ${source.url ? `<div class="auto-research-url"><a href="${source.url}" target="_blank">🔗 Источник</a></div>` : ''}
            </div>
            <div class="auto-research-click-hint">Нажмите для деталей →</div>
        `;
        
        list.appendChild(item);
    });
}

function getTrustColor(percent) {
    if (percent >= 80) return '#16a34a';
    if (percent >= 60) return '#ca8a04';
    if (percent >= 40) return '#ea580c';
    return '#dc2626';
}

function showResearchDetailModal(source) {
    const modal = document.getElementById('research-modal');
    const relevance = source.relevance_score || 0;

    document.getElementById('modal-title').textContent = source.title || 'Без названия';
    document.getElementById('modal-authors').textContent =
        (source.authors && source.authors.length > 0) ? source.authors.join(', ') : 'Не указаны';
    document.getElementById('modal-year').textContent = source.year || 'N/A';
    document.getElementById('modal-source').textContent = source.source || 'Не указан';

    const urlEl = document.getElementById('modal-url');
    if (source.url) {
        urlEl.innerHTML = '<a href="' + source.url + '" target="_blank">' + source.url + '</a>';
    } else {
        urlEl.textContent = 'Не указана';
    }

    const verdictEl = document.getElementById('modal-verdict');
    let verdictText, verdictClass, trustLevel;
    if (relevance >= 0.8) {
        verdictText = '✅ Сильное доказательство';
        verdictClass = 'verdict-strong';
        trustLevel = 'Высокая';
    } else if (relevance >= 0.6) {
        verdictText = '⚠️ Умеренное доказательство';
        verdictClass = 'verdict-moderate';
        trustLevel = 'Средняя';
    } else if (relevance >= 0.4) {
        verdictText = '❓ Слабое доказательство';
        verdictClass = 'verdict-weak';
        trustLevel = 'Низкая';
    } else {
        verdictText = '❌ Незначительное';
        verdictClass = 'verdict-minimal';
        trustLevel = 'Очень низкая';
    }
    verdictEl.textContent = verdictText;
    verdictEl.className = 'detail-value verdict-badge ' + verdictClass;

    document.getElementById('modal-confidence').textContent =
        trustLevel + ' (' + (relevance * 100).toFixed(0) + '%)';

    document.getElementById('modal-abstract').textContent = source.abstract || 'Аннотация отсутствует';

    modal.classList.remove('hidden');
}

function closeResearchModal() {
    document.getElementById('research-modal').classList.add('hidden');
}

document.addEventListener('click', function (e) {
    const modal = document.getElementById('research-modal');
    if (modal && e.target === modal) {
        modal.classList.add('hidden');
    }
});
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
window.switchAuthMode = switchAuthMode;
window.logout = logout;
