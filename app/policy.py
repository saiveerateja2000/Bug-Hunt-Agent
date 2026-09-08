from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class PolicyRequest:
    campaign_id: str
    action: str
    target: str
    in_scope_hosts: set[str]
    excluded_prefixes: tuple[str, ...] = ()


@dataclass
class PolicyResult:
    allowed: bool
    reason: str


class PolicyEngine:
    def evaluate(self, req: PolicyRequest) -> PolicyResult:
        parsed = urlparse(req.target)
        host = parsed.hostname
        if not host:
            return PolicyResult(False, "Target must include a valid host")
        if host not in req.in_scope_hosts:
            return PolicyResult(False, "Target host is out of scope")
        for excluded in req.excluded_prefixes:
            if req.target.startswith(excluded):
                return PolicyResult(False, "Target path is explicitly excluded")
        return PolicyResult(True, "Allowed: target is in scope")
