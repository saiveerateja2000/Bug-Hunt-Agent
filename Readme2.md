# Product Build Prompt: Local Autonomous Bug-Bounty Research Platform

## Mission

Design and build a local-first AI-powered security research application that discovers legitimate bug-bounty programs, evaluates available opportunities, understands each target's business model and attack surface, creates a target-specific hunt plan, performs bounded authorized security testing, identifies and validates potential vulnerabilities, categorizes findings by confidence and priority, and generates detailed reports for human review.

The product must support both:

1. Autonomous, policy-controlled bug-bounty research.
2. Manual hunting by the researcher, with the application providing scope, intelligence, checklists, evidence capture, validation, prioritization, and reporting support.

The application must never be an unrestricted hacking tool. It may test only explicitly authorized programs and in-scope assets, following the rules published on the applicable program page.

## Operating assumptions

- The first version runs locally on the researcher's computer.
- Platform selection is dynamic and depends on the availability of legitimate, active programs.
- Initially prioritize HackerOne, Bugcrowd, Intigriti, YesWeHack, Immunefi, and official company security-reward pages.
- The application must verify whether each program is active, legitimate, in scope, and accepting submissions before adding it to the hunt queue.
- Program rules are authoritative and override the application's default behavior.
- The user wants to find and categorize vulnerabilities first; bounty submission and workflow decisions can be added later.
- Logs, evidence, reports, and historical program data may be retained locally for a long period, subject to configurable storage and privacy controls.

## End-to-end workflow

```text
Discover programs
  -> verify source and current status
  -> import program rules and scope
  -> remove excluded or unsafe targets
  -> rank opportunities
  -> select a campaign
  -> classify business model and attack surface
  -> generate a hunt plan
  -> perform passive reconnaissance
  -> request or apply the correct testing permission
  -> run bounded authorized checks
  -> monitor safety and target impact
  -> stop, pause, or escalate when required
  -> validate possible findings
  -> deduplicate and categorize findings
  -> perform risk analysis
  -> generate detailed report
  -> prepare manual follow-up and evidence package
```

## Module 1: Program discovery and verification

Collect program information from permitted APIs, feeds, public directories, or official pages. Do not violate platform terms through uncontrolled scraping.

Initial source priority:

- HackerOne
- Bugcrowd
- Intigriti
- YesWeHack
- Immunefi for blockchain and DeFi programs
- Official security-reward and vulnerability-disclosure pages

Store the following for every program:

- Company and program name
- Source platform and canonical URL
- Program type: bounty, private bounty, or disclosure program
- Current active or paused status
- Reward range and reward categories
- In-scope domains, APIs, mobile apps, repositories, contracts, or other assets
- Out-of-scope assets and vulnerability classes
- Authentication and test-account rules
- Rate limits and testing windows
- Safe-harbor and legal language
- Prohibited actions
- Disclosure and duplicate-report policy
- Researcher eligibility
- Expected response times
- Last update timestamp
- Source-verification timestamp
- Program-data confidence

The verifier must flag stale, contradictory, incomplete, or ambiguous rules. Ambiguous programs must be placed in a review queue and must not be tested automatically.

## Module 2: Opportunity scoring and categorization

Rank programs and assets by estimated opportunity, not guaranteed payout. The scoring system must be explainable and configurable.

Use factors such as:

- Scope clarity
- Program activity and freshness
- Reward potential
- Competition and researcher saturation
- Duplicate likelihood
- Response history
- Availability of test accounts
- Technology match
- Number and quality of exposed assets
- Recent product or infrastructure changes
- Business importance of the target
- Expected research effort
- Availability of meaningful attack surface
- Historical accepted finding categories where legally and publicly available

Produce categories such as:

- High-priority opportunity
- Medium-priority opportunity
- Low-priority opportunity
- Manual-review required
- Passive-recon only
- Not currently suitable

Every score must show its reasons, missing data, uncertainty, expected effort, and recommended research focus.

Example:

```text
Opportunity: Example API Program
Priority: High
Opportunity score: 81/100
Estimated effort: Medium
Reward potential: Medium-high
Competition: Medium
Scope confidence: High
Recommended focus: authorization, tenant isolation, and business logic
Important limitation: no test account supplied
```

## Module 3: Scope, authorization, and policy engine

This is a mandatory enforcement layer. Every agent action must pass through it.

For each campaign, require:

- Verified program source
- Explicit target selection
- Imported in-scope assets
- Imported exclusions
- Active program status
- Researcher confirmation
- Selected testing mode
- Maximum request rate
- Maximum total requests
- Maximum campaign duration
- Test-account selection
- Stop conditions

