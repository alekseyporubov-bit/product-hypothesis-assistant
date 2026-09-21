"""
Product Hypothesis Assistant
Система поддержки принятия решений продуктового менеджера
при обосновании новых фичей продукта.

Разработана на основе TDPD (Test-Driven Product Development) фреймворка
и структуры ГОСТ 34.602-2026

Техническое задание: Система помогает подготовить количественно обоснованное
заключение о потенциале продуктовой гипотезы в виде score уверенности.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
import os
import uuid
from research_finder import ResearchFinder


# ============================================================================
# 1. CONTEXT: Определение контекста и ролей (TDPD)
# ============================================================================

class HypothesisStatus(Enum):
    """Статус гипотезы в процессе валидации"""
    DRAFT = "draft"  # Черновик
    IN_RESEARCH = "in_research"  # На исследовании
    VALIDATED = "validated"  # Валидирована
    REJECTED = "rejected"  # Отклонена
    IN_DEVELOPMENT = "in_development"  # На разработке
    RELEASED = "released"  # В production
    COMPLETED = "completed"  # Закончена (с результатом)


class EvidenceType(Enum):
    """Типы доказательств для поддержки гипотезы"""
    MARKET_RESEARCH = "market_research"  # Исследование рынка
    USER_FEEDBACK = "user_feedback"  # Обратная связь пользователей
    COMPETITOR_ANALYSIS = "competitor_analysis"  # Анализ конкурентов
    ANALYTICS = "analytics"  # Данные аналитики
    EXPERT_OPINION = "expert_opinion"  # Мнение эксперта
    CASE_STUDY = "case_study"  # Case study успеха


class ScoringFactor(Enum):
    """Факторы для скоринга гипотезы"""
    PROBLEM_SEVERITY = "problem_severity"  # Серьёзность проблемы (0-10)
    MARKET_SIZE = "market_size"  # Размер рынка (0-10)
    USER_DEMAND = "user_demand"  # Спрос пользователей (0-10)
    COMPETITIVE_ADVANTAGE = "competitive_advantage"  # Конкурентное преимущество (0-10)
    IMPLEMENTATION_EFFORT = "implementation_effort"  # Усилия реализации (0-10, инверсная)
    ALIGNMENT = "alignment"  # Соответствие стратегии (0-10)


# ============================================================================
# 2. DATA MODELS: Структуры данных для хранения гипотез и доказательств
# ============================================================================

@dataclass
class Evidence:
    """Доказательство в поддержку или против гипотезы"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: EvidenceType = EvidenceType.MARKET_RESEARCH
    title: str = ""
    description: str = ""
    source: str = ""  # Источник информации
    confidence: float = 0.5  # 0-1, уверенность в доказательстве
    supports: bool = True  # True = поддерживает, False = опровергает
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "evidence_type": self.evidence_type.value,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "confidence": self.confidence,
            "supports": self.supports,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ScoreBreakdown:
    """Детальное разложение score по факторам"""
    factor: ScoringFactor
    score: float  # 0-10
    rationale: str  # Обоснование оценки
    evidence_count: int = 0  # Количество доказательств
    
    def to_dict(self):
        return {
            "factor": self.factor.value,
            "score": self.score,
            "rationale": self.rationale,
            "evidence_count": self.evidence_count
        }


@dataclass
class HypothesisScore:
    """Итоговый score гипотезы с детализацией"""
    overall_score: float  # 0-100, итоговая оценка
    confidence_level: str  # "low", "medium", "high"
    breakdown: List[ScoreBreakdown] = field(default_factory=list)
    supporting_evidence_count: int = 0
    contradicting_evidence_count: int = 0
    data_completeness: float = 0.0  # 0-1, насколько полны данные для оценки
    recommendation: str = ""  # Рекомендация (proceed/investigate/reject)
    research_sources: List[Dict] = field(default_factory=list)  # Найденные исследования из открытых источников
    
    def to_dict(self):
        return {
            "overall_score": self.overall_score,
            "confidence_level": self.confidence_level,
            "breakdown": [item.to_dict() for item in self.breakdown],
            "supporting_evidence_count": self.supporting_evidence_count,
            "contradicting_evidence_count": self.contradicting_evidence_count,
            "data_completeness": self.data_completeness,
            "recommendation": self.recommendation,
            "research_sources": self.research_sources
        }


