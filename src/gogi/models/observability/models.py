"""The telemetry the observability service returns. Timestamps are unix millis."""

from typing import Literal

from pydantic import BaseModel, Field

ScoreSource = Literal["AUTOMATED", "MODEL_JUDGE", "HUMAN", "USER_FEEDBACK"]
Severity = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class SpanEvent(BaseModel):
    name: str = ""
    timestamp: int = 0
    attributes: dict[str, str] = Field(default_factory=dict)


class Span(BaseModel):
    trace_id: str = ""
    span_id: str = ""
    # empty for the root span of a trace
    parent_span_id: str = ""
    service: str = ""
    operation: str = ""
    start_time: int = 0
    end_time: int = 0
    # ok or error
    status: str = "ok"
    error_message: str = ""
    attributes: dict[str, str] = Field(default_factory=dict)
    numeric_attributes: dict[str, float] = Field(default_factory=dict)
    events: list[SpanEvent] = Field(default_factory=list)
    session_id: str = ""
    workflow_id: str = ""
    user_id: str = ""
    input: str = ""
    output: str = ""
    tags: list[str] = Field(default_factory=list)

    @property
    def duration_ms(self) -> int:
        return self.end_time - self.start_time


class Generation(BaseModel):
    """An LLM call: a span with the model, tokens and cost."""

    span: Span = Field(default_factory=Span)
    model: str = ""
    provider: str = ""
    # differs from model after a fallback
    requested_model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    # true if the platform priced the call from its price table
    cost_estimated: bool = False
    cache_hit: bool = False
    fallback_used: bool = False
    time_to_first_token_ms: float = 0.0


class Score(BaseModel):
    score_id: str = ""
    trace_id: str = ""
    span_id: str = ""
    generation_id: str = ""
    name: str = ""
    # a number for continuous dimensions, a string for categories, a bool for pass/fail
    value: float | str | bool | None = None
    source: str = ""
    comment: str = ""
    metadata: dict[str, str] = Field(default_factory=dict)
    timestamp: int = 0


class ScoreSummary(BaseModel):
    name: str = ""
    source: str = ""
    count: int = 0
    # over numeric scores
    mean: float = 0.0
    # over boolean scores: the share that are true
    true_ratio: float = 0.0
    categories: dict[str, int] = Field(default_factory=dict)


class Trace(BaseModel):
    trace_id: str = ""
    session_id: str = ""
    workflow_id: str = ""
    user_id: str = ""
    input: str = ""
    output: str = ""
    tags: list[str] = Field(default_factory=list)
    start_time: int = 0
    end_time: int = 0
    total_duration_ms: float = 0.0
    total_cost_usd: float = 0.0
    total_tokens: int = 0
    span_count: int = 0
    error_count: int = 0
    # only from get_trace
    spans: list[Span] = Field(default_factory=list)
    generations: list[Generation] = Field(default_factory=list)
    scores: list[Score] = Field(default_factory=list)


class TracePage(BaseModel):
    traces: list[Trace] = Field(default_factory=list)
    # pass as cursor for the next page; empty on the last page
    next_cursor: str = ""


class GenerationPage(BaseModel):
    generations: list[Generation] = Field(default_factory=list)
    next_cursor: str = ""


class ScorePage(BaseModel):
    scores: list[Score] = Field(default_factory=list)
    next_cursor: str = ""
    # over every matching score, not only this page
    summaries: list[ScoreSummary] = Field(default_factory=list)


class LogEvent(BaseModel):
    event_id: str = ""
    trace_id: str = ""
    span_id: str = ""
    timestamp: int = 0
    service: str = ""
    severity: str = "INFO"
    event_type: str = ""
    message: str = ""
    attributes: dict[str, str] = Field(default_factory=dict)
    numeric_attributes: dict[str, float] = Field(default_factory=dict)
    workflow_id: str = ""
    user_id: str = ""


class LogPage(BaseModel):
    events: list[LogEvent] = Field(default_factory=list)
    next_cursor: str = ""


class MetricSample(BaseModel):
    # the start of the bucket
    timestamp: int = 0
    value: float = 0.0
    count: int = 0


class MetricSeries(BaseModel):
    labels: dict[str, str] = Field(default_factory=dict)
    samples: list[MetricSample] = Field(default_factory=list)


class CostBucket(BaseModel):
    # the start of the period; 0 without a granularity
    period_start: int = 0
    group: dict[str, str] = Field(default_factory=dict)
    cost_usd: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    generations: int = 0


class CostReport(BaseModel):
    total_cost_usd: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    generations: int = 0
    unpriced_generations: int = 0
    buckets: list[CostBucket] = Field(default_factory=list)


class BudgetAlert(BaseModel):
    name: str
    period: Literal["daily", "weekly", "monthly"]
    limit_usd: float = Field(gt=0)
    filters: dict[str, str] = Field(default_factory=dict)
    # shares of the limit; empty means 0.7, 0.9 and 1.0
    thresholds: list[float] = Field(default_factory=list)
    webhook_url: str = ""
    created_at: int = 0
    updated_at: int = 0


class BudgetStatus(BaseModel):
    alert: BudgetAlert
    period_start: int = 0
    period_end: int = 0
    spent_usd: float = 0.0
    fraction: float = 0.0
    projected_usd: float = 0.0
    projected_fraction: float = 0.0
    crossed_thresholds: list[float] = Field(default_factory=list)
    # ok, warning or exceeded
    state: str = "ok"


class ServiceHealth(BaseModel):
    service: str = ""
    # healthy, degraded, unhealthy or unknown
    status: str = "unknown"
    last_seen: int = 0
    span_count: int = 0
    error_rate: float = 0.0
    p95_duration_ms: float = 0.0
    reason: str = ""