Enforce:

- Exact domains, subdomains, IPs, URLs, ports, and asset types
- Wildcard rules
- Excluded paths and functionality
- Program-specific request limits
- Time windows
- Authentication restrictions
- No access to unrelated users or real customer data
- No destructive or disruptive actions by default
- Automatic shutdown on policy violation or uncertainty

The system must maintain a complete decision record explaining why each action was allowed or blocked.

## Module 4: Target intelligence and attack-surface mapping

Determine the target's business model from program information and observable authorized evidence.

Possible models include:

- SaaS
- E-commerce
- Fintech
- Healthcare
- Marketplace
- Social platform
- Cloud service
- Mobile application
- API platform
- Open-source project
- AI application
- Blockchain or DeFi

Map:

- Domains and subdomains
- Web applications
- APIs and API versions
- Authentication and account recovery
- User roles and tenant boundaries
- File-upload functionality
- Payments, refunds, coupons, and transactions
- Invitations, sharing, and collaboration
- Administrative functions
- Mobile endpoints
- Public repositories
- Third-party integrations
- Cloud assets
- Smart contracts when explicitly in scope

Clearly distinguish evidence from assumptions and assign confidence to each map entry.

## Module 5: Hunt-plan generator

Create a detailed, program-specific plan based on the business model, technology, scope, and rules.

Examples:

- SaaS: tenant isolation, role permissions, sharing, invitations, administrative workflows
- E-commerce: order state, refunds, coupons, payment logic, inventory ownership
- Marketplace: buyer/seller separation, listing ownership, escrow, messaging
- API: authentication, authorization, object-level access, token handling, rate limits
- Mobile: backend authorization, tokens, deep links, client-side trust assumptions
- AI: prompt injection, data leakage, tool permissions, cross-user context separation
- Blockchain: access control, transaction validation, contract logic, oracle assumptions

Each plan must specify:

- Goal
- Authorized asset
- Research category
- Required account and role
- Allowed actions
- Forbidden actions
- Request budget
- Evidence requirements
- Expected impact
- Stop conditions
- Whether human approval is required
- Manual steps the researcher can perform

## Module 6: Safe tool orchestration

Survey and integrate mature, permitted security-research tools through controlled wrappers. The application must not give the AI unrestricted shell access.

Potential tools include:

- Burp Suite integrations
- Playwright for isolated browser workflows
- Subfinder and Amass for authorized asset discovery
- Httpx for service validation
- Ffuf or Feroxbuster for permitted endpoint discovery
- Gau for historical URL discovery where permitted
- Nmap for explicitly authorized network discovery
- Nuclei for bounded, validated checks
- Curl for controlled HTTP inspection
- Postman or Insomnia for API workflows
- Semgrep or CodeQL for authorized source-code review
- Wireshark for local or explicitly authorized traffic analysis

The tool registry must record tool version, command parameters, target, scope decision, result, and operator or agent identity.

Only use a tool when:

- The program permits it or does not prohibit the activity
- The target is in scope
- The request budget allows it
- The selected testing mode allows it
- The safety policy permits it

## Module 7: Specialized agents

Use narrow, auditable agents instead of a single unrestricted agent:

1. Program discovery agent
2. Scope-verification agent
3. Opportunity-ranking agent
4. Reconnaissance agent
5. Web-application agent
6. API agent
7. Authentication and authorization agent
8. Business-logic analysis agent
9. Mobile-analysis agent
10. Cloud-analysis agent
11. Blockchain-analysis agent
12. Evidence agent
13. Duplicate-detection agent
14. Risk-analysis agent
15. Report-writing agent
16. Safety and policy agent

The safety and policy agent must be independent, monitor every action, and be able to pause or terminate any worker.

## Module 8: Guardrails, monitoring, and emergency termination

Make safety controls available at the campaign, agent, tool, request, and workflow-step levels.

Required controls:

- Global pause button
- Campaign pause button
- Individual-agent termination
- Individual-step cancellation
- Immediate kill switch
- Request-rate limiter
- Total request budget
- Time budget
- Scope verification before every request
- Sensitive-data redaction
- Response-size limits
- Automatic detection of unexpected target behavior
- Automatic stop on errors, instability, or possible service degradation
- Automatic stop on scope ambiguity
- Automatic stop on unauthorized redirects
- Automatic stop on unexpected data exposure
- Human approval gate for impactful validation
- Full audit log

If the agent detects that its actions may be affecting the target, it must stop the current procedure, preserve minimal evidence, notify the user, and wait for direction.