@dataclass
class SurveyQuestion:
    """Вопрос для анкетирования пользователей"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    question: str = ""
    question_type: str = "open"  # open, multiple_choice, rating
    options: List[str] = field(default_factory=list)  # Для multiple_choice
    reasoning: str = ""  # Почему это важно для валидации гипотезы
    
    def to_dict(self):
        return asdict(self)


@dataclass
class RealWorldOutcome:
    """Фактический исход фичи после релиза (постфактум)"""
    hypothesis_id: str = ""
    was_successful: bool = False  # True = успех, False = неудача/нет эффекта
    actual_impact: str = ""  # Описание реального воздействия
    metrics: Dict[str, float] = field(default_factory=dict)  # Метрики эффекта
    lessons_learned: str = ""  # Извлечённые уроки
    recorded_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            "hypothesis_id": self.hypothesis_id,
            "was_successful": self.was_successful,
            "actual_impact": self.actual_impact,
            "metrics": self.metrics,
            "lessons_learned": self.lessons_learned,
            "recorded_at": self.recorded_at.isoformat()
        }


@dataclass
class Hypothesis:
    """Основная структура гипотезы/фичи для валидации"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    problem_statement: str = ""  # Какую проблему решает
    target_users: str = ""  # Кто целевые пользователи
    expected_outcome: str = ""  # Какой результат ожидается
    user_id: str = ""  # Владелец гипотезы (пусто = не привязана/легаси)
    
    status: HypothesisStatus = HypothesisStatus.DRAFT
    score: Optional[HypothesisScore] = None
    
    evidence: List[Evidence] = field(default_factory=list)
    auto_research_sources: List[Dict] = field(default_factory=list)
    survey_questions: List[SurveyQuestion] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Постфактум данные (заполняются после релиза)
    outcome: Optional[RealWorldOutcome] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "problem_statement": self.problem_statement,
            "target_users": self.target_users,
            "expected_outcome": self.expected_outcome,
            "user_id": self.user_id,
            "status": self.status.value,
            "score": self.score.to_dict() if self.score else None,
            "evidence": [e.to_dict() for e in self.evidence],
            "evidence_count": len(self.evidence),
            "auto_research_sources": self.auto_research_sources,
            "auto_research_count": len(self.auto_research_sources),
            "survey_questions": [q.to_dict() for q in self.survey_questions],
            "survey_questions_count": len(self.survey_questions),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "outcome": self.outcome.to_dict() if self.outcome else None
        }


# ============================================================================
# 3. SCORING ENGINE: Логика вычисления score (Вариант A - эвристический)
# ============================================================================

