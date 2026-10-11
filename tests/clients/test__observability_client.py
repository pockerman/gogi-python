from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from gogi.clients.observability_client import ObservabilityClient
from gogi.models.observability import BudgetAlert
from gogi.utils.trace_context import current_trace, trace_metadata
from gogi.v1 import observability_service_pb2 as pb2

# The fixtures are a recipe assistant that suggests dishes from what is in the fridge


@pytest.fixture
def client():
    platform = SimpleNamespace(gateway_url="localhost:1")
    client = ObservabilityClient(platform, service="recipe-app", flush_interval_seconds=3600, max_buffer_size=5)
    client._stub = MagicMock()
    yield client
    client.close()


def sent_spans(client):
    return [span for call in client._stub.RecordSpan.call_args_list for span in call.args[0].spans]


def test_spans_nest_under_the_trace(client):
    with client.trace(
        "recipes.suggest", session_id="s-3", user_id="cook-9", workflow_id="recipes", input="eggs, leeks"
    ) as root:
        assert current_trace().trace_id == root.trace_id
        with client.span("recipes.rank", candidates=12) as child:
            child.set_attribute("ranker", "rules")
        root.set_output("A leek frittata.")
    assert current_trace() is None
    client.flush()

    child_span, root_span = sent_spans(client)
    assert root_span.parent_span_id == ""
    assert child_span.parent_span_id == root_span.span_id
    assert child_span.trace_id == root_span.trace_id
    assert (root_span.session_id, root_span.user_id, root_span.workflow_id) == ("s-3", "cook-9", "recipes")
    assert child_span.session_id == "s-3"
    assert (root_span.input, root_span.output) == ("eggs, leeks", "A leek frittata.")
    assert child_span.numeric_attributes["candidates"] == 12
    assert child_span.attributes["ranker"] == "rules"
    assert root_span.service == "recipe-app"
    assert root_span.status == pb2.SPAN_STATUS_OK
    assert root_span.end_time >= root_span.start_time


def test_calls_inside_a_trace_carry_it(client):
    assert trace_metadata() == ()
    with client.trace("recipes.suggest", session_id="s-3") as root:
        metadata = dict(client.route_metadata)
    assert metadata["x-target-service"] == "observability"
    assert metadata["x-trace-id"] == root.trace_id
    assert metadata["x-span-id"] == root.span_id
    assert metadata["x-session-id"] == "s-3"
    assert "x-user-id" not in metadata
    assert dict(client.route_metadata) == {"x-target-service": "observability"}


def test_a_failed_block_fails_its_span(client):
    with pytest.raises(KeyError):
        with client.trace("recipes.suggest"):
            raise KeyError("saffron")
    client.flush()

    (span,) = sent_spans(client)
    assert span.status == pb2.SPAN_STATUS_ERROR
    assert "saffron" in span.error_message


def test_failed_sends_are_retried_and_the_oldest_dropped(client):
    client._stub.IngestLogs.side_effect = RuntimeError("unavailable")
    for i in range(8):
        client.log("pantry_checked", f"check {i}")
    client.flush()

    client._stub.IngestLogs.side_effect = None
    client.flush()
    events = client._stub.IngestLogs.call_args.args[0].events
    assert [e.message for e in events] == [f"check {i}" for i in range(3, 8)]
    assert events[0].severity == pb2.SEVERITY_INFO
    assert events[0].service == "recipe-app"


def test_metrics_and_logs_link_to_the_trace(client):
    with client.trace("recipes.suggest", workflow_id="recipes") as root:
        client.log("allergen_found", "nuts", severity="WARNING", attributes={"ingredient": "pesto"})
    client.counter("recipes.suggestions_total", labels={"cuisine": "italian"})
    client.histogram("recipes.ranking_ms", 42.5)
    client.flush()

    (event,) = client._stub.IngestLogs.call_args.args[0].events
    assert event.trace_id == root.trace_id
    assert event.workflow_id == "recipes"
    assert event.severity == pb2.SEVERITY_WARNING
    counter, histogram = client._stub.RecordMetrics.call_args.args[0].points
    assert counter.type == pb2.METRIC_TYPE_COUNTER and counter.labels["cuisine"] == "italian"
    assert histogram.type == pb2.METRIC_TYPE_HISTOGRAM and histogram.value == 42.5

    with pytest.raises(ValueError):
        client.log("x", severity="LOUD")


def test_scores(client):
    client._stub.RecordScore.return_value = pb2.RecordScoreResponse(score_ids=["sc-1"])

    assert client.score("t-1", "uses_fridge_items", True, "AUTOMATED") == "sc-1"
    client.score("t-1", "tastiness", 0.8, "HUMAN", comment="good")
    client.score("t-1", "difficulty", "easy", "MODEL_JUDGE")

    boolean, numeric, categorical = [c.args[0].scores[0] for c in client._stub.RecordScore.call_args_list]
    assert boolean.WhichOneof("value") == "boolean_value" and boolean.boolean_value is True
    assert numeric.WhichOneof("value") == "numeric_value" and numeric.source == pb2.SCORE_SOURCE_HUMAN
    assert categorical.categorical_value == "easy"

    client._stub.RecordScore.return_value = pb2.RecordScoreResponse(rejected=["score 0: trace_id is required"])
    with pytest.raises(ValueError):
        client.score("", "x", 1.0, "HUMAN")
    with pytest.raises(ValueError):
        client.score("t-1", "x", 1.0, "ROBOT")