## Module 9: Finding validation and categorization

When a possible issue is found:

1. Confirm the asset is in scope.
2. Confirm the program is active.
3. Reproduce using a dedicated test account.
4. Avoid unrelated users and sensitive data.
5. Capture the minimum proof required.
6. Check for duplicates.
7. Assign confidence.
8. Estimate technical and business risk.
9. Pause for human approval if deeper testing is needed.

Categorize findings by:

- Vulnerability type
- Severity
- Confidence
- Exploit complexity
- Business impact
- Affected asset
- Reproducibility
- Duplicate status
- Program eligibility
- Manual follow-up priority

## Module 10: Risk analysis and reporting

For every validated finding, produce:

- Title
- Executive summary
- Affected asset
- Program and scope reference
- Vulnerability category
- Severity and reasoning
- Confidence score
- Reproduction steps
- Expected behavior
- Actual behavior
- Sanitized evidence
- Security impact
- Affected roles or tenants
- Recommended remediation
- Suggested retest procedure
- Timeline
- Audit history

Reports must be detailed enough for both a bounty triage team and a developer to understand and fix the issue.

The first versions must draft reports only. Submission must remain manual until the system demonstrates reliable scope enforcement, evidence quality, and false-positive control.

## Manual-hunt support

The researcher must be able to use the application manually to:

- Browse program rules
- View the attack-surface map
- Follow generated checklists
- Record observations
- Attach screenshots and sanitized requests
- Mark steps complete
- Add custom findings
- Request AI analysis
- Compare findings
- Generate reports
- Pause or terminate autonomous work

Manual and autonomous work must share the same campaign, evidence, scope, and audit systems.

## Local architecture

Recommended initial stack:

- Python and FastAPI backend
- PostgreSQL database
- Redis and background workers
- React dashboard
- Playwright for isolated browser automation
- Docker-based tool isolation
- Local encrypted secrets storage
- Local evidence and report archive
- Pluggable language-model provider

The application must work without exposing local credentials, browser profiles, or sensitive files to the agent.

## Storage and privacy

Retain program data, evidence, logs, reports, campaign history, and model decisions locally for long-term research and comparison.

Implement:

- Encryption at rest where practical
- Secret separation
- Sensitive-data redaction
- Configurable retention
- Evidence versioning
- Export and backup
- Deletion controls
- Access logs

## MVP scope

The MVP should support:

- Program discovery from the first available trusted sources
- Program verification
- Scope import and policy enforcement
- Opportunity scoring
- Web and API target classification
- Passive reconnaissance
- Safe active checks
- Evidence capture
- Finding categorization
- Risk analysis
- Report drafting
- Manual-hunt workspace
- Campaign pause and emergency termination
- Complete audit logging

Start against intentionally vulnerable local applications and authorized staging targets. Do not connect to live public programs until all safety controls pass testing.

## Evolution plan

Phase 1: local labs, program intelligence, scope engine, ranking, and dashboard.

Phase 2: web/API attack-surface mapping, passive reconnaissance, and hunt plans.

Phase 3: safe checks, evidence capture, validation, and reports.

Phase 4: carefully approved testing of selected public programs.

Phase 5: specialized agents for mobile, cloud, AI, and blockchain targets.

Improve the system from structured feedback such as valid finding, false positive, duplicate, accepted report, rejected report, correct severity, scope error, and evidence quality. Safety policies must not self-modify without human review.

## Definition of success

The MVP is successful when it can discover legitimate programs, accurately enforce scope, explain opportunity rankings, map a target, create a useful hunt plan, perform bounded authorized checks, stop safely when behavior is unexpected, produce reproducible evidence, reduce false positives, support manual hunting, and generate detailed reports.

## Outstanding decisions

The following items remain open and must be decided before production deployment:

- Exact platform APIs or permitted data-access methods
- Initial model provider and operating cost
- Final approved tool list and licenses
- Whether credentials are stored locally or in a separate vault
- Evidence retention and backup policy
- Legal/compliance review
- Exact actions requiring approval
- Whether report submission will ever be automated
- Initial success metrics
- Team and researcher access controls
- Supported operating systems
- Backup and disaster-recovery approach

Until these decisions are resolved, use conservative defaults: local execution, passive mode, safe-active checks only, no destructive actions, no real customer data, no automatic submission, and mandatory human approval for impactful activity.


## Deployment Extension: Minimal Docker-Based Local Architecture

Extend the autonomous bug-bounty platform with a Docker-first local deployment model.

The deployment must use the minimum practical number of containers while preserving security, reliability, reproducibility, and emergency controls.