class ScoringEngine:
    """
    Двигатель скоринга гипотез.
    Формирует score уверенности на основе собранных доказательств.
    
    Реализован вариант A ТЗ: LLM-агент с эвристическим скорингом.
    """
    
    # Веса факторов (информационные — с DL-002 не влияют на итоговый score,
    # который считается по confidence-weighted формуле agreement × strength).
    FACTOR_WEIGHTS = {
        ScoringFactor.PROBLEM_SEVERITY: 0.20,
        ScoringFactor.MARKET_SIZE: 0.15,
        ScoringFactor.USER_DEMAND: 0.25,
        ScoringFactor.COMPETITIVE_ADVANTAGE: 0.15,
        ScoringFactor.IMPLEMENTATION_EFFORT: 0.15,
        ScoringFactor.ALIGNMENT: 0.10,
    }

    # Насыщение покрытия: при SUPPORT_SATURATION «надёжных» подтверждающих единиц
    # strength = 1.0 (несколько надёжных источников + много положительных
    # доказательств → score ≈ 100).
    SUPPORT_SATURATION = 8.0
    
    @staticmethod
    def calculate_score(hypothesis: Hypothesis) -> HypothesisScore:
        """
        Вычисляет итоговый score гипотезы.
        
        Процесс:
        1. Взвешивает доказательства по confidence (надёжности источников)
        2. Ищет подтверждающие исследования в открытых источниках
        3. Считает согласованность (agreement) и покрытие (strength) подтверждений
        4. Итоговый score = 100 × agreement × strength (DL-002)
        5. Выдаёт confidence level и рекомендацию
        """
        
        # =========================================================================
        # 1. Confidence-weighted сигнал доказательств (DL-002)
        # =========================================================================
        supporting_count = sum(1 for e in hypothesis.evidence if e.supports)
        contradicting_count = sum(1 for e in hypothesis.evidence if not e.supports)

        # Учитываем надёжность каждого источника: уверенное доказательство (0.9)
        # вносит больший вклад в итог, чем слабое (0.2).
        support_weight = sum(e.confidence for e in hypothesis.evidence if e.supports)
        contradict_weight = sum(e.confidence for e in hypothesis.evidence if not e.supports)

        # =========================================================================
        # 2. Исследования из открытых источников (надёжный подтверждающий сигнал)
        # =========================================================================
        research_finder = ResearchFinder()
        research_analysis = research_finder.search_problem_severity(
            problem_statement=hypothesis.problem_statement,
            target_users=hypothesis.target_users
        )
        research_count = research_analysis.get("research_count", 0)
        research_quality = research_analysis.get("average_relevance", 0.0)
        research_sources = research_analysis.get("research_sources", [])

        # Авто-исследования считаем подтверждающим сигналом, взвешенным по релевантности.
        research_weight = min(research_count, 5) * research_quality

        # =========================================================================
        # 3. Информационная разбивка по факторам (confidence-weighted).
        #    Не влияет на итоговый score — только детализация для UI (DL-002).
        # =========================================================================
        breakdown: List[ScoreBreakdown] = []

        # Фактор 1: Серьёзность проблемы
        problem_count = sum(
            1 for e in hypothesis.evidence
            if e.evidence_type == EvidenceType.MARKET_RESEARCH and e.supports
        )
        problem_weight = sum(
            e.confidence for e in hypothesis.evidence
            if e.evidence_type == EvidenceType.MARKET_RESEARCH and e.supports
        )
        user_evidence_score = min(10, problem_weight * 2.5)
        research_evidence_score = min(10, research_count * 1.5 + research_quality * 3)
        problem_score = user_evidence_score * 0.4 + research_evidence_score * 0.6

        rationale = f"Пользовательские доказательства: {problem_count} шт. (confidence-вес {problem_weight:.2f}) | "
        rationale += f"Исследования из открытых источников: {research_count} (качество: {research_quality:.2f}) | "
        rationale += f"{research_analysis.get('recommendation', 'N/A')}"

        breakdown.append(ScoreBreakdown(
            factor=ScoringFactor.PROBLEM_SEVERITY,
            score=problem_score,
            rationale=rationale,
            evidence_count=problem_count + research_count
        ))
        
        # Фактор 2: Размер рынка
        market_count = sum(
            1 for e in hypothesis.evidence
            if e.evidence_type == EvidenceType.MARKET_RESEARCH
        )
        market_weight = sum(
            e.confidence for e in hypothesis.evidence
            if e.evidence_type == EvidenceType.MARKET_RESEARCH
        )
        market_score = min(10, market_weight * 2.0)
        breakdown.append(ScoreBreakdown(
            factor=ScoringFactor.MARKET_SIZE,
            score=market_score,
            rationale=f"Наличие данных о размере рынка: {market_count} источников (confidence-вес {market_weight:.2f})",
            evidence_count=market_count
        ))

        # Фактор 3: Спрос пользователей
        demand_count = sum(
            1 for e in hypothesis.evidence
            if e.evidence_type == EvidenceType.USER_FEEDBACK
        )
        demand_weight = sum(
            e.confidence for e in hypothesis.evidence
            if e.evidence_type == EvidenceType.USER_FEEDBACK
        )
        demand_score = min(10, demand_weight * 3.0)
        breakdown.append(ScoreBreakdown(
            factor=ScoringFactor.USER_DEMAND,
            score=demand_score,
            rationale=f"Подтверждение спроса от пользователей: {demand_count} упоминаний (confidence-вес {demand_weight:.2f})",
            evidence_count=demand_count
        ))

        # Фактор 4: Конкурентное преимущество
        competitor_count = sum(
            1 for e in hypothesis.evidence
            if e.evidence_type == EvidenceType.COMPETITOR_ANALYSIS
        )
        competitor_weight = sum(
            e.confidence for e in hypothesis.evidence
            if e.evidence_type == EvidenceType.COMPETITOR_ANALYSIS
        )
        competitive_score = min(10, competitor_weight * 3.5)
        breakdown.append(ScoreBreakdown(
            factor=ScoringFactor.COMPETITIVE_ADVANTAGE,
            score=competitive_score,
            rationale=f"Анализ конкурентного ландшафта: {competitor_count} источников (confidence-вес {competitor_weight:.2f})",
            evidence_count=competitor_count
        ))

        # Фактор 5: Усилия реализации (инверсная — меньше усилий = выше score)
        effort_score = 8.0  # По умолчанию высокий (требует отдельного анализа)
        breakdown.append(ScoreBreakdown(
            factor=ScoringFactor.IMPLEMENTATION_EFFORT,
            score=effort_score,
            rationale="Оценка требует детального технического анализа",
            evidence_count=0
        ))

        # Фактор 6: Соответствие стратегии
        alignment_count = sum(
            1 for e in hypothesis.evidence
            if e.evidence_type == EvidenceType.EXPERT_OPINION
        )
        alignment_weight = sum(
            e.confidence for e in hypothesis.evidence
            if e.evidence_type == EvidenceType.EXPERT_OPINION
        )
        alignment_score = min(10, 5 + alignment_weight * 1.5)
        breakdown.append(ScoreBreakdown(
            factor=ScoringFactor.ALIGNMENT,
            score=alignment_score,
            rationale=f"Мнение экспертов о стратегическом соответствии: {alignment_count} источников (confidence-вес {alignment_weight:.2f})",
            evidence_count=alignment_count
        ))
        
        # =========================================================================
        # 4. Итоговый score: согласованность × покрытие (DL-002)
        # =========================================================================
        total_support = support_weight + research_weight
        total_weight = total_support + contradict_weight

        # Доля подтверждающего сигнала (0..1): 1.0 если всё подтверждает,
        # стремится к 0 если большинство доказательств опровергает проблему.
        agreement = total_support / total_weight if total_weight > 0 else 0.0

        # Покрытие надёжными источниками (0..1). Насыщается при SUPPORT_SATURATION
        # «надёжных» подтверждающих единиц: несколько надёжных источников + много
        # положительных доказательств дают strength, близкий к 1.
        strength = min(1.0, total_support / ScoringEngine.SUPPORT_SATURATION)

        overall = max(0.0, min(100.0, 100.0 * agreement * strength))

        # Определяем уровень уверенности
        if overall >= 70:
            confidence_level = "high"
            recommendation = "proceed"  # Рекомендуем идти в разработку
        elif overall >= 50:
            confidence_level = "medium"
            recommendation = "investigate"  # Рекомендуем дополнительное исследование
        else:
            confidence_level = "low"
            recommendation = "reject"  # Рекомендуем отклонить

        # Оцениваем полноту данных
        total_evidence = len(hypothesis.evidence)
        data_completeness = min(1.0, total_evidence / 10)  # 10+ доказательств = 100%

        return HypothesisScore(
            overall_score=round(overall, 2),
            confidence_level=confidence_level,
            breakdown=breakdown,
            supporting_evidence_count=supporting_count,
            contradicting_evidence_count=contradicting_count,
            data_completeness=data_completeness,
            recommendation=recommendation,
            research_sources=research_sources
        )


# ============================================================================
# 4. HYPOTHESIS MANAGER: Управление гипотезами и их жизненным циклом
# ============================================================================

