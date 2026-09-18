from gogi.clients.base_client import BaseClient
from gogi.clients.grpc_helpers.guardrails_client_grpc_helpers import (
    GuardrailsClientGRPCHelper,
)
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
from gogi.v1 import llm_quardrail_service_pb2_grpc


class GuardrailsClient(BaseClient):
    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="guardrails", logger=logger)
        self._grpc_helper = GuardrailsClientGRPCHelper()
        self._stub = llm_quardrail_service_pb2_grpc.GuardrailsServiceStub(self._channel)

    def validate_input(self, request: ValidateInputRequest) -> ValidateInputResponse:
        grpc_request = self._grpc_helper.build_grpc_validate_input_request(request)
        grpc_response = self._stub.ValidateInput(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_validate_input_grpc_response(grpc_response)

    def filter_output(self, request: FilterOutputRequest) -> FilterOutputResponse:
        grpc_request = self._grpc_helper.build_grpc_filter_output_request(request)
        grpc_response = self._stub.FilterOutput(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_filter_output_grpc_response(grpc_response)

    def check_policy(self, request: CheckPolicyRequest) -> CheckPolicyResponse:
        grpc_request = self._grpc_helper.build_grpc_check_policy_request(request)
        grpc_response = self._stub.CheckPolicy(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_check_policy_grpc_response(grpc_response)

    def report_violation(self, request: ReportViolationRequest) -> ReportViolationResponse:
        grpc_request = self._grpc_helper.build_grpc_report_violation_request(request)
        grpc_response = self._stub.ReportViolation(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_report_violation_grpc_response(grpc_response)
