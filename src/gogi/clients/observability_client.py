import atexit
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from google.protobuf.json_format import MessageToDict

from gogi.clients.base_client import BaseClient
from gogi.models.observability import (
    BudgetAlert,
    BudgetStatus,
    CostReport,
    Generation,
    GenerationPage,
    LogEvent,
    LogPage,
    MetricSeries,
    Score,
    ScorePage,
    ScoreSummary,
    ServiceHealth,
    Span,
    Trace,
    TracePage,
)
from gogi.utils.trace_context import (
    TraceContext,
    current_trace,
    new_span_id,
    new_trace_id,
    reset_trace,
    set_trace,
)
from gogi.v1 import observability_service_pb2 as pb2
from gogi.v1 import observability_service_pb2_grpc

_SEVERITIES = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
_SOURCES = {"AUTOMATED", "MODEL_JUDGE", "HUMAN", "USER_FEEDBACK"}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _to_dict(message) -> dict:
    return MessageToDict(message, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)


def _span_from_grpc(span: pb2.Span) -> Span:
    data = _to_dict(span)
    data["status"] = "error" if span.status == pb2.SPAN_STATUS_ERROR else "ok"
    return Span.model_validate(data)


def _generation_from_grpc(generation: pb2.Generation) -> Generation:
    return Generation(
        span=_span_from_grpc(generation.span),
        model=generation.model,
        provider=generation.provider,
        requested_model=generation.requested_model,
        prompt_tokens=generation.prompt_tokens,
        completion_tokens=generation.completion_tokens,
        cost_usd=generation.cost_usd,
        cost_estimated=generation.cost_estimated,
        cache_hit=generation.cache_hit,
        fallback_used=generation.fallback_used,
        time_to_first_token_ms=generation.time_to_first_token_ms,
    )


def _source_name(source: int) -> str:
    return pb2.ScoreSource.Name(source).removeprefix("SCORE_SOURCE_")


def _score_from_grpc(score: pb2.Score) -> Score:
    kind = score.WhichOneof("value")
    return Score(
        score_id=score.score_id,
        trace_id=score.trace_id,
        span_id=score.span_id,
        generation_id=score.generation_id,
        name=score.name,
        value=getattr(score, kind) if kind else None,
        source=_source_name(score.source),
        comment=score.comment,
        metadata=dict(score.metadata),
        timestamp=score.timestamp,
    )


def _trace_from_grpc(trace: pb2.Trace) -> Trace:
    return Trace(
        trace_id=trace.trace_id,
        session_id=trace.session_id,
        workflow_id=trace.workflow_id,
        user_id=trace.user_id,
        input=trace.input,
        output=trace.output,
        tags=list(trace.tags),
        start_time=trace.start_time,
        end_time=trace.end_time,
        total_duration_ms=trace.total_duration_ms,
        total_cost_usd=trace.total_cost_usd,
        total_tokens=trace.total_tokens,
        span_count=trace.span_count,
        error_count=trace.error_count,
        spans=[_span_from_grpc(s) for s in trace.spans],
        generations=[_generation_from_grpc(g) for g in trace.generations],
        scores=[_score_from_grpc(s) for s in trace.scores],
    )


def _log_from_grpc(event: pb2.LogEvent) -> LogEvent:
    data = _to_dict(event)
    data["severity"] = pb2.Severity.Name(event.severity).removeprefix("SEVERITY_")
    return LogEvent.model_validate(data)


class TraceSpan:
    """A span of the application's own work, ended when its block ends."""

    def __init__(self, span: pb2.Span):
        self._span = span

    @property
    def trace_id(self) -> str:
        return self._span.trace_id

    @property
    def span_id(self) -> str:
        return self._span.span_id

    def set_attribute(self, key: str, value: str | float | int | bool) -> None:
        """Sets an attribute; numbers are numeric attributes, anything else is text."""
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            self._span.numeric_attributes[key] = float(value)
        else:
            self._span.attributes[key] = str(value)

    def set_input(self, text: str) -> None:
        self._span.input = text

    def set_output(self, text: str) -> None:
        """The response; on the root span it becomes the trace's output."""
        self._span.output = text

    def add_event(self, name: str, **attributes: str) -> None:
        self._span.events.append(pb2.SpanEvent(name=name, timestamp=_now_ms(), attributes=attributes))


