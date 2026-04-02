# tests/fixtures/e2e_game_snapshot.py
"""Factory for game e2e scenario snapshot."""

from __future__ import annotations


def make_game_snapshot(
    *,
    with_project_split: bool = False,
    with_seam_broken: bool = False,
    with_requirement_change: bool = False,
) -> dict:
    """Build a complete game snapshot for S2 scenario testing."""
    initiative = {
        "initiative_id": "game-001",
        "name": "Roguelike地牢探索",
        "goal": "roguelike地牢探索游戏，随机地图、怪物战斗、装备掉落、角色成长、2-4人合作",
        "status": "active",
        "project_ids": ["game-main"] if not with_project_split else ["game-main", "game-singleplayer", "game-multiplayer"],
        "shared_concepts": [],
        "shared_contracts": [],
        "initiative_memory_ref": "memory://initiative/game-001",
        "global_acceptance_goals": [
            "核心探索循环可玩",
            "战斗系统有反馈",
            "多人合作流畅",
        ],
        "requirement_event_ids": [],
        "scheduler_state": {},
    }

    base_wp = {
        "initiative_id": "game-001",
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

    if not with_project_split:
        projects = [{
            "project_id": "game-main",
            "initiative_id": "game-001",
            "parent_project_id": None,
            "name": "Roguelike地牢",
            "kind": "game",
            "status": "active",
            "current_phase": "implementation",
            "project_archetype": "gaming",
            "domains": ["地图", "战斗", "经济", "成长", "多人"],
            "active_roles": ["software_engineer", "qa_engineer"],
            "concept_model_refs": [],
            "contracts": [],
            "executor_policy_ref": "policy://game-default",
            "work_package_ids": ["wp-map", "wp-combat", "wp-loot", "wp-growth", "wp-multiplayer"],
            "seam_ids": [],
            "project_memory_ref": "memory://project/game-main",
            "assumptions": [],
            "requirement_events": [],
            "children": [],
            "coordination_project": False,
        }]
        work_packages = [
            {**base_wp, "work_package_id": "wp-map", "project_id": "game-main", "domain": "地图", "title": "地图生成", "goal": "随机地牢地图生成", "status": "ready", "priority": 90, "deliverables": ["map_gen.py"], "acceptance_criteria": ["随机种子可控", "地图连通"], "depends_on": [], "blocks": ["wp-combat"], "related_seams": []},
            {**base_wp, "work_package_id": "wp-combat", "project_id": "game-main", "domain": "战斗", "title": "战斗系统", "goal": "实现回合制战斗", "status": "ready", "priority": 85, "deliverables": ["combat.py"], "acceptance_criteria": ["伤害计算正确", "状态效果生效"], "depends_on": ["wp-map"], "blocks": ["wp-loot"], "related_seams": []},
            {**base_wp, "work_package_id": "wp-loot", "project_id": "game-main", "domain": "经济", "title": "装备掉落", "goal": "实现装备掉落和拾取", "status": "ready", "priority": 70, "deliverables": ["loot.py"], "acceptance_criteria": ["掉落概率可配", "品质分级"], "depends_on": ["wp-combat"], "blocks": [], "related_seams": []},
            {**base_wp, "work_package_id": "wp-growth", "project_id": "game-main", "domain": "成长", "title": "角色成长", "goal": "实现经验和升级", "status": "ready", "priority": 65, "deliverables": ["growth.py"], "acceptance_criteria": ["经验值计算", "属性成长"], "depends_on": [], "blocks": [], "related_seams": []},
            {**base_wp, "work_package_id": "wp-multiplayer", "project_id": "game-main", "domain": "多人", "title": "多人同步", "goal": "实现2-4人在线合作", "status": "ready", "priority": 80, "deliverables": ["multiplayer.py"], "acceptance_criteria": ["状态同步", "延迟补偿"], "depends_on": ["wp-combat"], "blocks": [], "related_seams": []},
        ]
        seams = []
    else:
        projects = [
            {"project_id": "game-main", "initiative_id": "game-001", "parent_project_id": None, "name": "Roguelike地牢", "kind": "game", "status": "split_done", "current_phase": "implementation", "project_archetype": "gaming", "domains": [], "active_roles": [], "concept_model_refs": [], "contracts": [], "executor_policy_ref": "policy://game-default", "work_package_ids": [], "seam_ids": ["seam-sp-mp"], "project_memory_ref": "", "assumptions": [], "requirement_events": [], "children": ["game-singleplayer", "game-multiplayer"], "coordination_project": True},
            {"project_id": "game-singleplayer", "initiative_id": "game-001", "parent_project_id": "game-main", "name": "单机核心", "kind": "game", "status": "active", "current_phase": "implementation", "project_archetype": "gaming", "domains": ["地图", "战斗", "经济", "成长"], "active_roles": ["software_engineer"], "concept_model_refs": [], "contracts": [], "executor_policy_ref": "policy://game-default", "work_package_ids": ["wp-map", "wp-combat", "wp-loot", "wp-growth"], "seam_ids": ["seam-sp-mp"], "project_memory_ref": "", "assumptions": [], "requirement_events": [], "children": [], "coordination_project": False},
            {"project_id": "game-multiplayer", "initiative_id": "game-001", "parent_project_id": "game-main", "name": "多人联机", "kind": "game", "status": "active", "current_phase": "implementation", "project_archetype": "gaming", "domains": ["多人", "网络"], "active_roles": ["software_engineer"], "concept_model_refs": [], "contracts": [], "executor_policy_ref": "policy://game-default", "work_package_ids": ["wp-multiplayer", "wp-network"], "seam_ids": ["seam-sp-mp"], "project_memory_ref": "", "assumptions": [], "requirement_events": [], "children": [], "coordination_project": False},
        ]
        work_packages = [
            {**base_wp, "work_package_id": "wp-map", "project_id": "game-singleplayer", "domain": "地图", "title": "地图生成", "goal": "随机地图", "status": "ready", "priority": 90, "deliverables": ["map_gen.py"], "acceptance_criteria": ["连通"], "depends_on": [], "blocks": ["wp-combat"], "related_seams": []},
            {**base_wp, "work_package_id": "wp-combat", "project_id": "game-singleplayer", "domain": "战斗", "title": "战斗", "goal": "战斗系统", "status": "ready", "priority": 85, "deliverables": ["combat.py"], "acceptance_criteria": ["伤害正确"], "depends_on": ["wp-map"], "blocks": [], "related_seams": ["seam-sp-mp"]},
            {**base_wp, "work_package_id": "wp-loot", "project_id": "game-singleplayer", "domain": "经济", "title": "掉落", "goal": "装备掉落", "status": "ready", "priority": 70, "deliverables": ["loot.py"], "acceptance_criteria": ["概率可配"], "depends_on": ["wp-combat"], "blocks": [], "related_seams": []},
            {**base_wp, "work_package_id": "wp-growth", "project_id": "game-singleplayer", "domain": "成长", "title": "成长", "goal": "角色升级", "status": "ready", "priority": 65, "deliverables": ["growth.py"], "acceptance_criteria": ["经验正确"], "depends_on": [], "blocks": [], "related_seams": []},
            {**base_wp, "work_package_id": "wp-multiplayer", "project_id": "game-multiplayer", "domain": "多人", "title": "同步", "goal": "状态同步", "status": "ready", "priority": 80, "deliverables": ["sync.py"], "acceptance_criteria": ["同步正确"], "depends_on": [], "blocks": [], "related_seams": ["seam-sp-mp"]},
            {**base_wp, "work_package_id": "wp-network", "project_id": "game-multiplayer", "domain": "网络", "title": "网络层", "goal": "传输层", "status": "ready", "priority": 75, "deliverables": ["network.py"], "acceptance_criteria": ["延迟低"], "depends_on": [], "blocks": ["wp-multiplayer"], "related_seams": []},
        ]
        seam_status = "broken" if with_seam_broken else "frozen"
        seams = [{
            "seam_id": "seam-sp-mp",
            "initiative_id": "game-001",
            "source_project_id": "game-singleplayer",
            "target_project_id": "game-multiplayer",
            "type": "api",
            "name": "单机-联机接缝",
            "status": seam_status,
            "contract_version": "v1",
            "owner_role_id": "technical_architect",
            "owner_executor": "claude_code",
            "artifacts": ["game-state-sync-contract.json"],
            "acceptance_criteria": ["战斗事件格式一致", "状态同步协议匹配"],
            "risks": [],
            "related_work_packages": ["wp-combat", "wp-multiplayer"],
            "change_log": [{"version": "v1", "summary": "initial"}],
            "verification_refs": [],
        }]

    executor_policies = [{
        "policy_id": "game-default",
        "default": "claude_code",
        "by_phase": {},
        "by_role": {},
        "by_domain": {},
        "by_work_package": {},
        "fallback_order": ["claude_code", "codex"],
        "rules": [],
    }]

    requirement_events = []
    if with_requirement_change:
        requirement_events.append({
            "requirement_event_id": "req-pvp",
            "initiative_id": "game-001",
            "project_ids": ["game-singleplayer", "game-multiplayer"] if with_project_split else ["game-main"],
            "type": "add",
            "summary": "新增PvP竞技场模式",
            "details": "支持1v1 PvP对战",
            "source": "user",
            "impact_level": "high",
            "affected_domains": ["战斗", "多人"],
            "affected_work_packages": ["wp-combat", "wp-multiplayer"],
            "affected_seams": ["seam-sp-mp"] if with_project_split else [],
            "patch_status": "recorded",
            "created_at": "2026-04-02T16:00:00Z",
            "applied_at": None,
        })

    return {
        "initiative": initiative,
        "projects": projects,
        "work_packages": work_packages,
        "seams": seams,
        "executor_policies": executor_policies,
        "requirement_events": requirement_events,
    }
