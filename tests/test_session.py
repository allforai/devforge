from devforge.session import RunRecord, SessionState, TransitionLogEntry, UserIntent, ViewState


def test_session_protocol_models_are_constructible() -> None:
    session = SessionState(
        session_id="session-1",
        project_id="flydict",
        active_phase="analysis_design",
        active_feature="offline favorites",
        mode="waiting_user",
    )
    run = RunRecord(
        run_id="run-21",
        executor="claude_code",
        title="Analyze iOS cache boundary",
        status="running",
        trigger_ref="node:offline-favorites@v1",
    )
    view = ViewState(focus="attached", attached_run_id=run.run_id)
    intent = UserIntent(kind="continue_cycle")
    transition = TransitionLogEntry(
        transition_id="tx-1",
        object_type="run",
        object_id=run.run_id,
        before="queued",
        after="running",
        reason="seam analysis triggered by blocked node",
    )

    assert session.mode == "waiting_user"
    assert run.executor == "claude_code"
    assert view.attached_run_id == "run-21"
    assert intent.kind == "continue_cycle"
    assert transition.after == "running"
