from dataclasses import dataclass

from app.policy import PolicyEngine, PolicyRequest


@dataclass
class ToolRequest:
    campaign_id: str
    action: str
    target: str
    in_scope_hosts: set[str]


@dataclass
class ToolResult:
    ok: bool
    message: str


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
            )
        )
        if not decision.allowed:
            return ToolResult(False, f"blocked by policy: {decision.reason}")
        # Placeholder for approved wrappers only.
        return ToolResult(True, "executed with bounded safe wrapper")
