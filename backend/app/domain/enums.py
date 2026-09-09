"""Domain enums for Aegis AI representing system lifecycle and state machines."""

import enum


class AppEnvironment(str, enum.Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class TenantStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


class TargetMode(str, enum.Enum):
    HOSTED = "HOSTED"
    LOCAL_HF = "LOCAL_HF"
    AGENT = "AGENT"


class ConnectorProfile(str, enum.Enum):
    AEGIS_SIMPLE_CHAT_V1 = "aegis_simple_chat_v1"
    OPENAI_CHAT_V1 = "openai_chat_v1"
    GRADIO_SPACE_V1 = "gradio_space_v1"
    CUSTOM_REST_V1 = "custom_rest_v1"


class EvaluationLevel(str, enum.Enum):
    PRELIMINARY_RAPID = "PRELIMINARY_RAPID"
    FULL = "FULL"


class HumanReviewStatus(str, enum.Enum):
    NONE = "NONE"
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"
    DISPUTED = "DISPUTED"


class TargetStatus(str, enum.Enum):
    PENDING_VALIDATION = "PENDING_VALIDATION"
    VALIDATING = "VALIDATING"
    VERIFIED = "VERIFIED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    SUSPENDED = "SUSPENDED"


class CredentialKind(str, enum.Enum):
    API_KEY = "API_KEY"
    OAUTH = "OAUTH"
    AGENT_TOKEN = "AGENT_TOKEN"
    CUSTOM_HEADER = "CUSTOM_HEADER"


class CredentialStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class BenchmarkSourceType(str, enum.Enum):
    EXTERNAL = "EXTERNAL"
    DOMAIN_CUSTOM = "DOMAIN_CUSTOM"
    SYNTHETIC = "SYNTHETIC"


class BenchmarkSourceStatus(str, enum.Enum):
    APPROVED = "APPROVED"
    PENDING_REVIEW = "PENDING_REVIEW"
    REJECTED = "REJECTED"
    DEPRECATED = "DEPRECATED"


class TestCaseMode(str, enum.Enum):
    SINGLE = "SINGLE"
    SESSION = "SESSION"


class SeverityLevel(str, enum.Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReviewStatus(str, enum.Enum):
    APPROVED = "APPROVED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"


class JobMode(str, enum.Enum):
    QUICK = "QUICK"
    FULL = "FULL"


class JobState(str, enum.Enum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PAUSING = "PAUSING"
    PAUSED = "PAUSED"
    RECOVERING = "RECOVERING"
    AGGREGATING = "AGGREGATING"
    CERTIFYING = "CERTIFYING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_LIMITATIONS = "COMPLETED_WITH_LIMITATIONS"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class JobItemState(str, enum.Enum):
    PENDING = "PENDING"
    LEASED = "LEASED"
    TARGET_RUNNING = "TARGET_RUNNING"
    TARGET_COMPLETE = "TARGET_COMPLETE"
    JUDGING = "JUDGING"
    COMPLETE = "COMPLETE"
    RETRY_WAIT = "RETRY_WAIT"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    JUDGE_INVALID = "JUDGE_INVALID"


class SessionState(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    SAFE_TERMINATED = "SAFE_TERMINATED"
    HARM_DETECTED = "HARM_DETECTED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class TurnRole(str, enum.Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"


class TurnState(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    RECEIVED = "RECEIVED"
    JUDGED = "JUDGED"
    FAILED = "FAILED"


class TargetResponseStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    REFUSAL = "REFUSAL"
    MALFORMED = "MALFORMED"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"
    BLOCKED = "BLOCKED"


class JudgeStatus(str, enum.Enum):
    PENDING = "PENDING"
    JUDGED = "JUDGED"
    JUDGE_INVALID = "JUDGE_INVALID"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    SKIPPED = "SKIPPED"


class Verdict(str, enum.Enum):
    SAFE = "SAFE"
    UNSAFE = "UNSAFE"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_EVALUABLE = "NOT_EVALUABLE"


class AttemptPhase(str, enum.Enum):
    TARGET = "TARGET"
    JUDGE = "JUDGE"


class AttemptStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    RETRYABLE_ERROR = "RETRYABLE_ERROR"
    HARD_FAILURE = "HARD_FAILURE"
    TIMEOUT = "TIMEOUT"


class TraceAvailability(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    CORRUPT = "CORRUPT"
    PARTIAL = "PARTIAL"


class TraceStageType(str, enum.Enum):
    PROMPT = "PROMPT"
    RETRIEVAL = "RETRIEVAL"
    TOOL_CALL = "TOOL_CALL"
    INTERMEDIATE_REASONING = "INTERMEDIATE_REASONING"
    OUTPUT_SYNTHESIS = "OUTPUT_SYNTHESIS"


class TraceStageStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    MODIFIED = "MODIFIED"
    SKIPPED = "SKIPPED"


class CertificateStatus(str, enum.Enum):
    GENERATING = "GENERATING"
    READY = "READY"
    FAILED = "FAILED"
    SUPERSEDED = "SUPERSEDED"
