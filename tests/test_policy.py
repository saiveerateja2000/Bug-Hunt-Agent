from app.policy import PolicyEngine, PolicyRequest


def test_policy_allows_in_scope_target() -> None:
    engine = PolicyEngine()
    result = engine.evaluate(
        PolicyRequest(
            campaign_id="c1",
            action="probe",
            target="https://api.example.local/v1/health",
            in_scope_hosts={"api.example.local"},
        )
    )
    assert result.allowed is True


def test_policy_blocks_out_of_scope_target() -> None:
    engine = PolicyEngine()
    result = engine.evaluate(
        PolicyRequest(
            campaign_id="c1",
            action="probe",
            target="https://admin.example.com/",
            in_scope_hosts={"api.example.local"},
        )
    )
    assert result.allowed is False