class HypothesisManager:
    """
    Менеджер гипотез - управляет созданием, валидацией и отслеживанием гипотез.
    Реализует workflow TDPD: Context → Problem → Input → Red → Green → Output/UAT
    """
    
    
    def __init__(self):
        self.hypotheses: Dict[str, Hypothesis] = {}
        self.scoring_engine = ScoringEngine()

        # Единственное хранилище — PostgreSQL (DATABASE_URL / POSTGRES_URL).
        # Без строки подключения данные живут только в памяти процесса.
        self.db_url = (
            os.environ.get("DATABASE_URL")
            or os.environ.get("POSTGRES_URL")
            or ""
        ).strip()
        self.use_postgres = bool(self.db_url)

        if self.use_postgres:
            print("🗄️ PostgreSQL включён (DATABASE_URL задан)")
            self._ensure_db_table()
            self.load()
        else:
            print("⚠️ DATABASE_URL не задан — данные хранятся только в памяти и не сохраняются")

    def create_hypothesis(self, title: str, description: str, 
                         problem_statement: str, target_users: str,
                         expected_outcome: str, user_id: str = "") -> Hypothesis:
        """Создаёт новую гипотезу (Context + Problem этапы TDPD)"""
        hypothesis = Hypothesis(
            title=title,
            description=description,
            problem_statement=problem_statement,
            target_users=target_users,
            expected_outcome=expected_outcome,
            user_id=user_id or "",
            status=HypothesisStatus.DRAFT
        )
        self.hypotheses[hypothesis.id] = hypothesis
        self.save()  # ← Сохраняем в БД
        return hypothesis
    
    def add_evidence(self, hypothesis_id: str, evidence: Evidence,
                     user_id: Optional[str] = None) -> bool:
        """Добавляет доказательство в поддержку гипотезы (Input этап TDPD)"""
        hypothesis = self._owned_hypothesis(hypothesis_id, user_id)
        if hypothesis is None:
            return False
        hypothesis.evidence.append(evidence)
        hypothesis.updated_at = datetime.now()
        self.save()  # ← Сохраняем в БД
        return True
    
    def add_survey_question(self, hypothesis_id: str, question: SurveyQuestion,
                            user_id: Optional[str] = None) -> bool:
        """Добавляет вопрос для анкетирования"""
        hypothesis = self._owned_hypothesis(hypothesis_id, user_id)
        if hypothesis is None:
            return False
        hypothesis.survey_questions.append(question)
        self.save()  # ← Сохраняем в БД
        return True
    
    def validate_hypothesis(self, hypothesis_id: str,
                            user_id: Optional[str] = None) -> Tuple[bool, Optional[HypothesisScore]]:
        """
        Валидирует гипотезу и вычисляет score.
        Реализует Red/Green этапы TDPD (проверка гипотез).
        """
        hypothesis = self._owned_hypothesis(hypothesis_id, user_id)
        if hypothesis is None:
            return False, None
        
        # Вычисляем score
        score = self.scoring_engine.calculate_score(hypothesis)
        hypothesis.score = score
        
        # Обновляем статус
        if score.recommendation == "proceed":
            hypothesis.status = HypothesisStatus.VALIDATED
        elif score.recommendation == "investigate":
            hypothesis.status = HypothesisStatus.IN_RESEARCH
        else:
            hypothesis.status = HypothesisStatus.REJECTED
        
        hypothesis.updated_at = datetime.now()
        self.save()  # ← Сохраняем в БД
        return True, score
    
    def record_outcome(self, hypothesis_id: str, outcome: RealWorldOutcome,
                       user_id: Optional[str] = None) -> bool:
        """
        Записывает фактический исход фичи после релиза (Output/UAT этап TDPD).
        Это ключевой этап для проверки корреляции score ↔ реальный успех (Цель 3 ТЗ).
        """
        hypothesis = self._owned_hypothesis(hypothesis_id, user_id)
        if hypothesis is None:
            return False
        
        outcome.hypothesis_id = hypothesis_id
        hypothesis.outcome = outcome
        hypothesis.status = HypothesisStatus.COMPLETED
        hypothesis.updated_at = datetime.now()
        self.save()  # ← Сохраняем в БД
        return True
    
    def _owned_hypothesis(self, hypothesis_id: str,
                          user_id: Optional[str] = None) -> Optional[Hypothesis]:
        """Возвращает гипотезу, если она принадлежит user_id (или фильтр не задан)."""
        hypothesis = self.hypotheses.get(hypothesis_id)
        if hypothesis is None:
            return None
        if user_id is not None and hypothesis.user_id != user_id:
            return None
        return hypothesis

    def get_hypothesis(self, hypothesis_id: str,
                       user_id: Optional[str] = None) -> Optional[Hypothesis]:
        """Получает гипотезу по ID (с проверкой владельца, если задан user_id)"""
        return self._owned_hypothesis(hypothesis_id, user_id)
    
    def list_hypotheses(self, user_id: Optional[str] = None) -> List[Hypothesis]:
        """Список гипотез (при user_id — только гипотезы этого пользователя)"""
        if user_id is None:
            return list(self.hypotheses.values())
        return [h for h in self.hypotheses.values() if h.user_id == user_id]

    def claim_orphaned_hypotheses(self, user_id: str) -> int:
        """Привязывает «сиротские» гипотезы (user_id="") к первому пользователю.
        Возвращает число привязанных гипотез."""
        claimed = 0
        for hypothesis in self.hypotheses.values():
            if hypothesis.user_id == "":
                hypothesis.user_id = user_id
                hypothesis.updated_at = datetime.now()
                claimed += 1
        if claimed:
            self.save()
        return claimed
    
    def export_hypothesis(self, hypothesis_id: str,
                          user_id: Optional[str] = None) -> Optional[Dict]:
        """Экспортирует гипотезу в JSON (Output этап TDPD)"""
        hypothesis = self._owned_hypothesis(hypothesis_id, user_id)
        if not hypothesis:
            return None
        return hypothesis.to_dict()

    def scan_auto_research(self, hypothesis_id: str,
                           user_id: Optional[str] = None) -> Dict:
        """
        🔥 НОВАЯ ФУНКЦИОНАЛЬНАЯ ВОЗМОЖНОСТЬ:
        Автоматически ищет исследования в открытых источниках по теме гипотезы
        и сохраняет их в auto_research_sources (максимум 5).
        """
        hypothesis = self._owned_hypothesis(hypothesis_id, user_id)
        if not hypothesis:
            return {'success': False, 'error': 'Гипотеза не найдена'}

        # Инициализируем ResearchFinder для поиска
        research_finder = ResearchFinder()

        # Ищем исследования по проблеме и целевой аудитории
        research_analysis = research_finder.search_problem_severity(
            problem_statement=hypothesis.problem_statement,
            target_users=hypothesis.target_users
        )

        # Ограничиваем максимум 5 результатами
        sources = research_analysis.get('research_sources', [])[:5]

        # Сохраняем в гипотезу
        hypothesis.auto_research_sources = sources
        hypothesis.updated_at = datetime.now()
        self.save()

        return {
            'success': True,
            'hypothesis_id': hypothesis_id,
            'hypothesis_title': hypothesis.title,
            'research_count': len(sources),
            'research_sources': sources,
            'average_relevance': research_analysis.get('average_relevance', 0),
            'message': f'Найдено {len(sources)} исследований из открытых источников'
        }
    
    # ========================================================================
    # PERSISTENCE: Сохранение в PostgreSQL (DATABASE_URL)
    # ========================================================================

    POSTGRES_TABLE = "hypotheses"

    # RelaxDev: «TLS не используется. База доступна только из внутренней сети,
    # поэтому в коде укажите ssl: false, а из строки уберите sslmode=require,
    # ssl=true и channel_binding». Эти параметры вырезаем из DATABASE_URL.
    _BLOCKED_SSL_PARAMS = frozenset(
        {"sslmode", "ssl", "channel_binding", "sslcert", "sslkey", "sslrootcert"}
    )

    @classmethod
    def _normalize_postgres_url(cls, db_url: str) -> str:
        """Убирает SSL-параметры из строки подключения (RelaxDev работает без TLS)."""
        import urllib.parse as _urlparse

        parsed = _urlparse.urlsplit(db_url)
        query = [
            (k, v)
            for k, v in _urlparse.parse_qsl(parsed.query, keep_blank_values=True)
            if k.lower() not in cls._BLOCKED_SSL_PARAMS
        ]
        return _urlparse.urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                _urlparse.urlencode(query),
                parsed.fragment,
            )
        )

    def _get_postgres_connection(self):
        """Открывает новое соединение с PostgreSQL по DATABASE_URL (без SSL)."""
        try:
            import psycopg2
        except ImportError as e:
            raise RuntimeError(
                "Библиотека psycopg2 не установлена. Добавьте 'psycopg2-binary' "
                "в requirements.txt и выполните pip install."
            ) from e
        # RelaxDev не поддерживает TLS: принудительно отключаем SSL.
        return psycopg2.connect(
            self._normalize_postgres_url(self.db_url), sslmode="disable"
        )

    def _ensure_db_table(self) -> bool:
        """Идемпотентно создаёт таблицу hypotheses, если её ещё нет."""
        try:
            conn = self._get_postgres_connection()
        except Exception as e:
            print(f"⚠️ PostgreSQL: не удалось подключиться ({e})")
            return False
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.POSTGRES_TABLE} (
                        id UUID PRIMARY KEY,
                        data JSONB NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            print(f"🗄️ PostgreSQL: таблица '{self.POSTGRES_TABLE}' готова")
            return True
        except Exception as e:
            print(f"⚠️ PostgreSQL: не удалось создать таблицу '{self.POSTGRES_TABLE}': {e}")
            return False
        finally:
            conn.close()

    def _save_to_postgres(self) -> bool:
        """Сохраняет все гипотезы в PostgreSQL (одна строка на гипотезу)."""
        try:
            import psycopg2.extras
        except ImportError:
            return False
        try:
            conn = self._get_postgres_connection()
        except Exception as e:
            print(f"❌ Ошибка сохранения в PostgreSQL: {e}")
            return False
        try:
            with conn, conn.cursor() as cur:
                for h_id, h in self.hypotheses.items():
                    payload = psycopg2.extras.Json(
                        h.to_dict(),
                        dumps=lambda obj: json.dumps(obj, ensure_ascii=False, default=str),
                    )
                    cur.execute(
                        f"""
                        INSERT INTO {self.POSTGRES_TABLE} (id, data, updated_at)
                        VALUES (%s, %s, now())
                        ON CONFLICT (id)
                        DO UPDATE SET data = EXCLUDED.data, updated_at = now()
                        """,
                        (h_id, payload),
                    )
            print(f"🗄️ Данные сохранены в PostgreSQL ({len(self.hypotheses)} гипотез)")
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения в PostgreSQL: {e}")
            return False
        finally:
            conn.close()

    def _load_from_postgres(self) -> bool:
        """Загружает все гипотезы из PostgreSQL."""
        try:
            conn = self._get_postgres_connection()
        except Exception as e:
            print(f"❌ Ошибка загрузки из PostgreSQL: {e}")
            return False
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    f"SELECT id, data FROM {self.POSTGRES_TABLE} ORDER BY updated_at"
                )
                rows = cur.fetchall()
            for h_id, data in rows:
                if isinstance(data, str):
                    data = json.loads(data)
                hypothesis = self._hypothesis_from_dict(data)
                self.hypotheses[h_id] = hypothesis
            print(f"🗄️ Загружено {len(self.hypotheses)} гипотез из PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки из PostgreSQL: {e}")
            return False
        finally:
            conn.close()

    def save(self) -> bool:
        """Сохраняет все гипотезы в PostgreSQL (единственное хранилище)."""
        if not self.use_postgres:
            return True  # БД не настроена — данные только в памяти
        return self._save_to_postgres()

    def load(self) -> bool:
        """Загружает все гипотезы из PostgreSQL."""
        if not self.use_postgres:
            return True  # БД не настроена — начинаем с пустого набора
        return self._load_from_postgres()

    @staticmethod
    def _hypothesis_from_dict(data: Dict) -> Hypothesis:
        """Восстанавливает объект Hypothesis из словаря"""
        try:
            # Восстанавливаем основные поля
            hypothesis = Hypothesis(
                id=data.get('id', str(uuid.uuid4())),
                title=data.get('title', ''),
                description=data.get('description', ''),
                problem_statement=data.get('problem_statement', ''),
                target_users=data.get('target_users', ''),
                expected_outcome=data.get('expected_outcome', ''),
                user_id=data.get('user_id', ''),
                status=HypothesisStatus(data.get('status', 'draft')),
            )
            
            # Восстанавливаем дату создания и обновления
            hypothesis.created_at = datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
            hypothesis.updated_at = datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
            
            # Восстанавливаем доказательства
            for evidence_data in data.get('evidence', []):
                evidence = HypothesisManager._evidence_from_dict(evidence_data)
                hypothesis.evidence.append(evidence)

            # Восстанавливаем вопросы анкеты
            for question_data in data.get('survey_questions', []):
                hypothesis.survey_questions.append(
                    HypothesisManager._survey_question_from_dict(question_data)
                )
            
            # Восстанавливаем score если есть
            if data.get('score'):
                hypothesis.score = HypothesisManager._score_from_dict(data['score'])
            
            # Восстанавливаем outcome если есть
            if data.get('outcome'):
                hypothesis.outcome = HypothesisManager._outcome_from_dict(data['outcome'])
            
            if data.get('auto_research_sources'):
                hypothesis.auto_research_sources = data['auto_research_sources']
            return hypothesis
        except Exception as e:
            print(f"Ошибка восстановления гипотезы: {e}")
            raise
    
    @staticmethod
    def _survey_question_from_dict(data: Dict) -> SurveyQuestion:
        """Восстанавливает объект SurveyQuestion из словаря."""
        return SurveyQuestion(
            id=data.get('id', str(uuid.uuid4())),
            question=data.get('question', ''),
            question_type=data.get('question_type', 'open'),
            options=list(data.get('options', [])),
            reasoning=data.get('reasoning', '')
        )

    @staticmethod
    def _evidence_from_dict(data: Dict) -> Evidence:
        """Восстанавливает объект Evidence из словаря"""
        evidence = Evidence(
            id=data.get('id', str(uuid.uuid4())),
            evidence_type=EvidenceType(data.get('evidence_type', 'market_research')),
            title=data.get('title', ''),
            description=data.get('description', ''),
            source=data.get('source', ''),
            confidence=float(data.get('confidence', 0.5)),
            supports=data.get('supports', True)
        )
        evidence.created_at = datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        return evidence
    
    @staticmethod
    def _score_from_dict(data: Dict) -> HypothesisScore:
        """Восстанавливает объект HypothesisScore из словаря"""
        breakdown = []
        for item in data.get('breakdown', []):
            breakdown.append(ScoreBreakdown(
                factor=ScoringFactor(item.get('factor', 'problem_severity')),
                score=float(item.get('score', 0)),
                rationale=item.get('rationale', ''),
                evidence_count=item.get('evidence_count', 0)
            ))
        
        return HypothesisScore(
            overall_score=float(data.get('overall_score', 0)),
            confidence_level=data.get('confidence_level', 'low'),
            breakdown=breakdown,
            supporting_evidence_count=data.get('supporting_evidence_count', 0),
            contradicting_evidence_count=data.get('contradicting_evidence_count', 0),
            data_completeness=float(data.get('data_completeness', 0.0)),
            recommendation=data.get('recommendation', ''),
            research_sources=data.get('research_sources', [])
        )
    
    @staticmethod
    def _outcome_from_dict(data: Dict) -> RealWorldOutcome:
        """Восстанавливает объект RealWorldOutcome из словаря"""
        outcome = RealWorldOutcome(
            hypothesis_id=data.get('hypothesis_id', ''),
            was_successful=data.get('was_successful', False),
            actual_impact=data.get('actual_impact', ''),
            metrics=data.get('metrics', {}),
            lessons_learned=data.get('lessons_learned', '')
        )
        outcome.recorded_at = datetime.fromisoformat(data.get('recorded_at', datetime.now().isoformat()))
        return outcome
    
    def get_correlation_analysis(self, user_id: Optional[str] = None) -> Dict:
        """
        Анализирует корреляцию между score и реальным исходом (Цель 3 ТЗ).
        Требует проведения 6+ месяцев эксплуатации с регулярной фиксацией исходов.
        """
        hypotheses = self.list_hypotheses(user_id)
        completed = [h for h in hypotheses if h.outcome and h.score]
        
        if not completed:
            return {
                "status": "insufficient_data",
                "message": "Недостаточно данных. Требуется минимум 5-10 фичей с записанными исходами."
            }
        
        correct_predictions = sum(
            1 for h in completed
            if (h.score.recommendation == "proceed" and h.outcome.was_successful) or
               (h.score.recommendation in ["investigate", "reject"] and not h.outcome.was_successful)
        )
        
        accuracy = correct_predictions / len(completed) * 100
        
        return {
            "total_completed": len(completed),
            "correct_predictions": correct_predictions,
            "accuracy_percentage": accuracy,
            "data": [
                {
                    "hypothesis_id": h.id,
                    "title": h.title,
                    "predicted_recommendation": h.score.recommendation,
                    "predicted_score": h.score.overall_score,
                    "actual_outcome": h.outcome.was_successful,
                    "correlation_match": (h.score.recommendation == "proceed") == h.outcome.was_successful
                }
                for h in completed
            ]
        }


