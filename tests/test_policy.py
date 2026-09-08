from app.policy import PolicyEngine, PolicyRequest



def test_policy_allows_in_scope_passive_probe() -> None:
    engine = PolicyEngine()
    result = engine.evaluate(
        PolicyRequest(
            campaign_id=1,
            action="http_probe",
            target="https://api.example.local/v1/health",
            in_scope_hosts={"api.example.local"},
            excluded_hosts=set(),
            research_mode="passive",
            emergency_stop_active=False,
            total_requests_so_far=0,
            max_total_requests=10,
        )
    )
    assert result.allowed is True



def test_policy_blocks_out_of_scope_target() -> None:
    engine = PolicyEngine()
    result = engine.evaluate(
        PolicyRequest(
            campaign_id=1,
            action="http_probe",
            target="https://admin.example.com/",
            in_scope_hosts={"api.example.local"},
            excluded_hosts=set(),
            research_mode="passive",
            emergency_stop_active=False,
            total_requests_so_far=0,
            max_total_requests=10,
        )
    )
    assert result.allowed is False



def test_policy_blocks_active_action_in_passive_mode() -> None:
    engine = PolicyEngine()
    result = engine.evaluate(
        PolicyRequest(
            campaign_id=1,
            action="idor_check",
            target="https://api.example.local/v1/resource/1",
            in_scope_hosts={"api.example.local"},
            excluded_hosts=set(),
            research_mode="passive",
            emergency_stop_active=False,
            total_requests_so_far=0,
            max_total_requests=10,
        )
    )
    assert result.allowed is False
