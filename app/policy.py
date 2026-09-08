from dataclasses import dataclass
from urllib.parse import urlparse


PASSIVE_ONLY_ACTIONS = {"passive_recon", "http_probe", "surface_map"}
SAFE_ACTIVE_ACTIONS = {"auth_check", "idor_check", "rate_limit_check"}


@dataclass
class PolicyRequest:
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
class PolicyResult:
    allowed: bool
    reason: str


class PolicyEngine:
    def evaluate(self, req: PolicyRequest) -> PolicyResult:
        if req.emergency_stop_active:
            return PolicyResult(False, "Emergency stop is active")
        if req.total_requests_so_far >= req.max_total_requests:
            return PolicyResult(False, "Campaign request budget exceeded")

        parsed = urlparse(req.target)
        host = parsed.hostname
        if parsed.scheme not in {"http", "https"} or not host:
            return PolicyResult(False, "Target must be a valid http(s) URL")
        if host in req.excluded_hosts:
            return PolicyResult(False, "Target host is explicitly excluded")
        if host not in req.in_scope_hosts:
            return PolicyResult(False, "Target host is out of scope")

        action = req.action.strip().lower()
        mode = req.research_mode.strip().lower()
        if mode == "passive" and action not in PASSIVE_ONLY_ACTIONS:
            return PolicyResult(False, "Passive mode blocks active security checks")
        if mode == "safe_active" and action not in PASSIVE_ONLY_ACTIONS.union(SAFE_ACTIVE_ACTIONS):
            return PolicyResult(False, "Action is not allowed in safe-active mode")

        return PolicyResult(True, "Allowed by policy")