# ============================================================================
# 5. INTERACTIVE ASSISTANT: Диалоговый интерфейс (Вариант A - чат-подобный)
# ============================================================================

class HypothesisAssistant:
    """
    Интерактивный ассистент для работы с гипотезами.
    Реализует диалоговый режим (F-08 из ТЗ).
    """
    
    def __init__(self):
        self.manager = HypothesisManager()
        self.current_hypothesis_id: Optional[str] = None
    
    def start_new_hypothesis(self) -> str:
        """Инициирует создание новой гипотезы"""
        print("\n" + "="*70)
        print("Product Hypothesis Assistant v1.0")
        print("Система поддержки принятия решений по новым фичам")
        print("="*70 + "\n")
        
        print("Шаг 1/5: Основная информация о гипотезе\n")
        
        title = input("Название фичи: ").strip()
        if not title:
            print("Ошибка: название не может быть пустым")
            return ""
        
        description = input("Краткое описание (1-2 предложения): ").strip()
        problem = input("Какую проблему решает эта фича? ").strip()
        users = input("Кто целевые пользователи? ").strip()
        outcome = input("Какой результат ожидаем? ").strip()
        
        hypothesis = self.manager.create_hypothesis(
            title=title,
            description=description,
            problem_statement=problem,
            target_users=users,
            expected_outcome=outcome
        )
        
        self.current_hypothesis_id = hypothesis.id
        print(f"\n✓ Гипотеза создана. ID: {hypothesis.id}\n")
        
        return hypothesis.id
    
    def add_evidence_interactive(self) -> bool:
        """Интерактивное добавление доказательств"""
        if not self.current_hypothesis_id:
            print("Ошибка: сначала создайте гипотезу")
            return False
        
        print("\nШаг 2/5: Добавление доказательств\n")
        print("Введите доказательства в поддержку гипотезы.")
        print("Типы: market_research, user_feedback, competitor_analysis, analytics, expert_opinion, case_study\n")
        
        evidence_count = 0
        while True:
            print(f"\nДоказательство #{evidence_count + 1}")
            evidence_type_str = input("Тип доказательства (или 'готово' для завершения): ").strip().lower()
            
            if evidence_type_str == "готово":
                break
            
            try:
                evidence_type = EvidenceType[evidence_type_str.upper().replace("_", "")]
            except (KeyError, AttributeError):
                print("⚠ Неизвестный тип. Используйте указанные выше.")
                continue
            
            title = input("Название доказательства: ").strip()
            description = input("Описание: ").strip()
            source = input("Источник информации: ").strip()
            supports = input("Поддерживает гипотезу? (да/нет): ").strip().lower() == "да"
            confidence = float(input("Уверенность (0.0-1.0, по умолчанию 0.8): ") or "0.8")
            
            evidence = Evidence(
                evidence_type=evidence_type,
                title=title,
                description=description,
                source=source,
                supports=supports,
                confidence=min(1.0, max(0.0, confidence))
            )
            
            self.manager.add_evidence(self.current_hypothesis_id, evidence)
            evidence_count += 1
            print(f"✓ Доказательство добавлено\n")
        
        print(f"\n✓ Всего добавлено доказательств: {evidence_count}\n")
        return evidence_count > 0
    
    def generate_survey_template(self) -> List[SurveyQuestion]:
        """Генерирует template вопросов для исследования"""
        if not self.current_hypothesis_id:
            return []
        
        print("\nШаг 3/5: Шаблон опроса для валидации\n")
        
        hypothesis = self.manager.get_hypothesis(self.current_hypothesis_id)
        if not hypothesis:
            return []
        
        # Генерируем шаблонные вопросы (в реальной системе - LLM)
        questions = [
            SurveyQuestion(
                question=f"Насколько серьёзна проблема: '{hypothesis.problem_statement}'? (1-10)",
                question_type="rating",
                reasoning="Оценка критичности проблемы для целевой аудитории"
            ),
            SurveyQuestion(
                question=f"Готовы ли вы использовать решение для '{hypothesis.description}'?",
                question_type="multiple_choice",
                options=["Да, сразу же", "Да, но нужно улучшить", "Может быть", "Нет"],
                reasoning="Прямая оценка спроса на решение"
            ),
            SurveyQuestion(
                question="Какие конкурентные решения вы сейчас используете?",
                question_type="open",
                reasoning="Понимание конкурентного ландшафта"
            ),
            SurveyQuestion(
                question="Что должно измениться, чтобы вы переключились на новое решение?",
                question_type="open",
                reasoning="Выявление ключевых критериев успеха"
            )
        ]
        
        for q in questions:
            self.manager.add_survey_question(self.current_hypothesis_id, q)
        
        print(f"✓ Сгенерировано {len(questions)} вопросов для анкетирования\n")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q.question}")
            if q.options:
                for opt in q.options:
                    print(f"     - {opt}")
        
        return questions
    
    def validate_and_score(self) -> Optional[HypothesisScore]:
        """Валидирует гипотезу и выдаёт score"""
        if not self.current_hypothesis_id:
            return None
        
        print("\nШаг 4/5: Валидация и скоринг\n")
        print("Анализирую собранные доказательства...\n")
        
        success, score = self.manager.validate_hypothesis(self.current_hypothesis_id)
        
        if not success or not score:
            return None
        
        # Выводим результаты
        self._print_score_report(score)
        
        return score
    
    def _print_score_report(self, score: HypothesisScore):
        """Форматирует и выводит report по скорингу"""
        print("─" * 70)
        print(f"ИТОГОВЫЙ SCORE: {score.overall_score:.1f}/100")
        print(f"Уровень уверенности: {score.confidence_level.upper()}")
        print(f"Рекомендация: ", end="")
        
        if score.recommendation == "proceed":
            print("✓ ИДТИ В РАЗРАБОТКУ")
        elif score.recommendation == "investigate":
            print("⚠ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНОЕ ИССЛЕДОВАНИЕ")
        else:
            print("✗ ОТКЛОНИТЬ")
        
        print("─" * 70)
        
        print(f"\nПолнота данных: {score.data_completeness*100:.0f}%")
        print(f"Поддерживающих доказательств: {score.supporting_evidence_count}")
        print(f"Противоречащих доказательств: {score.contradicting_evidence_count}")
        
        print("\n📊 Разложение score по факторам:")
        for breakdown in score.breakdown:
            print(f"  • {breakdown.factor.value}: {breakdown.score:.1f}/10")
            print(f"    Обоснование: {breakdown.rationale}")
        
        print()
    
    def record_outcome_interactive(self) -> bool:
        """Интерактивная запись фактического исхода фичи"""
        hypothesis_id = input("ID гипотезы (или Enter для текущей): ").strip()
        if not hypothesis_id:
            hypothesis_id = self.current_hypothesis_id
        
        if not hypothesis_id:
            print("Ошибка: ID гипотезы не задан")
            return False
        
        print("\nШаг 5/5: Запись фактического исхода (постфактум)\n")
        
        was_successful = input("Фича была успешной? (да/нет): ").strip().lower() == "да"
        impact = input("Описание реального воздействия: ").strip()
        lessons = input("Извлечённые уроки: ").strip()
        
        outcome = RealWorldOutcome(
            was_successful=was_successful,
            actual_impact=impact,
            lessons_learned=lessons
        )
        
        success = self.manager.record_outcome(hypothesis_id, outcome)
        
        if success:
            print("\n✓ Исход записан. Спасибо за обратную связь!\n")
        
        return success
    
    def show_correlation_analysis(self):
        """Показывает анализ корреляции score ↔ реальный успех"""
        print("\n📈 АНАЛИЗ КОРРЕЛЯЦИИ (Цель 3 ТЗ)\n")
        
        analysis = self.manager.get_correlation_analysis()
        
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    
    def interactive_session(self):
        """Запускает интерактивную сессию"""
        while True:
            print("\n" + "="*70)
            print("МЕНЮ")
            print("="*70)
            print("1. Создать новую гипотезу")
            print("2. Добавить доказательства")
            print("3. Сгенерировать шаблон опроса")
            print("4. Валидировать и получить score")
            print("5. Записать исход фичи (постфактум)")
            print("6. Анализ корреляции score ↔ успех")
            print("7. Экспортировать гипотезу (JSON)")
            print("8. Список всех гипотез")
            print("0. Выход")
            print("="*70)
            
            choice = input("Выберите опцию: ").strip()
            
            if choice == "1":
                self.start_new_hypothesis()
            elif choice == "2":
                self.add_evidence_interactive()
            elif choice == "3":
                self.generate_survey_template()
            elif choice == "4":
                self.validate_and_score()
            elif choice == "5":
                self.record_outcome_interactive()
            elif choice == "6":
                self.show_correlation_analysis()
            elif choice == "7":
                if self.current_hypothesis_id:
                    data = self.manager.export_hypothesis(self.current_hypothesis_id)
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                else:
                    print("Ошибка: гипотеза не выбрана")
            elif choice == "8":
                hypotheses = self.manager.list_hypotheses()
                print(f"\nВсего гипотез: {len(hypotheses)}\n")
                for h in hypotheses:
                    status_icon = "✓" if h.status == HypothesisStatus.VALIDATED else "○"
                    score_str = f" (score: {h.score.overall_score:.0f})" if h.score else ""
                    print(f"  {status_icon} [{h.id[:8]}...] {h.title}{score_str}")
            elif choice == "0":
                print("\nСпасибо за использование Product Hypothesis Assistant!\n")
                break
            else:
                print("⚠ Неизвестная опция")


# ============================================================================
# 6. MAIN: Точка входа
# ============================================================================

def main():
    """Запускает приложение"""
    assistant = HypothesisAssistant()
    assistant.interactive_session()


if __name__ == "__main__":
    main()