def test_get_trace(client):
    client._stub.GetTrace.return_value = pb2.Trace(
        trace_id="t-1",
        workflow_id="recipes",
        total_cost_usd=0.0021,
        total_tokens=900,
        start_time=1_000,
        end_time=2_500,
        spans=[pb2.Span(trace_id="t-1", span_id="a", operation="recipes.suggest", status=pb2.SPAN_STATUS_ERROR)],
        generations=[
            pb2.Generation(
                span=pb2.Span(trace_id="t-1", span_id="g", parent_span_id="a", start_time=1_100, end_time=2_000),
                model="claude-haiku-4-5",
                provider="anthropic",
                prompt_tokens=800,
                completion_tokens=100,
                cost_usd=0.0013,
                cost_estimated=True,
            )
        ],
        scores=[pb2.Score(score_id="s", name="tastiness", numeric_value=0.7, source=pb2.SCORE_SOURCE_HUMAN)],
    )

    trace = client.get_trace("t-1")

    assert trace.total_tokens == 900 and trace.workflow_id == "recipes"
    assert trace.spans[0].status == "error"
    generation = trace.generations[0]
    assert generation.span.duration_ms == 900
    assert (generation.model, generation.cost_usd, generation.cost_estimated) == ("claude-haiku-4-5", 0.0013, True)
    assert (trace.scores[0].value, trace.scores[0].source) == (0.7, "HUMAN")


def test_queries(client):
    client._stub.QueryTraces.return_value = pb2.QueryTracesResponse(
        traces=[pb2.Trace(trace_id="t-2", total_duration_ms=3200)], next_cursor="c2"
    )
    client._stub.QueryLogs.return_value = pb2.QueryLogsResponse(
        events=[pb2.LogEvent(event_id="e", severity=pb2.SEVERITY_ERROR, timestamp=5)]
    )
    client._stub.QueryScores.return_value = pb2.QueryScoresResponse(
        summaries=[pb2.ScoreSummary(name="tastiness", source=pb2.SCORE_SOURCE_HUMAN, count=4, mean=0.6)]
    )
    client._stub.QueryMetrics.return_value = pb2.QueryMetricsResponse(
        series=[
            pb2.MetricSeries(labels={"model": "m"}, samples=[pb2.MetricSample(timestamp=10, value=95.0, count=100)])
        ]
    )
    client._stub.GetCostReport.return_value = pb2.CostReport(
        total_cost_usd=1.25, generations=40, buckets=[pb2.CostBucket(group={"team": "kitchen"}, cost_usd=1.25)]
    )

    page = client.query_traces(workflow_id="recipes", score_name="tastiness", max_score=0.5, order_by="duration")
    request = client._stub.QueryTraces.call_args.args[0]
    assert request.HasField("max_score") and not request.HasField("min_score")
    assert (page.traces[0].trace_id, page.next_cursor) == ("t-2", "c2")

    logs = client.query_logs(trace_id="t-2", min_severity="WARNING")
    assert client._stub.QueryLogs.call_args.args[0].min_severity == pb2.SEVERITY_WARNING
    assert logs.events[0].severity == "ERROR"

    scores = client.query_scores(name="tastiness", source="HUMAN")
    assert scores.summaries[0].source == "HUMAN" and scores.summaries[0].count == 4

    series = client.query_metrics(
        "gogi.models.request_duration_ms", start_time=1, aggregation="p95", group_by=["model"]
    )
    assert series[0].samples[0].value == 95.0 and series[0].samples[0].count == 100

    report = client.get_cost_report(start_time=1, group_by=["team"], granularity="daily")
    assert report.generations == 40 and report.buckets[0].group == {"team": "kitchen"}


def test_budgets_and_health(client):
    client._stub.SetBudgetAlert.return_value = pb2.SetBudgetAlertResponse(
        alert=pb2.BudgetAlert(name="recipes-daily", period="daily", limit_usd=5, thresholds=[0.7, 0.9, 1.0])
    )
    client._stub.GetBudgetStatus.return_value = pb2.BudgetStatus(
        alert=pb2.BudgetAlert(name="recipes-daily", period="daily", limit_usd=5),
        spent_usd=4.0,
        fraction=0.8,
        crossed_thresholds=[0.7],
        state="warning",
    )
    client._stub.GetServiceHealth.return_value = pb2.ServiceHealthResponse(
        services=[pb2.ServiceHealth(service="llms", status="degraded", span_count=200, error_rate=0.06)]
    )

    alert = client.set_budget_alert(BudgetAlert(name="recipes-daily", period="daily", limit_usd=5))
    assert alert.thresholds == [0.7, 0.9, 1.0]
    budget = client.get_budget_status("recipes-daily")
    assert (budget.state, budget.crossed_thresholds) == ("warning", [0.7])
    (health,) = client.get_service_health()
    assert (health.service, health.status, health.span_count) == ("llms", "degraded", 200)
