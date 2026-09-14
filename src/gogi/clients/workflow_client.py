from gogi.models.workflow.requests.cancel_job_request import CancelJobRequest
from gogi.models.workflow.requests.complete_job_request import CompleteJobRequest
from gogi.models.workflow.requests.create_job_request import CreateJobRequest
from gogi.models.workflow.requests.delete_workflow_request import DeleteWorkflowRequest
from gogi.models.workflow.requests.deploy_workflow_request import DeployWorkflowRequest
from gogi.models.workflow.requests.fail_job_request import FailJobRequest
from gogi.models.workflow.requests.get_deployment_status_request import GetDeploymentStatusRequest
from gogi.models.workflow.requests.get_job_status_request import GetJobStatusRequest
from gogi.models.workflow.requests.get_workflow_request import GetWorkflowRequest
from gogi.models.workflow.requests.list_routes_request import ListRoutesRequest
from gogi.models.workflow.requests.list_workflows_request import ListWorkflowsRequest
from gogi.models.workflow.requests.register_route_request import RegisterRouteRequest
from gogi.models.workflow.requests.register_workflow_request import RegisterWorkflowRequest
from gogi.models.workflow.requests.rollback_workflow_request import RollbackWorkflowRequest
from gogi.models.workflow.requests.save_job_checkpoint_request import SaveJobCheckpointRequest
from gogi.models.workflow.requests.update_job_progress_request import UpdateJobProgressRequest
from gogi.models.workflow.requests.update_workflow_request import UpdateWorkflowRequest

from gogi.models.workflow.responses.cancel_job_response import CancelJobResponse
from gogi.models.workflow.responses.complete_job_response import CompleteJobResponse
from gogi.models.workflow.responses.create_job_response import CreateJobResponse
from gogi.models.workflow.responses.delete_workflow_response import DeleteWorkflowResponse
from gogi.models.workflow.responses.deploy_workflow_response import DeployWorkflowResponse
from gogi.models.workflow.responses.fail_job_response import FailJobResponse
from gogi.models.workflow.responses.get_deployment_status_response import GetDeploymentStatusResponse
from gogi.models.workflow.responses.get_job_status_response import GetJobStatusResponse
from gogi.models.workflow.responses.get_workflow_response import GetWorkflowResponse
from gogi.models.workflow.responses.list_routes_response import ListRoutesResponse
from gogi.models.workflow.responses.list_workflows_response import ListWorkflowsResponse
from gogi.models.workflow.responses.register_route_response import RegisterRouteResponse
from gogi.models.workflow.responses.register_workflow_response import RegisterWorkflowResponse
from gogi.models.workflow.responses.rollback_workflow_response import RollbackWorkflowResponse
from gogi.models.workflow.responses.save_job_checkpoint_response import SaveJobCheckpointResponse
from gogi.models.workflow.responses.update_job_progress_response import UpdateJobProgressResponse
from gogi.models.workflow.responses.update_workflow_response import UpdateWorkflowResponse

from gogi.v1 import workflow_service_pb2_grpc
from gogi.clients.base_client import BaseClient
from gogi.clients.grpc_helpers.workflow_client_grpc_helpers import WorkflowClientGRPCHelper


