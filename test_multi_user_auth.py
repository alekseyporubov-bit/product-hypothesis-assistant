#!/usr/bin/env python3
"""
Критические сценарии многопользовательской работы и авторизации через Google.

Проверяет (Red -> Green по TDPD):
1) у гипотезы есть поле user_id, оно сохраняется в словаре;
2) менеджер изолирует данные по пользователям (list/get/add/validate/
   record/export/scan/correlation);
3) «сиротские» гипотезы (user_id="") привязываются к первому пользователю;
4) JIT-создание учётной записи через Google (UserManager);
5) HTTP-уровень: неавторизованный запрос к /api/* возвращает 401,
   а авторизованный видит только свои гипотезы.

Запуск (без БД — в памяти):
    python3 test_multi_user_auth.py
"""

import sys

from product_hypothesis_assistant import (
    HypothesisManager,
    Evidence,
    EvidenceType,
    RealWorldOutcome,
)

try:
    from auth import UserManager
    _AUTH_AVAILABLE = True
except Exception:
    _AUTH_AVAILABLE = False

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL"), "-", name,
          ("| " + str(detail)[:160] if detail else ""))


def _manager():
    return HypothesisManager()


def test_hypothesis_has_user_id():
    m = _manager()
    h = m.create_hypothesis("T", "d", "p", "u", "e", user_id="user-1")
    check("create_hypothesis принимает user_id", h.user_id == "user-1", h.user_id)
    check("user_id попадает в to_dict", h.to_dict().get("user_id") == "user-1")

    legacy = m.create_hypothesis("T2", "d", "p", "u", "e")
    check("гипотеза без user_id получает пустое значение", legacy.user_id == "")


def test_list_scoped():
    m = _manager()
    a = m.create_hypothesis("A", "d", "p", "u", "e", user_id="u-a")
    b = m.create_hypothesis("B", "d", "p", "u", "e", user_id="u-b")

    ids_a = [h.id for h in m.list_hypotheses(user_id="u-a")]
    check("list_hypotheses(user_id=u-a) содержит только A",
          a.id in ids_a and b.id not in ids_a)

    check("list_hypotheses() без фильтра возвращает все",
          len(m.list_hypotheses()) == 2)


def test_get_scoped():
    m = _manager()
    a = m.create_hypothesis("A", "d", "p", "u", "e", user_id="u-a")
    check("владелец видит свою гипотезу",
          m.get_hypothesis(a.id, user_id="u-a") is not None)
    check("чужой пользователь НЕ видит гипотезу",
          m.get_hypothesis(a.id, user_id="u-b") is None)
    check("без фильтра (обратная совместимость) гипотеза доступна",
          m.get_hypothesis(a.id) is not None)


def test_mutation_scoped():
    m = _manager()
    a = m.create_hypothesis("A", "d", "p", "u", "e", user_id="u-a")

    ev = Evidence(
        evidence_type=EvidenceType.USER_FEEDBACK,
        title="ev", description="d", source="s",
        confidence=0.8, supports=True,
    )
    check("владелец может добавить доказательство",
          m.add_evidence(a.id, ev, user_id="u-a") is True)
    check("чужой НЕ может добавить доказательство",
          m.add_evidence(a.id, ev, user_id="u-b") is False)

    check("чужой НЕ может валидировать",
          m.validate_hypothesis(a.id, user_id="u-b") == (False, None))
    ok, _ = m.validate_hypothesis(a.id, user_id="u-a")
    check("владелец может валидировать", ok is True)

    outcome = RealWorldOutcome(was_successful=True, actual_impact="ok")
    check("чужой НЕ может записать исход",
          m.record_outcome(a.id, outcome, user_id="u-b") is False)
    check("владелец может записать исход",
          m.record_outcome(a.id, outcome, user_id="u-a") is True)

    check("чужой НЕ может экспортировать",
          m.export_hypothesis(a.id, user_id="u-b") is None)
    check("владелец может экспортировать",
          m.export_hypothesis(a.id, user_id="u-a") is not None)

    scan_other = m.scan_auto_research(a.id, user_id="u-b")
    check("чужой НЕ может сканировать исследования",
          scan_other.get("success") is False)
    scan_owner = m.scan_auto_research(a.id, user_id="u-a")
    check("владелец может сканировать исследования",
          scan_owner.get("success") is True)