## Recommended container architecture

Use three containers:

```text
Docker Compose
├── app
│   ├── API
│   ├── dashboard
│   ├── campaign orchestration
│   ├── AI workflow
│   ├── report generation
│   └── database migrations
├── worker
│   ├── reconnaissance jobs
│   ├── browser automation
│   ├── approved security tools
│   └── evidence collection
└── postgres
    ├── programs
    ├── campaigns
    ├── scope policies
    ├── findings
    ├── evidence metadata
    └── audit logs
```

The `app` and `worker` containers may be built from the same Docker image with different startup commands. This avoids maintaining separate dependency sets.

Redis should not be mandatory for the MVP. Use a database-backed job queue initially. Redis may be added later if concurrent workloads require it.

Object storage should not be mandatory initially. Store evidence in a mounted local data directory with metadata in PostgreSQL. Add MinIO or another object store only when evidence volume requires it.

## Container responsibilities

### App container

The app container must provide:

- REST API
- Local dashboard
- Authentication for the local user
- Program discovery interface
- Scope and policy management
- Campaign management
- Agent orchestration
- Approval requests
- Finding management
- Report generation
- Audit-log viewing
- Pause and emergency-stop controls

The app must not directly execute arbitrary security commands.

### Worker container

The worker container must provide:

- Background job execution
- Browser automation
- Passive reconnaissance
- Approved safe checks
- Tool wrappers
- Evidence capture
- Finding validation
- Target-impact monitoring

Every worker action must call the policy engine before execution.

The worker must run as a non-root user and use restricted filesystem access, limited capabilities, controlled networking, and explicit target configuration.

### PostgreSQL container

Use PostgreSQL for persistent application state.

Store:

- Programs
- Program sources
- Scope rules
- Exclusions
- Campaigns
- Targets
- Attack-surface assets
- Hunt plans
- Jobs
- Findings
- Evidence metadata
- Reports
- User approvals
- Tool executions
- Policy decisions
- Emergency-stop events
- Model and policy versions

Use a named Docker volume for database persistence.

## Local networking

Create a private Docker network for internal communication.

Only expose the app container to the host:

```text
Host → app:8000
app → postgres:5432
worker → postgres:5432
worker → approved external targets
```

Do not expose PostgreSQL directly to the host by default.

The dashboard should be available at:

```text
http://localhost:8000
```

Allow the port to be configured through an environment variable.

## Docker Compose requirements

Provide:

- `docker-compose.yml`
- `.env.example`
- `Dockerfile`
- `Dockerfile.dev` if development mode is needed
- Database migration setup
- Health checks
- Startup dependency handling
- Named persistent volumes
- Local data directory configuration
- Clean shutdown behavior
- Log configuration
- One-command startup
- One-command shutdown
- One-command test execution

The Compose configuration must support:

```text
docker compose build
docker compose up -d
docker compose logs -f
docker compose down
docker compose run --rm app test
```

Do not delete persistent data during normal shutdown.

Provide a separate explicitly named command for data reset, with a warning and confirmation requirement.

## Dependency and package reliability

All dependencies must be pinned to known compatible versions.

The build process must:

- Use lock files
- Avoid unbounded version ranges
- Rebuild from a clean environment
- Validate Python, Node.js, browser, and system-tool versions
- Run package installation checks
- Run import checks
- Run database migration checks
- Run frontend build checks
- Run browser-launch checks
- Run security-tool wrapper checks
- Run unit and integration tests
- Produce a dependency inventory
- Record image and package versions

The application must fail clearly if an expected package or binary is missing.

Do not silently ignore failed installations.

## Browser automation

Package Playwright and all required browser binaries inside the worker image.

At image-build time:

- Install the required browser
- Verify that it launches
- Verify that a test page can be loaded
- Verify screenshot and network-capture functionality
- Run a small browser integration test

Do not use the host user’s browser profile, cookies, extensions, or saved passwords.

Use isolated browser contexts for every campaign.

## Security-tool packaging

Security tools must be installed only when permitted by their licenses and distribution requirements.

Wrap each tool behind an internal interface that validates:

- Target
- Scope
- Testing mode
- Rate limit
- Request budget
- Timeout
- Output size
- Required approval

The AI must not receive unrestricted shell access.

Each tool wrapper must:

- Accept structured input
- Reject out-of-scope targets
- Use safe default parameters
- Enforce timeouts
- Enforce output limits
- Record its execution
- Return structured results
- Support cancellation
- Stop immediately when the campaign is paused or terminated

## Runtime safety

Apply the following container restrictions where compatible:

