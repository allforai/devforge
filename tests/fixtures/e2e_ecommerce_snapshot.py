# tests/fixtures/e2e_ecommerce_snapshot.py
"""Factory for e-commerce e2e scenario snapshot."""

from __future__ import annotations


def make_ecommerce_snapshot(
    *,
    with_failures: bool = False,
    with_requirement_change: bool = False,
) -> dict:
    """Build a complete e-commerce snapshot for S1 scenario testing."""
    initiative = {
        "initiative_id": "ecom-001",
        "name": "二手交易平台",
        "goal": "面向年轻人的二手交易平台，有社区感",
        "status": "active",
        "project_ids": ["ecom-main"],
        "shared_concepts": [],
        "shared_contracts": [],
        "initiative_memory_ref": "memory://initiative/ecom-001",
        "global_acceptance_goals": [
            "购买流程端到端可用",
            "搜索结果体现社区信号",
            "管理后台可审核订单",
        ],
        "requirement_event_ids": [],
        "scheduler_state": {},
    }

    project = {
        "project_id": "ecom-main",
        "initiative_id": "ecom-001",
        "parent_project_id": None,
        "name": "二手交易平台",
        "kind": "fullstack",
        "status": "active",
        "current_phase": "implementation",
        "project_archetype": "ecommerce",
        "domains": ["用户", "商品", "交易", "支付", "互动", "管理"],
        "active_roles": ["product_manager", "software_engineer", "qa_engineer"],
        "concept_model_refs": [],
        "contracts": [],
        "executor_policy_ref": "policy://ecom-default",
        "work_package_ids": [
            "wp-auth", "wp-catalog", "wp-search", "wp-cart", "wp-order",
            "wp-payment", "wp-review", "wp-admin",
        ],
        "seam_ids": ["seam-order-payment"],
        "project_memory_ref": "memory://project/ecom-main",
        "assumptions": [],
        "requirement_events": [],
        "children": [],
        "coordination_project": False,
    }

    base_wp = {
        "initiative_id": "ecom-001",
        "project_id": "ecom-main",
        "phase": "implementation",
        "role_id": "software_engineer",
        "executor": "claude_code",
        "fallback_executors": ["codex"],
        "inputs": [],
        "constraints": [],
        "assumptions": [],
        "artifacts_created": [],
        "findings": [],
        "handoff_notes": [],
        "last_execution_ref": {},
        "execution_history": [],
        "attempt_count": 0,
        "max_attempts": 3,
        "derivation_ring": 0,
        "backfill_source": None,
    }

    work_packages = [
        {**base_wp, "work_package_id": "wp-auth", "domain": "用户", "title": "用户认证", "goal": "实现注册登录", "status": "verified", "priority": 90, "deliverables": ["auth.py"], "acceptance_criteria": ["能注册", "能登录"], "depends_on": [], "blocks": ["wp-catalog", "wp-admin"], "related_seams": []},
        {**base_wp, "work_package_id": "wp-catalog", "domain": "商品", "title": "商品管理", "goal": "实现商品发布和列表", "status": "ready", "priority": 80, "deliverables": ["catalog.py"], "acceptance_criteria": ["能发布商品", "能查看列表"], "depends_on": ["wp-auth"], "blocks": ["wp-search", "wp-cart"], "related_seams": []},
        {**base_wp, "work_package_id": "wp-search", "domain": "商品", "title": "搜索", "goal": "实现商品搜索和排序", "status": "ready", "priority": 70, "deliverables": ["search.py"], "acceptance_criteria": ["能搜索", "结果排序"], "depends_on": ["wp-catalog"], "blocks": [], "related_seams": []},
        {**base_wp, "work_package_id": "wp-cart", "domain": "交易", "title": "购物车", "goal": "实现加购和购物车管理", "status": "ready", "priority": 75, "deliverables": ["cart.py"], "acceptance_criteria": ["能加购", "能删除", "能修改数量"], "depends_on": ["wp-catalog"], "blocks": ["wp-order"], "related_seams": []},
        {**base_wp, "work_package_id": "wp-order", "domain": "交易", "title": "订单", "goal": "实现下单和订单管理", "status": "ready", "priority": 85, "deliverables": ["order.py"], "acceptance_criteria": ["能下单", "能查看订单"], "depends_on": ["wp-cart"], "blocks": ["wp-payment"], "related_seams": ["seam-order-payment"]},
        {**base_wp, "work_package_id": "wp-payment", "domain": "支付", "title": "支付", "goal": "实现支付处理", "status": "ready" if not with_failures else "failed", "priority": 90, "deliverables": ["payment.py"], "acceptance_criteria": ["支付幂等", "支持微信支付"], "depends_on": ["wp-order"], "blocks": ["wp-review"], "related_seams": ["seam-order-payment"]},
        {**base_wp, "work_package_id": "wp-review", "domain": "互动", "title": "评价", "goal": "实现评价和社区互动", "status": "ready", "priority": 60, "deliverables": ["review.py"], "acceptance_criteria": ["能评价", "能回复"], "depends_on": ["wp-payment"], "blocks": [], "related_seams": []},
        {**base_wp, "work_package_id": "wp-admin", "domain": "管理", "title": "管理后台", "goal": "实现管理后台", "status": "ready", "priority": 50, "deliverables": ["admin.py"], "acceptance_criteria": ["能审核订单", "能管理用户"], "depends_on": ["wp-auth"], "blocks": [], "related_seams": []},
    ]

    if with_failures:
        work_packages[5]["status"] = "failed"
        work_packages[5]["attempt_count"] = 1
        work_packages[5]["findings"] = [{"id": "F-1", "summary": "支付模块超时", "severity": "high", "source": "codex", "details": "", "related_artifacts": []}]
        work_packages[5]["handoff_notes"] = ["codex执行超时"]

    seams = [
        {
            "seam_id": "seam-order-payment",
            "initiative_id": "ecom-001",
            "source_project_id": "ecom-main",
            "target_project_id": "ecom-main",
            "type": "api",
            "name": "订单-支付接口",
            "status": "frozen",
            "contract_version": "v1",
            "owner_role_id": "technical_architect",
            "owner_executor": "claude_code",
            "artifacts": ["order-payment-contract.json"],
            "acceptance_criteria": ["订单ID传递正确", "支付状态回调正确", "幂等性保证"],
            "risks": [],
            "related_work_packages": ["wp-order", "wp-payment"],
            "change_log": [{"version": "v1", "summary": "initial contract"}],
            "verification_refs": [],
        },
    ]

    executor_policies = [
        {
            "policy_id": "ecom-default",
            "default": "claude_code",
            "by_phase": {"implementation": "claude_code", "testing": "codex"},
            "by_role": {},
            "by_domain": {"管理": "codex"},
            "by_work_package": {},
            "fallback_order": ["claude_code", "codex", "python"],
            "rules": [],
        },
    ]

    requirement_events = []
    if with_requirement_change:
        requirement_events.append({
            "requirement_event_id": "req-coupon",
            "initiative_id": "ecom-001",
            "project_ids": ["ecom-main"],
            "type": "add",
            "summary": "新增优惠券功能",
            "details": "用户下单时可使用优惠券",
            "source": "user",
            "impact_level": "medium",
            "affected_domains": ["交易", "支付"],
            "affected_work_packages": ["wp-order", "wp-payment"],
            "affected_seams": ["seam-order-payment"],
            "patch_status": "recorded",
            "created_at": "2026-04-02T15:00:00Z",
            "applied_at": None,
        })

    return {
        "initiative": initiative,
        "projects": [project],
        "work_packages": work_packages,
        "seams": seams,
        "executor_policies": executor_policies,
        "requirement_events": requirement_events,
    }
