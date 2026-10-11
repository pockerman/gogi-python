from typing import Any

from gogi.clients.base_client import BaseClient
from gogi.clients.grpc_helpers.guardrails_client_grpc_helpers import (
    GuardrailsClientGRPCHelper,
)
from gogi.models.guardrails.guardrail_policy import GuardrailPolicy, PolicyMode, PolicyType
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
from gogi.models.guardrails.violation import Violation
from gogi.v1 import llm_quardrail_service_pb2, llm_quardrail_service_pb2_grpc


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

    def add_policy(
        self,
        policy: GuardrailPolicy | None = None,
        *,
        name: str = "",
        type: PolicyType | None = None,
        rules: list[dict[str, Any]] | None = None,
        application_id: str = "",
        mode: PolicyMode = "enforce",
        description: str = "",
        version: str = "",
    ) -> AddPolicyResponse:
        """Adds a policy, or replaces the policy with the same name.

        Pass a GuardrailPolicy, or its fields as keywords:

            platform.guardrails.add_policy(
                name="travel-desk-input",
                type="input",
                application_id="travel-desk",
                rules=[{"type": "prompt_injection", "action": "block"}],
            )

        The platform checks every rule and reports every problem at once. The response's
        warnings list the rules that are accepted but not enforced yet.
        """
        if policy is None:
            policy = GuardrailPolicy(
                name=name,
                type=type,
                rules=rules or [],
                application_id=application_id,
                mode=mode,
                description=description,
                version=version,
            )

        grpc_response = self._stub.AddPolicy(
            llm_quardrail_service_pb2.AddPolicyRequest(policy=self._grpc_helper.policy_to_grpc(policy)),
            metadata=self.route_metadata,
        )
        return self._grpc_helper.serialize_add_policy_grpc_response(grpc_response)

    def get_policy(self, name: str) -> GuardrailPolicy:
        grpc_response = self._stub.GetPolicy(
            llm_quardrail_service_pb2.GetPolicyRequest(name=name), metadata=self.route_metadata
        )
        return self._grpc_helper.grpc_to_policy(grpc_response.policy)

    def list_policies(self, application_id: str = "", policy_type: str = "") -> list[GuardrailPolicy]:
        """Lists the policies of the application and type; empty matches every one."""
        grpc_response = self._stub.ListPolicies(
            llm_quardrail_service_pb2.ListPoliciesRequest(application_id=application_id, type=policy_type),
            metadata=self.route_metadata,
        )
        return [self._grpc_helper.grpc_to_policy(policy) for policy in grpc_response.policies]

    def delete_policy(self, name: str) -> bool:
        grpc_response = self._stub.DeletePolicy(
            llm_quardrail_service_pb2.DeletePolicyRequest(name=name), metadata=self.route_metadata
        )
        return grpc_response.deleted

    def list_violations(self, request: ListViolationsRequest | None = None) -> list[Violation]:
        """Lists the reported violations, newest first."""
        grpc_request = self._grpc_helper.build_grpc_list_violations_request(request or ListViolationsRequest())
        grpc_response = self._stub.ListViolations(grpc_request, metadata=self.route_metadata)
        return [self._grpc_helper.grpc_to_violation(violation) for violation in grpc_response.violations]
