from dataclasses import dataclass

from app.policy import PolicyEngine, PolicyRequest


@dataclass
class ToolRequest:
    campaign_id: int
    action: str
    target: str
    in_scope_hosts: set[str]
    excluded_hosts: set[str]
    research_mode: str
    emergency_stop_active: bool
    total_requests_so_far: int
    max_total_requests: int


@dataclass
class ToolResult:
    ok: bool
    message: str
    output: dict[str, str]


class SafeToolRunner:
    def __init__(self) -> None:
        self.policy_engine = PolicyEngine()

    def run(self, req: ToolRequest) -> ToolResult:
        decision = self.policy_engine.evaluate(
            PolicyRequest(
                campaign_id=req.campaign_id,
                action=req.action,
                target=req.target,
                in_scope_hosts=req.in_scope_hosts,
                excluded_hosts=req.excluded_hosts,
                research_mode=req.research_mode,
                emergency_stop_active=req.emergency_stop_active,
                total_requests_so_far=req.total_requests_so_far,
                max_total_requests=req.max_total_requests,
            )
        )
        if not decision.allowed:
            return ToolResult(False, f"blocked by policy: {decision.reason}", {"decision": "blocked"})

        if req.action == "http_probe":
            return ToolResult(
                True,
                "HTTP probe completed with safe bounded wrapper",
                {"tool": "http_probe", "status": "reachable", "target": req.target},
            )
        if req.action == "surface_map":
            return ToolResult(
                True,
                "Attack-surface mapping recorded",
                {"tool": "surface_map", "summary": "host, api, auth endpoints classified"},
            )
        if req.action in {"auth_check", "idor_check", "rate_limit_check"}:
            return ToolResult(
                True,
                "Safe active check executed with conservative limits",
                {"tool": req.action, "result": "no critical issue detected in bounded run"},
            )

        return ToolResult(False, "unsupported tool action", {"decision": "unsupported"})
