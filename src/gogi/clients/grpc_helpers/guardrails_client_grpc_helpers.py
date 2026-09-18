from gogi.models.guardrails.requests.check_policy_request import CheckPolicyRequest
from gogi.models.guardrails.requests.filter_output_request import FilterOutputRequest
from gogi.models.guardrails.requests.report_violation_request import (
    ReportViolationRequest,
)
from gogi.models.guardrails.requests.validate_input_request import ValidateInputRequest
from gogi.models.guardrails.responses.check_policy_response import CheckPolicyResponse
from gogi.models.guardrails.responses.filter_output_response import FilterOutputResponse
from gogi.models.guardrails.responses.report_violation_response import (
    ReportViolationResponse,
)
from gogi.models.guardrails.responses.validate_input_response import (
    ValidateInputResponse,
)
from gogi.v1 import llm_quardrail_service_pb2


class GuardrailsClientGRPCHelper:
    # --- ValidateInput ---

    @staticmethod
    def build_grpc_validate_input_request(
        request: ValidateInputRequest,
    ) -> llm_quardrail_service_pb2.ValidateInputRequest:
        return llm_quardrail_service_pb2.ValidateInputRequest(
            content=request.content,
            checks=request.checks,
            context=request.context,
        )

    @staticmethod
    def serialize_validate_input_grpc_response(
        grpc_response: llm_quardrail_service_pb2.ValidateInputResponse,
    ) -> ValidateInputResponse:
        return ValidateInputResponse(
            allowed=grpc_response.allowed,
            denial_reason=grpc_response.denial_reason,
            triggered_checks=list(grpc_response.triggered_checks),
        )

    # --- FilterOutput ---

    @staticmethod
    def build_grpc_filter_output_request(request: FilterOutputRequest) -> llm_quardrail_service_pb2.FilterOutputRequest:
        return llm_quardrail_service_pb2.FilterOutputRequest(
            content=request.content,
            filters=request.filters,
            context=request.context,
        )

    @staticmethod
    def serialize_filter_output_grpc_response(
        grpc_response: llm_quardrail_service_pb2.FilterOutputResponse,
    ) -> FilterOutputResponse:
        return FilterOutputResponse(
            content=grpc_response.content,
            modified=grpc_response.modified,
            applied_filters=list(grpc_response.applied_filters),
        )

    # --- CheckPolicy ---

    @staticmethod
    def build_grpc_check_policy_request(request: CheckPolicyRequest) -> llm_quardrail_service_pb2.CheckPolicyRequest:
        return llm_quardrail_service_pb2.CheckPolicyRequest(
            policy_name=request.policy_name,
            action=request.action,
            context=request.context,
            arguments_json=request.arguments_json,
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
        )

    @staticmethod
    def serialize_report_violation_grpc_response(
        grpc_response: llm_quardrail_service_pb2.ReportViolationResponse,
    ) -> ReportViolationResponse:
        return ReportViolationResponse(
            violation_id=grpc_response.violation_id,
            recorded=grpc_response.recorded,
        )