def test_correlation_scoped():
    m = _manager()
    a = m.create_hypothesis("A", "d", "p", "u", "e", user_id="u-a")
    m.add_evidence(a.id, Evidence(
        evidence_type=EvidenceType.USER_FEEDBACK,
        title="ev", description="d", source="s", confidence=0.9, supports=True,
    ), user_id="u-a")
    m.validate_hypothesis(a.id, user_id="u-a")
    m.record_outcome(a.id, RealWorldOutcome(was_successful=True), user_id="u-a")

    analysis_a = m.get_correlation_analysis(user_id="u-a")
    analysis_b = m.get_correlation_analysis(user_id="u-b")
    check("корреляция считается только по своим гипотезам",
          analysis_a.get("status") != "insufficient_data"
          and analysis_b.get("status") == "insufficient_data")


def test_claim_orphaned():
    m = _manager()
    legacy = m.create_hypothesis("Legacy", "d", "p", "u", "e")  # user_id=""
    own = m.create_hypothesis("Own", "d", "p", "u", "e", user_id="u-a")

    count = m.claim_orphaned_hypotheses("u-a")
    check("claim_orphaned_hypotheses вернул 1 сироту", count == 1, count)
    check("сирота привязана к первому пользователю", legacy.user_id == "u-a")
    check("сирота видна первому пользователю",
          m.get_hypothesis(legacy.id, user_id="u-a") is not None)
    check("своя гипотеза не задета", own.user_id == "u-a")


def test_user_manager_jit():
    if not _AUTH_AVAILABLE:
        check("UserManager доступен (auth.py)", False, "auth.py не найден")
        return
    um = UserManager()
    u1, created1, first1 = um.ensure_user("sub-1", "a@example.com", "Alice", "")
    check("первый вход создаёт учётку (JIT)", created1 is True and first1 is True)

    u2, created2, first2 = um.ensure_user("sub-1", "a@example.com", "Alice", "")
    check("повторный вход находит существующую учётку",
          created2 is False and first2 is False and u2.id == u1.id)

    u3, created3, first3 = um.ensure_user("sub-2", "b@example.com", "Bob", "")
    check("второй пользователь создаётся, но не первый",
          created3 is True and first3 is False)

    check("get_user возвращает учётку", um.get_user(u1.id) is not None)


def test_flask_auth_gating():
    try:
        import app as app_module
    except Exception as e:
        check("app импортируется", False, repr(e))
        return

    client = app_module.app.test_client()

    r = client.get("/api/list-hypotheses")
    check("неавторизованный GET /api/list-hypotheses -> 401",
          r.status_code == 401, r.status_code)

    r = client.get("/api/auth/status")
    data = r.get_json()
    check("/api/auth/status без сессии -> authenticated=false",
          data is not None and data.get("authenticated") is False)

    m = app_module.manager
    h_own = m.create_hypothesis("X", "d", "p", "u", "e", user_id="user-x")
    h_other = m.create_hypothesis("Y", "d", "p", "u", "e", user_id="user-y")

    with client.session_transaction() as sess:
        sess["user_id"] = "user-x"

    r = client.get("/api/list-hypotheses")
    ids = [hh["id"] for hh in r.get_json()["hypotheses"]]
    check("авторизованный видит только свои гипотезы",
          h_own.id in ids and h_other.id not in ids)


def main() -> int:
    test_hypothesis_has_user_id()
    test_list_scoped()
    test_get_scoped()
    test_mutation_scoped()
    test_correlation_scoped()
    test_claim_orphaned()
    test_user_manager_jit()
    test_flask_auth_gating()

    failed = [n for n, ok in results if not ok]
    print("\n" + "=" * 70)
    print("ИТОГ: %d/%d пройдено" % (len(results) - len(failed), len(results)))
    if failed:
        print("ПРОВАЛЕНЫ:")
        for n in failed:
            print("  -", n)
        return 1
    print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
    return 0


if __name__ == "__main__":
    sys.exit(main())