class _Buffer:
    """Items waiting to be sent; the oldest are dropped beyond the limit."""

    def __init__(self, max_size: int):
        self.items: list = []
        self.max_size = max_size
        self.dropped = 0

    def add(self, item) -> int:
        self.items.append(item)
        if len(self.items) > self.max_size:
            over = len(self.items) - self.max_size
            del self.items[:over]
            self.dropped += over
        return len(self.items)

    def take(self, n: int) -> list:
        batch, self.items = self.items[:n], self.items[n:]
        return batch

    def put_back(self, batch: list) -> None:
        room = max(self.max_size - len(self.items), 0)
        if room < len(batch):
            self.dropped += len(batch) - room
            batch = batch[len(batch) - room :]
        self.items = batch + self.items


class ObservabilityClient(BaseClient):
    """Reports the application's telemetry and queries the platform's.

    Spans, logs and metric points are buffered and sent in batches from a background thread,
    so reporting never slows the application down; what is left is sent at exit, or with
    flush(). Inside trace() or span(), every call to the platform carries the trace, so the
    spans the platform's services record nest under the application's.
    """

    def __init__(
        self,
        platform,
        logger=None,
        service: str = "application",
        batch_size: int = 100,
        flush_interval_seconds: float = 5.0,
        max_buffer_size: int = 10_000,
    ):
        super().__init__(platform=platform, service_name="observability", logger=logger)
        self._stub = observability_service_pb2_grpc.ObservabilityServiceStub(self._channel)
        # the name the application's spans, logs and metrics are reported under
        self.service = service
        self._batch_size = batch_size
        self._lock = threading.Lock()
        self._spans = _Buffer(max_buffer_size)
        self._logs = _Buffer(max_buffer_size)
        self._metrics = _Buffer(max_buffer_size)
        self._wake = threading.Event()
        self._stopped = threading.Event()
        self._interval = flush_interval_seconds
        self._thread = threading.Thread(target=self._run, name="gogi-observability", daemon=True)
        self._thread.start()
        atexit.register(self.close)

    # --- tracing ---

    @contextmanager
    def trace(
        self,
        operation: str,
        *,
        session_id: str = "",
        user_id: str = "",
        workflow_id: str = "",
        input: str = "",
        tags: list[str] | None = None,
        **attributes: Any,
    ) -> Iterator[TraceSpan]:
        """Starts a trace for a request: its root span, ended when the block ends.

        The session, user and workflow go with every call to the platform made inside it.
        Set the response with set_output: it becomes the trace's output.
        """
        context = TraceContext(trace_id=new_trace_id(), session_id=session_id, user_id=user_id, workflow_id=workflow_id)
        with self._span(operation, context, input=input, tags=tags or [], attributes=attributes) as span:
            yield span

    @contextmanager
    def span(self, operation: str, **attributes: Any) -> Iterator[TraceSpan]:
        """Records a span of the application's own work inside the current trace, or starts
        a trace if there is none."""
        context = current_trace() or TraceContext(trace_id=new_trace_id())
        with self._span(operation, context, input="", tags=[], attributes=attributes) as span:
            yield span

    @contextmanager
    def _span(self, operation: str, context: TraceContext, input: str, tags: list[str], attributes: dict):
        span = pb2.Span(
            trace_id=context.trace_id,
            span_id=new_span_id(),
            parent_span_id=context.span_id,
            service=self.service,
            operation=operation,
            start_time=_now_ms(),
            session_id=context.session_id,
            workflow_id=context.workflow_id,
            user_id=context.user_id,
            input=input,
            tags=tags,
        )
        handle = TraceSpan(span)
        for key, value in attributes.items():
            handle.set_attribute(key, value)

        token = set_trace(context.child(span.span_id))
        try:
            yield handle
            span.status = pb2.SPAN_STATUS_OK
        except BaseException as e:
            span.status = pb2.SPAN_STATUS_ERROR
            span.error_message = f"{type(e).__name__}: {e}"
            raise
        finally:
            reset_trace(token)
            span.end_time = _now_ms()
            self._add(self._spans, span)

    # --- logs and metrics ---

    def log(
        self,
        event_type: str,
        message: str = "",
        severity: str = "INFO",
        attributes: dict[str, str] | None = None,
        numeric_attributes: dict[str, float] | None = None,
    ) -> None:
        """Records a structured log event, linked to the current span."""
        if severity not in _SEVERITIES:
            raise ValueError(f"severity must be one of {sorted(_SEVERITIES)}")
        context = current_trace()
        self._add(
            self._logs,
            pb2.LogEvent(
                trace_id=context.trace_id if context else "",
                span_id=context.span_id if context else "",
                timestamp=_now_ms(),
                service=self.service,
                severity=pb2.Severity.Value("SEVERITY_" + severity),
                event_type=event_type,
                message=message,
                attributes=attributes or {},
                numeric_attributes=numeric_attributes or {},
                workflow_id=context.workflow_id if context else "",
                user_id=context.user_id if context else "",
            ),
        )

    def counter(self, name: str, value: float = 1, labels: dict[str, str] | None = None) -> None:
        """Records a value that accumulates; names end in _total by convention."""
        self._metric(name, pb2.METRIC_TYPE_COUNTER, value, labels)

    def histogram(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Records a measurement whose distribution matters, e.g. a latency in ms."""
        self._metric(name, pb2.METRIC_TYPE_HISTOGRAM, value, labels)

    def _metric(self, name: str, metric_type, value: float, labels: dict[str, str] | None) -> None:
        self._add(
            self._metrics,
            pb2.MetricPoint(
                name=name,
                type=metric_type,
                value=value,
                labels=labels or {},
                timestamp=_now_ms(),
                service=self.service,
            ),
        )

    # --- delivery ---

    def _add(self, buffer: _Buffer, item) -> None:
        with self._lock:
            size = buffer.add(item)
        if size >= self._batch_size:
            self._wake.set()

    def _run(self) -> None:
        while not self._stopped.is_set():
            self._wake.wait(self._interval)
            self._wake.clear()
            self.flush()

    def _flush_buffer(self, buffer: _Buffer, kind: str, send) -> None:
        while True:
            with self._lock:
                batch = buffer.take(self._batch_size)
                dropped, buffer.dropped = buffer.dropped, 0
            if dropped and self.logger:
                self.logger.warning(f"observability: dropped {dropped} {kind} that could not be sent")
            if not batch:
                return
            try:
                send(batch)
            except Exception as e:
                with self._lock:
                    buffer.put_back(batch)
                if self.logger:
                    self.logger.debug(f"observability: failed to send {len(batch)} {kind}, will retry: {e}")
                return
            if len(batch) < self._batch_size:
                return

    def flush(self) -> None:
        """Sends what is buffered now."""
        metadata = self.route_metadata
        self._flush_buffer(
            self._spans, "spans", lambda b: self._stub.RecordSpan(pb2.RecordSpanRequest(spans=b), metadata=metadata)
        )
        self._flush_buffer(
            self._logs,
            "log events",
            lambda b: self._stub.IngestLogs(pb2.IngestLogsRequest(events=b), metadata=metadata),
        )
        self._flush_buffer(
            self._metrics,
            "metric points",
            lambda b: self._stub.RecordMetrics(pb2.RecordMetricsRequest(points=b), metadata=metadata),
        )

    def close(self) -> None:
        """Stops the background thread and sends what is buffered."""
        if self._stopped.is_set():
            return
        self._stopped.set()
        self._wake.set()
        self._thread.join(timeout=5)
        self.flush()

    # --- scores ---

    def score(
        self,
        trace_id: str,
        name: str,
        value: float | str | bool,
        source: str,
        span_id: str = "",
        generation_id: str = "",
        comment: str = "",
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Records a quality score about a trace, or one of its spans or generations, and
        returns its id. A bool is a pass/fail score, a number a continuous one (0.0 to 1.0),
        a string a category. source is AUTOMATED, MODEL_JUDGE, HUMAN or USER_FEEDBACK."""
        if source not in _SOURCES:
            raise ValueError(f"source must be one of {sorted(_SOURCES)}")
        score = pb2.Score(
            trace_id=trace_id,
            span_id=span_id,
            generation_id=generation_id,
            name=name,
            source=pb2.ScoreSource.Value("SCORE_SOURCE_" + source),
            comment=comment,
            metadata=metadata or {},
        )
        if isinstance(value, bool):
            score.boolean_value = value
        elif isinstance(value, (int, float)):
            score.numeric_value = float(value)
        else:
            score.categorical_value = str(value)

        response = self._stub.RecordScore(pb2.RecordScoreRequest(scores=[score]), metadata=self.route_metadata)
        if response.rejected:
            raise ValueError(response.rejected[0])
        return response.score_ids[0]

    # --- queries ---

    def get_trace(self, trace_id: str) -> Trace:
        """A trace with its spans, generations and scores."""
        return _trace_from_grpc(
            self._stub.GetTrace(pb2.GetTraceRequest(trace_id=trace_id), metadata=self.route_metadata)
        )

    def query_traces(
        self,
        start_time: int = 0,
        end_time: int = 0,
        session_id: str = "",
        workflow_id: str = "",
        user_id: str = "",
        service: str = "",
        tag: str = "",
        min_duration_ms: float = 0,
        min_cost_usd: float = 0,
        errors_only: bool = False,
        score_name: str = "",
        min_score: float | None = None,
        max_score: float | None = None,
        order_by: str = "recent",
        limit: int = 0,
        cursor: str = "",
    ) -> TracePage:
        """Traces, without their spans, newest first, or by duration or cost."""
        response = self._stub.QueryTraces(
            pb2.QueryTracesRequest(
                start_time=start_time,
                end_time=end_time,
                session_id=session_id,
                workflow_id=workflow_id,
                user_id=user_id,
                service=service,
                tag=tag,
                min_duration_ms=min_duration_ms,
                min_cost_usd=min_cost_usd,
                errors_only=errors_only,
                score_name=score_name,
                min_score=min_score,
                max_score=max_score,
                order_by=order_by,
                limit=limit,
                cursor=cursor,
            ),
            metadata=self.route_metadata,
        )
        return TracePage(traces=[_trace_from_grpc(t) for t in response.traces], next_cursor=response.next_cursor)

    def query_generations(
        self,
        start_time: int = 0,
        end_time: int = 0,
        model: str = "",
        provider: str = "",
        workflow_id: str = "",
        user_id: str = "",
        session_id: str = "",
        min_cost_usd: float = 0,
        fallback_used: bool | None = None,
        limit: int = 0,
        cursor: str = "",
    ) -> GenerationPage:
        """LLM calls, newest first."""
        response = self._stub.QueryGenerations(
            pb2.QueryGenerationsRequest(
                start_time=start_time,
                end_time=end_time,
                model=model,
                provider=provider,
                workflow_id=workflow_id,
                user_id=user_id,
                session_id=session_id,
                min_cost_usd=min_cost_usd,
                fallback_used=fallback_used,
                limit=limit,
                cursor=cursor,
            ),
            metadata=self.route_metadata,
        )
        return GenerationPage(
            generations=[_generation_from_grpc(g) for g in response.generations], next_cursor=response.next_cursor
        )

    def query_scores(
        self,
        trace_id: str = "",
        name: str = "",
        source: str = "",
        workflow_id: str = "",
        start_time: int = 0,
        end_time: int = 0,
        limit: int = 0,
        cursor: str = "",
    ) -> ScorePage:
        """Scores, newest first, with summaries over every matching score."""
        if source and source not in _SOURCES:
            raise ValueError(f"source must be one of {sorted(_SOURCES)}")
        response = self._stub.QueryScores(
            pb2.QueryScoresRequest(
                trace_id=trace_id,
                name=name,
                source=pb2.ScoreSource.Value("SCORE_SOURCE_" + source) if source else 0,
                workflow_id=workflow_id,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
                cursor=cursor,
            ),
            metadata=self.route_metadata,
        )
        summaries = []
        for summary in response.summaries:
            data = _to_dict(summary)
            data["source"] = _source_name(summary.source)
            summaries.append(ScoreSummary.model_validate(data))
        return ScorePage(
            scores=[_score_from_grpc(s) for s in response.scores], next_cursor=response.next_cursor, summaries=summaries
        )

    def query_logs(
        self,
        trace_id: str = "",
        span_id: str = "",
        service: str = "",
        event_type: str = "",
        min_severity: str = "",
        workflow_id: str = "",
        user_id: str = "",
        attributes: dict[str, str] | None = None,
        start_time: int = 0,
        end_time: int = 0,
        limit: int = 0,
        cursor: str = "",
    ) -> LogPage:
        """Log events, newest first."""
        if min_severity and min_severity not in _SEVERITIES:
            raise ValueError(f"min_severity must be one of {sorted(_SEVERITIES)}")
        response = self._stub.QueryLogs(
            pb2.QueryLogsRequest(
                trace_id=trace_id,
                span_id=span_id,
                service=service,
                event_type=event_type,
                min_severity=pb2.Severity.Value("SEVERITY_" + min_severity) if min_severity else 0,
                workflow_id=workflow_id,
                user_id=user_id,
                attributes=attributes or {},
                start_time=start_time,
                end_time=end_time,
                limit=limit,
                cursor=cursor,
            ),
            metadata=self.route_metadata,
        )
        return LogPage(events=[_log_from_grpc(e) for e in response.events], next_cursor=response.next_cursor)

    def query_metrics(
        self,
        name: str,
        start_time: int,
        end_time: int = 0,
        label_filters: dict[str, str] | None = None,
        group_by: list[str] | None = None,
        step_ms: int = 0,
        aggregation: str = "",
    ) -> list[MetricSeries]:
        """A metric aggregated over time: sum, count, avg, min, max, p50, p90, p95 or p99."""
        response = self._stub.QueryMetrics(
            pb2.QueryMetricsRequest(
                name=name,
                start_time=start_time,
                end_time=end_time,
                label_filters=label_filters or {},
                group_by=group_by or [],
                step_ms=step_ms,
                aggregation=aggregation,
            ),
            metadata=self.route_metadata,
        )
        return [MetricSeries.model_validate(_to_dict(s)) for s in response.series]

    def get_cost_report(
        self,
        start_time: int,
        end_time: int = 0,
        group_by: list[str] | None = None,
        filters: dict[str, str] | None = None,
        granularity: str = "",
    ) -> CostReport:
        """The cost of LLM calls, grouped by model, provider, workflow_id, user_id, session_id,
        service or any attribute of their spans, e.g. team; per hourly, daily, weekly or monthly period."""
        response = self._stub.GetCostReport(
            pb2.CostReportRequest(
                start_time=start_time,
                end_time=end_time,
                group_by=group_by or [],
                filters=filters or {},
                granularity=granularity,
            ),
            metadata=self.route_metadata,
        )
        return CostReport.model_validate(_to_dict(response))

    # --- budgets and health ---

    def set_budget_alert(self, alert: BudgetAlert) -> BudgetAlert:
        response = self._stub.SetBudgetAlert(
            pb2.SetBudgetAlertRequest(
                alert=pb2.BudgetAlert(
                    name=alert.name,
                    period=alert.period,
                    limit_usd=alert.limit_usd,
                    filters=alert.filters,
                    thresholds=alert.thresholds,
                    webhook_url=alert.webhook_url,
                )
            ),
            metadata=self.route_metadata,
        )
        return BudgetAlert.model_validate(_to_dict(response.alert))

    def get_budget_status(self, name: str) -> BudgetStatus:
        response = self._stub.GetBudgetStatus(pb2.GetBudgetStatusRequest(name=name), metadata=self.route_metadata)
        return BudgetStatus.model_validate(_to_dict(response))

    def list_budget_alerts(self) -> list[BudgetAlert]:
        response = self._stub.ListBudgetAlerts(pb2.ListBudgetAlertsRequest(), metadata=self.route_metadata)
        return [BudgetAlert.model_validate(_to_dict(a)) for a in response.alerts]

    def delete_budget_alert(self, name: str) -> bool:
        return self._stub.DeleteBudgetAlert(
            pb2.DeleteBudgetAlertRequest(name=name), metadata=self.route_metadata
        ).deleted

    def get_service_health(self, service: str = "", window_ms: int = 0) -> list[ServiceHealth]:
        """The health of the platform's services, from the spans they recorded recently."""
        response = self._stub.GetServiceHealth(
            pb2.ServiceHealthRequest(service=service, window_ms=window_ms), metadata=self.route_metadata
        )
        return [ServiceHealth.model_validate(_to_dict(s)) for s in response.services]