class WorkflowClient(BaseClient):
    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="workflows", logger=logger)
        self._grpc_helper = WorkflowClientGRPCHelper()
        self._stub = workflow_service_pb2_grpc.WorkflowServerStub(self._channel)

    # --- Registry ---

    def register_workflow(self, request: RegisterWorkflowRequest) -> RegisterWorkflowResponse:
        grpc_request = self._grpc_helper.build_grpc_register_workflow_request(request)
        grpc_response = self._stub.RegisterWorkflow(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_register_workflow_grpc_response(grpc_response)

    def get_workflow(self, request: GetWorkflowRequest) -> GetWorkflowResponse:
        grpc_request = self._grpc_helper.build_grpc_get_workflow_request(request)
        grpc_response = self._stub.GetWorkflow(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_get_workflow_grpc_response(grpc_response)

    def list_workflows(self, request: ListWorkflowsRequest) -> ListWorkflowsResponse:
        grpc_request = self._grpc_helper.build_grpc_list_workflows_request(request)
        grpc_response = self._stub.ListWorkflows(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_list_workflows_grpc_response(grpc_response)

    def update_workflow(self, request: UpdateWorkflowRequest) -> UpdateWorkflowResponse:
        grpc_request = self._grpc_helper.build_grpc_update_workflow_request(request)
        grpc_response = self._stub.UpdateWorkflow(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_update_workflow_grpc_response(grpc_response)

    def delete_workflow(self, request: DeleteWorkflowRequest) -> DeleteWorkflowResponse:
        grpc_request = self._grpc_helper.build_grpc_delete_workflow_request(request)
        grpc_response = self._stub.DeleteWorkflow(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_delete_workflow_grpc_response(grpc_response)

    # --- Deployment ---

    def deploy_workflow(self, request: DeployWorkflowRequest) -> DeployWorkflowResponse:
        grpc_request = self._grpc_helper.build_grpc_deploy_workflow_request(request)
        grpc_response = self._stub.DeployWorkflow(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_deploy_workflow_grpc_response(grpc_response)

    def get_deployment_status(self, request: GetDeploymentStatusRequest) -> GetDeploymentStatusResponse:
        grpc_request = self._grpc_helper.build_grpc_get_deployment_status_request(request)
        grpc_response = self._stub.GetDeploymentStatus(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_get_deployment_status_grpc_response(grpc_response)

    def rollback_workflow(self, request: RollbackWorkflowRequest) -> RollbackWorkflowResponse:
        grpc_request = self._grpc_helper.build_grpc_rollback_workflow_request(request)
        grpc_response = self._stub.RollbackWorkflow(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_rollback_workflow_grpc_response(grpc_response)

    # --- Routing ---

    def register_route(self, request: RegisterRouteRequest) -> RegisterRouteResponse:
        grpc_request = self._grpc_helper.build_grpc_register_route_request(request)
        grpc_response = self._stub.RegisterRoute(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_register_route_grpc_response(grpc_response)

    def list_routes(self, request: ListRoutesRequest) -> ListRoutesResponse:
        grpc_request = self._grpc_helper.build_grpc_list_routes_request(request)
        grpc_response = self._stub.ListRoutes(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_list_routes_grpc_response(grpc_response)

    # --- Async jobs ---

    def create_job(self, request: CreateJobRequest) -> CreateJobResponse:
        grpc_request = self._grpc_helper.build_grpc_create_job_request(request)
        grpc_response = self._stub.CreateJob(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_create_job_grpc_response(grpc_response)

    def get_job_status(self, request: GetJobStatusRequest) -> GetJobStatusResponse:
        grpc_request = self._grpc_helper.build_grpc_get_job_status_request(request)
        grpc_response = self._stub.GetJobStatus(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_get_job_status_grpc_response(grpc_response)

    def update_job_progress(self, request: UpdateJobProgressRequest) -> UpdateJobProgressResponse:
        grpc_request = self._grpc_helper.build_grpc_update_job_progress_request(request)
        grpc_response = self._stub.UpdateJobProgress(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_update_job_progress_grpc_response(grpc_response)

    def save_job_checkpoint(self, request: SaveJobCheckpointRequest) -> SaveJobCheckpointResponse:
        grpc_request = self._grpc_helper.build_grpc_save_job_checkpoint_request(request)
        grpc_response = self._stub.SaveJobCheckpoint(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_save_job_checkpoint_grpc_response(grpc_response)

    def complete_job(self, request: CompleteJobRequest) -> CompleteJobResponse:
        grpc_request = self._grpc_helper.build_grpc_complete_job_request(request)
        grpc_response = self._stub.CompleteJob(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_complete_job_grpc_response(grpc_response)

    def fail_job(self, request: FailJobRequest) -> FailJobResponse:
        grpc_request = self._grpc_helper.build_grpc_fail_job_request(request)
        grpc_response = self._stub.FailJob(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_fail_job_grpc_response(grpc_response)

    def cancel_job(self, request: CancelJobRequest) -> CancelJobResponse:
        grpc_request = self._grpc_helper.build_grpc_cancel_job_request(request)
        grpc_response = self._stub.CancelJob(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_cancel_job_grpc_response(grpc_response)
