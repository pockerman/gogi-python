import json
from typing import Any

from gogi.models.guardrails.guardrail_policy import GuardrailPolicy
from gogi.models.guardrails.requests.check_policy_request import CheckPolicyRequest
from gogi.models.guardrails.requests.filter_output_request import FilterOutputRequest
from gogi.models.guardrails.requests.list_violations_request import ListViolationsRequest
from gogi.models.guardrails.requests.report_violation_request import (
    ReportViolationRequest,
)
from gogi.models.guardrails.requests.validate_input_request import ValidateInputRequest
from gogi.models.guardrails.responses.add_policy_response import AddPolicyResponse
from gogi.models.guardrails.responses.check_policy_response import CheckPolicyResponse
from gogi.models.guardrails.responses.filter_output_response import FilterOutputResponse
from gogi.models.guardrails.responses.report_violation_response import (
    ReportViolationResponse,
)
from gogi.models.guardrails.responses.validate_input_response import (
    ValidateInputResponse,
)
from gogi.models.guardrails.triggered_rule import TriggeredRule
from gogi.models.guardrails.violation import Violation
from gogi.v1 import llm_quardrail_service_pb2


class GuardrailsClientGRPCHelper:
    @staticmethod
    def serialize_triggered_rules(grpc_rules: Any) -> list[TriggeredRule]:
        return [
            TriggeredRule(
                policy_name=rule.policy_name,
                rule_type=rule.rule_type,
                action=rule.action,
                severity=rule.severity,
                detail=rule.detail,
                shadow=rule.shadow,
            )
            for rule in grpc_rules
        ]

    # --- ValidateInput ---

    @staticmethod
    def build_grpc_validate_input_request(
        request: ValidateInputRequest,
    ) -> llm_quardrail_service_pb2.ValidateInputRequest:
        return llm_quardrail_service_pb2.ValidateInputRequest(
            content=request.content,
            checks=request.checks,
            context=request.context,
            policy_names=request.policy_names,
            application_id=request.application_id,
        )

    @staticmethod
    def serialize_validate_input_grpc_response(
        grpc_response: llm_quardrail_service_pb2.ValidateInputResponse,
    ) -> ValidateInputResponse:
        return ValidateInputResponse(
            allowed=grpc_response.allowed,
            denial_reason=grpc_response.denial_reason,
            triggered_checks=list(grpc_response.triggered_checks),
            triggered_rules=GuardrailsClientGRPCHelper.serialize_triggered_rules(grpc_response.triggered_rules),
            user_message=grpc_response.user_message,
            evaluation_id=grpc_response.evaluation_id,
        )

    # --- FilterOutput ---

    @staticmethod
    def build_grpc_filter_output_request(request: FilterOutputRequest) -> llm_quardrail_service_pb2.FilterOutputRequest:
        return llm_quardrail_service_pb2.FilterOutputRequest(
            content=request.content,
            filters=request.filters,
            context=request.context,
            policy_names=request.policy_names,
            application_id=request.application_id,
        )

    @staticmethod
    def serialize_filter_output_grpc_response(
        grpc_response: llm_quardrail_service_pb2.FilterOutputResponse,
    ) -> FilterOutputResponse:
        return FilterOutputResponse(
            content=grpc_response.content,
            modified=grpc_response.modified,
            applied_filters=list(grpc_response.applied_filters),
            blocked=grpc_response.blocked,
            triggered_rules=GuardrailsClientGRPCHelper.serialize_triggered_rules(grpc_response.triggered_rules),
            evaluation_id=grpc_response.evaluation_id,
        )

    # --- CheckPolicy ---

    @staticmethod
    def build_grpc_check_policy_request(request: CheckPolicyRequest) -> llm_quardrail_service_pb2.CheckPolicyRequest:
        arguments_json = request.arguments_json
        if not arguments_json and request.arguments is not None:
            arguments_json = json.dumps(request.arguments)

        return llm_quardrail_service_pb2.CheckPolicyRequest(
            policy_name=request.policy_name,
            action=request.action,
            context=request.context,
            arguments_json=arguments_json,
            application_id=request.application_id,
        )

    @staticmethod
    def serialize_check_policy_grpc_response(
        grpc_response: llm_quardrail_service_pb2.CheckPolicyResponse,
    ) -> CheckPolicyResponse:
        return CheckPolicyResponse(
            allowed=grpc_response.allowed,
            denial_reason=grpc_response.denial_reason,
            violated_rules=list(grpc_response.violated_rules),
            suggested_action=grpc_response.suggested_action,
            triggered_rules=GuardrailsClientGRPCHelper.serialize_triggered_rules(grpc_response.triggered_rules),
            approval_role=grpc_response.approval_role,
            evaluation_id=grpc_response.evaluation_id,
        )

    # --- ReportViolation ---

    @staticmethod
    def build_grpc_report_violation_request(
        request: ReportViolationRequest,
    ) -> llm_quardrail_service_pb2.ReportViolationRequest:
        return llm_quardrail_service_pb2.ReportViolationRequest(
            policy_name=request.policy_name,
            action=request.action,
            severity=request.severity,
            context=request.context,
            details=request.details,
            evaluation_id=request.evaluation_id,
        )

    @staticmethod
    def serialize_report_violation_grpc_response(
        grpc_response: llm_quardrail_service_pb2.ReportViolationResponse,
    ) -> ReportViolationResponse:
        return ReportViolationResponse(
            violation_id=grpc_response.violation_id,
            recorded=grpc_response.recorded,
        )

    # --- Policies ---

    @staticmethod
    def policy_to_grpc(policy: GuardrailPolicy) -> llm_quardrail_service_pb2.Policy:
        return llm_quardrail_service_pb2.Policy(
            name=policy.name,
            type=policy.type,
            application_id=policy.application_id,
            mode=policy.mode,
            rules_json=json.dumps(policy.rules),
            description=policy.description,
            version=policy.version,
        )

    @staticmethod
    def grpc_to_policy(grpc_policy: llm_quardrail_service_pb2.Policy) -> GuardrailPolicy:
        return GuardrailPolicy(
            name=grpc_policy.name,
            type=grpc_policy.type,
            rules=json.loads(grpc_policy.rules_json),
            application_id=grpc_policy.application_id,
            mode=grpc_policy.mode or "enforce",
            description=grpc_policy.description,
            version=grpc_policy.version,
            revision=grpc_policy.revision,
            source=grpc_policy.source,
            created_at=grpc_policy.created_at,
            updated_at=grpc_policy.updated_at,
        )

    @staticmethod
    def serialize_add_policy_grpc_response(
        grpc_response: llm_quardrail_service_pb2.AddPolicyResponse,
    ) -> AddPolicyResponse:
        return AddPolicyResponse(
            policy=GuardrailsClientGRPCHelper.grpc_to_policy(grpc_response.policy),
            warnings=list(grpc_response.warnings),
        )

    # --- Violations ---

    @staticmethod
    def build_grpc_list_violations_request(
        request: ListViolationsRequest,
    ) -> llm_quardrail_service_pb2.ListViolationsRequest:
        return llm_quardrail_service_pb2.ListViolationsRequest(
            policy_name=request.policy_name,
            severity=request.severity,
            since=request.since,
            limit=request.limit,
        )

    @staticmethod
    def grpc_to_violation(grpc_violation: llm_quardrail_service_pb2.Violation) -> Violation:
        return Violation(
            violation_id=grpc_violation.violation_id,
            policy_name=grpc_violation.policy_name,
            action=grpc_violation.action,
            severity=grpc_violation.severity,
            context=dict(grpc_violation.context),
            details=grpc_violation.details,
            evaluation_id=grpc_violation.evaluation_id,
            created_at=grpc_violation.created_at,
        )