- Run as non-root
- Drop unnecessary Linux capabilities
- Use read-only filesystem paths where possible
- Mount only required directories
- Separate evidence, temporary files, and application data
- Use explicit outbound network controls where practical
- Disable privileged mode
- Do not mount the host Docker socket
- Do not mount the host home directory
- Do not mount host browser profiles
- Limit CPU and memory
- Limit concurrent workers
- Enforce per-campaign request budgets
- Support immediate job cancellation

The emergency-stop mechanism must work even if an agent job is still running.

## Configuration

Use environment variables for configuration, with safe defaults.

Provide `.env.example` with placeholders for:

- Database connection
- Application secret
- Local host and port
- Model provider
- Model API key
- Tool enablement
- Maximum workers
- Default rate limit
- Maximum campaign duration
- Evidence directory
- Log level
- Research mode
- Approval mode

Never commit real credentials.

The default configuration must be:

- Local-only
- Passive mode
- No automatic report submission
- No destructive testing
- One worker
- Strict rate limits
- Human approval enabled

## Data persistence

Use named volumes or bind mounts for:

```text
./data/postgres
./data/evidence
./data/reports
./data/logs
./data/backups
```

The application must provide:

- Database backup
- Report export
- Evidence export
- Restore procedure
- Data-retention settings
- Optional encryption guidance
- Safe cleanup of temporary files

Do not store secrets inside evidence, logs, screenshots, or reports.

## Health checks and observability

Each service must expose a health check.

The app health check must confirm:

- API is responding
- Database connection works
- Migrations are current
- Policy engine is available
- Emergency-stop state is readable

The worker health check must confirm:

- Worker is alive
- Job queue is available
- Browser launches
- Tool registry is loaded
- Policy engine can be reached

The database health check must confirm:

- PostgreSQL accepts connections
- Required schema exists

The dashboard should show:

- Service health
- Current jobs
- Failed jobs
- Request counts
- Worker status
- Resource usage
- Active emergency stops
- Blocked policy decisions

## Test strategy

Before connecting to any live bounty program, run the complete system against intentionally vulnerable local applications.

Required test environments should include:

- A local web application
- A local API
- Authentication and role-based access
- Multi-tenant data separation
- File-upload workflows
- Business-logic workflows
- A deliberately vulnerable training application

Test:

- Scope enforcement
- Out-of-scope blocking
- Rate limiting
- Pause behavior
- Emergency termination
- Browser isolation
- Evidence redaction
- Duplicate detection
- Report generation
- Database migrations
- Backup and restore
- Tool timeout handling
- Network failure recovery
- Worker restart recovery
- Application restart recovery

The test suite must verify that a paused or terminated campaign cannot start new actions.

## CI and release checks

Before creating a release image, automatically run:

1. Dependency installation
2. Static analysis
3. Unit tests
4. Integration tests
5. Database migration tests
6. Frontend build
7. Browser smoke test
8. Tool-wrapper smoke tests
9. Container health checks
10. Scope-policy tests
11. Emergency-stop tests
12. Image vulnerability scan
13. License inventory
14. Clean rebuild from scratch

A build must fail if mandatory checks fail.

## Development and production-like modes

Provide two modes.

### Development mode

- Source code mounted for fast iteration
- Detailed logs
- Test data enabled
- Mock AI provider available
- Local training targets enabled
- No live target defaults

### Production-like local mode

- Immutable application image
- Pinned dependencies
- Minimal logs without sensitive data
- No debug endpoints
- Local authentication enabled
- Strict policy enforcement
- Backups enabled
- Safe mode enabled by default

## Packaging and user experience

Provide a simple local installation experience:

```text
1. Install Docker Desktop
2. Copy .env.example to .env
3. Add required model credentials
4. Run the startup command
5. Open the local dashboard
6. Run the built-in system checks
7. Select a local training target
```

The application must display a first-run checklist confirming:

- Database is healthy
- Browser is available
- Tool registry is available
- Model connection works
- Evidence directory is writable
- Emergency stop works
- No live target has been configured accidentally

## Definition of deployment success

The Docker deployment is successful when a clean machine can build and start the platform with the documented commands, persist data across restarts, run the built-in vulnerable lab, execute bounded research jobs, pause and terminate jobs immediately, generate reports, and recover from normal service failures.

## Important deployment decision

Use three containers for the MVP:

- One app container
- One worker container using the same image
- One PostgreSQL container

Do not add Redis, MinIO, separate frontend, or separate tool containers until testing proves they are necessary. If a specific tool requires stronger isolation, add a dedicated tool-runner container later rather than complicating the initial deployment.
