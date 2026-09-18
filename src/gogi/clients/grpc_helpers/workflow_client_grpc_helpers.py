from gogi.models.workflow.requests.cancel_job_request import CancelJobRequest
from gogi.models.workflow.requests.complete_job_request import CompleteJobRequest
from gogi.models.workflow.requests.create_job_request import CreateJobRequest
from gogi.models.workflow.requests.delete_workflow_request import DeleteWorkflowRequest
from gogi.models.workflow.requests.deploy_workflow_request import DeployWorkflowRequest
from gogi.models.workflow.requests.fail_job_request import FailJobRequest
from gogi.models.workflow.requests.get_deployment_status_request import (
    GetDeploymentStatusRequest,
)
from gogi.models.workflow.requests.get_job_status_request import GetJobStatusRequest
from gogi.models.workflow.requests.get_workflow_request import GetWorkflowRequest
from gogi.models.workflow.requests.list_routes_request import ListRoutesRequest
from gogi.models.workflow.requests.list_workflows_request import ListWorkflowsRequest
from gogi.models.workflow.requests.register_route_request import RegisterRouteRequest
from gogi.models.workflow.requests.register_workflow_request import (
    RegisterWorkflowRequest,
)
from gogi.models.workflow.requests.rollback_workflow_request import (
    RollbackWorkflowRequest,
)
from gogi.models.workflow.requests.save_job_checkpoint_request import (
    SaveJobCheckpointRequest,
)
from gogi.models.workflow.requests.update_job_progress_request import (
    UpdateJobProgressRequest,
)
from gogi.models.workflow.requests.update_workflow_request import UpdateWorkflowRequest
from gogi.models.workflow.responses.cancel_job_response import CancelJobResponse
from gogi.models.workflow.responses.complete_job_response import CompleteJobResponse
from gogi.models.workflow.responses.create_job_response import CreateJobResponse
from gogi.models.workflow.responses.delete_workflow_response import (
    DeleteWorkflowResponse,
)
from gogi.models.workflow.responses.deploy_workflow_response import (
    DeployWorkflowResponse,
)
from gogi.models.workflow.responses.fail_job_response import FailJobResponse
from gogi.models.workflow.responses.get_deployment_status_response import (
    GetDeploymentStatusResponse,
)
from gogi.models.workflow.responses.get_job_status_response import GetJobStatusResponse
from gogi.models.workflow.responses.get_workflow_response import GetWorkflowResponse
from gogi.models.workflow.responses.list_routes_response import ListRoutesResponse
from gogi.models.workflow.responses.list_workflows_response import ListWorkflowsResponse
from gogi.models.workflow.responses.register_route_response import RegisterRouteResponse
from gogi.models.workflow.responses.register_workflow_response import (
    RegisterWorkflowResponse,
)
from gogi.models.workflow.responses.rollback_workflow_response import (
    RollbackWorkflowResponse,
)
from gogi.models.workflow.responses.save_job_checkpoint_response import (
    SaveJobCheckpointResponse,
)
from gogi.models.workflow.responses.update_job_progress_response import (
    UpdateJobProgressResponse,
)
from gogi.models.workflow.responses.update_workflow_response import (
    UpdateWorkflowResponse,
)
from gogi.models.workflow.route import Route
from gogi.models.workflow.workflow_deployment import WorkflowDeployment
from gogi.models.workflow.workflow_job import WorkflowJob
from gogi.models.workflow.workflow_spec import WorkflowSpec
from gogi.v1 import workflow_service_pb2


class WorkflowClientGRPCHelper:
    # --- shared message builders ---

    @staticmethod
    def build_grpc_workflow_spec(spec: WorkflowSpec) -> workflow_service_pb2.WorkflowSpec:
        return workflow_service_pb2.WorkflowSpec(
            name=spec.name,
            api_path=spec.api_path,
            container_image=spec.container_image,
            response_mode=spec.response_mode,
            scaling=workflow_service_pb2.ScalingConfig(
                min_replicas=spec.scaling.min_replicas,
                max_replicas=spec.scaling.max_replicas,
                target_cpu_percent=spec.scaling.target_cpu_percent,
            ),
            resources=workflow_service_pb2.ResourceConfig(
                cpu=spec.resources.cpu,
                memory=spec.resources.memory,
                gpu_type=spec.resources.gpu_type,
                num_gpus=spec.resources.num_gpus,
            ),
            reliability=workflow_service_pb2.ReliabilityConfig(
                timeout_seconds=spec.reliability.timeout_seconds,
                max_retries=spec.reliability.max_retries,
            ),
            version=spec.version,
        )

    @staticmethod
    def serialize_grpc_workflow_spec(grpc_spec: workflow_service_pb2.WorkflowSpec) -> WorkflowSpec:
        return WorkflowSpec(
            name=grpc_spec.name,
            api_path=grpc_spec.api_path,
            container_image=grpc_spec.container_image,
            response_mode=grpc_spec.response_mode,
            scaling={
                "min_replicas": grpc_spec.scaling.min_replicas,
                "max_replicas": grpc_spec.scaling.max_replicas,
                "target_cpu_percent": grpc_spec.scaling.target_cpu_percent,
            },
            resources={
                "cpu": grpc_spec.resources.cpu,
                "memory": grpc_spec.resources.memory,
                "gpu_type": grpc_spec.resources.gpu_type,
                "num_gpus": grpc_spec.resources.num_gpus,
            },
            reliability={
                "timeout_seconds": grpc_spec.reliability.timeout_seconds,
                "max_retries": grpc_spec.reliability.max_retries,
            },
            version=grpc_spec.version,
        )

    @staticmethod
    def serialize_grpc_deployment(grpc_deployment: workflow_service_pb2.WorkflowDeployment) -> WorkflowDeployment:
        return WorkflowDeployment(
            workflow_id=grpc_deployment.workflow_id,
            deployment_id=grpc_deployment.deployment_id,
            version=grpc_deployment.version,
            status=grpc_deployment.status,
            current_replicas=grpc_deployment.current_replicas,
            desired_replicas=grpc_deployment.desired_replicas,
            healthy_endpoints=list(grpc_deployment.healthy_endpoints),
        )

    @staticmethod
    def serialize_grpc_job(grpc_job: workflow_service_pb2.WorkflowJob) -> WorkflowJob:
        return WorkflowJob(
            job_id=grpc_job.job_id,
            workflow_id=grpc_job.workflow_id,
            status=grpc_job.status,
            progress_message=grpc_job.progress_message,
            input_json=grpc_job.input_json,
            result_json=grpc_job.result_json,
            error=grpc_job.error,
            checkpoint_json=grpc_job.checkpoint_json,
            assigned_endpoint=grpc_job.assigned_endpoint,
            created_at=grpc_job.created_at,
            updated_at=grpc_job.updated_at,
        )

    # --- RegisterWorkflow ---

    @staticmethod
    def build_grpc_register_workflow_request(
        request: RegisterWorkflowRequest,
    ) -> workflow_service_pb2.RegisterWorkflowRequest:
        return workflow_service_pb2.RegisterWorkflowRequest(
            spec=WorkflowClientGRPCHelper.build_grpc_workflow_spec(request.spec),
        )

    @staticmethod
    def serialize_register_workflow_grpc_response(
        grpc_response: workflow_service_pb2.RegisterWorkflowResponse,
    ) -> RegisterWorkflowResponse:
        return RegisterWorkflowResponse(
            workflow_id=grpc_response.workflow_id,
            version=grpc_response.version,
        )

    # --- GetWorkflow ---

    @staticmethod
    def build_grpc_get_workflow_request(request: GetWorkflowRequest) -> workflow_service_pb2.GetWorkflowRequest:
        return workflow_service_pb2.GetWorkflowRequest(name=request.name)

    @staticmethod
    def serialize_get_workflow_grpc_response(
        grpc_response: workflow_service_pb2.GetWorkflowResponse,
    ) -> GetWorkflowResponse:
        return GetWorkflowResponse(
            spec=WorkflowClientGRPCHelper.serialize_grpc_workflow_spec(grpc_response.spec),
        )

    # --- ListWorkflows ---

    @staticmethod
    def build_grpc_list_workflows_request(request: ListWorkflowsRequest) -> workflow_service_pb2.ListWorkflowsRequest:
        return workflow_service_pb2.ListWorkflowsRequest()

    @staticmethod
    def serialize_list_workflows_grpc_response(
        grpc_response: workflow_service_pb2.ListWorkflowsResponse,
    ) -> ListWorkflowsResponse:
        return ListWorkflowsResponse(
            specs=[WorkflowClientGRPCHelper.serialize_grpc_workflow_spec(spec) for spec in grpc_response.specs],
        )

    # --- UpdateWorkflow ---

    @staticmethod
    def build_grpc_update_workflow_request(
        request: UpdateWorkflowRequest,
    ) -> workflow_service_pb2.UpdateWorkflowRequest:
        return workflow_service_pb2.UpdateWorkflowRequest(
            spec=WorkflowClientGRPCHelper.build_grpc_workflow_spec(request.spec),
        )

    @staticmethod
    def serialize_update_workflow_grpc_response(
        grpc_response: workflow_service_pb2.UpdateWorkflowResponse,
    ) -> UpdateWorkflowResponse:
        return UpdateWorkflowResponse(version=grpc_response.version)

    # --- DeleteWorkflow ---

    @staticmethod
    def build_grpc_delete_workflow_request(
        request: DeleteWorkflowRequest,
    ) -> workflow_service_pb2.DeleteWorkflowRequest:
        return workflow_service_pb2.DeleteWorkflowRequest(name=request.name)

    @staticmethod
    def serialize_delete_workflow_grpc_response(
        grpc_response: workflow_service_pb2.DeleteWorkflowResponse,
    ) -> DeleteWorkflowResponse:
        return DeleteWorkflowResponse(success=grpc_response.success)

    # --- DeployWorkflow ---

    @staticmethod
    def build_grpc_deploy_workflow_request(
        request: DeployWorkflowRequest,
    ) -> workflow_service_pb2.DeployWorkflowRequest:
        return workflow_service_pb2.DeployWorkflowRequest(
            workflow_id=request.workflow_id,
            version=request.version,
            container_id=request.container_id,
            endpoint=request.endpoint,
        )

    @staticmethod
    def serialize_deploy_workflow_grpc_response(
        grpc_response: workflow_service_pb2.DeployWorkflowResponse,
    ) -> DeployWorkflowResponse:
        return DeployWorkflowResponse(
            deployment=WorkflowClientGRPCHelper.serialize_grpc_deployment(grpc_response.deployment),
        )

    # --- GetDeploymentStatus ---

    @staticmethod
    def build_grpc_get_deployment_status_request(
        request: GetDeploymentStatusRequest,
    ) -> workflow_service_pb2.GetDeploymentStatusRequest:
        return workflow_service_pb2.GetDeploymentStatusRequest(workflow_id=request.workflow_id)

    @staticmethod
    def serialize_get_deployment_status_grpc_response(
        grpc_response: workflow_service_pb2.GetDeploymentStatusResponse,
    ) -> GetDeploymentStatusResponse:
        return GetDeploymentStatusResponse(
            deployment=WorkflowClientGRPCHelper.serialize_grpc_deployment(grpc_response.deployment),
        )

    # --- RollbackWorkflow ---

    @staticmethod
    def build_grpc_rollback_workflow_request(
        request: RollbackWorkflowRequest,
    ) -> workflow_service_pb2.RollbackWorkflowRequest:
        return workflow_service_pb2.RollbackWorkflowRequest(
            workflow_id=request.workflow_id,
            target_version=request.target_version,
        )

    @staticmethod
    def serialize_rollback_workflow_grpc_response(
        grpc_response: workflow_service_pb2.RollbackWorkflowResponse,
    ) -> RollbackWorkflowResponse:
        return RollbackWorkflowResponse(
            deployment=WorkflowClientGRPCHelper.serialize_grpc_deployment(grpc_response.deployment),
        )

    # --- RegisterRoute ---

    @staticmethod
    def build_grpc_register_route_request(request: RegisterRouteRequest) -> workflow_service_pb2.RegisterRouteRequest:
        return workflow_service_pb2.RegisterRouteRequest(
            api_path=request.api_path,
            endpoint=request.endpoint,
        )

    @staticmethod
    def serialize_register_route_grpc_response(
        grpc_response: workflow_service_pb2.RegisterRouteResponse,
    ) -> RegisterRouteResponse:
        return RegisterRouteResponse(success=grpc_response.success)

    # --- ListRoutes ---

    @staticmethod
    def build_grpc_list_routes_request(request: ListRoutesRequest) -> workflow_service_pb2.ListRoutesRequest:
        return workflow_service_pb2.ListRoutesRequest()

    @staticmethod
    def serialize_list_routes_grpc_response(
        grpc_response: workflow_service_pb2.ListRoutesResponse,
    ) -> ListRoutesResponse:
        return ListRoutesResponse(
            routes=[Route(api_path=route.api_path, endpoint=route.endpoint) for route in grpc_response.routes],
        )

    # --- CreateJob ---

    @staticmethod
    def build_grpc_create_job_request(request: CreateJobRequest) -> workflow_service_pb2.CreateJobRequest:
        return workflow_service_pb2.CreateJobRequest(
            workflow_id=request.workflow_id,
            input_json=request.input_json,
            assigned_endpoint=request.assigned_endpoint,
        )

    @staticmethod
    def serialize_create_job_grpc_response(grpc_response: workflow_service_pb2.CreateJobResponse) -> CreateJobResponse:
        return CreateJobResponse(job_id=grpc_response.job_id)

    # --- GetJobStatus ---

    @staticmethod
    def build_grpc_get_job_status_request(request: GetJobStatusRequest) -> workflow_service_pb2.GetJobStatusRequest:
        return workflow_service_pb2.GetJobStatusRequest(job_id=request.job_id)

    @staticmethod
    def serialize_get_job_status_grpc_response(
        grpc_response: workflow_service_pb2.GetJobStatusResponse,
    ) -> GetJobStatusResponse:
        return GetJobStatusResponse(
            job=WorkflowClientGRPCHelper.serialize_grpc_job(grpc_response.job),
        )

    # --- UpdateJobProgress ---

    @staticmethod
    def build_grpc_update_job_progress_request(
        request: UpdateJobProgressRequest,
    ) -> workflow_service_pb2.UpdateJobProgressRequest:
        return workflow_service_pb2.UpdateJobProgressRequest(
            job_id=request.job_id,
            progress_message=request.progress_message,
        )

    @staticmethod
    def serialize_update_job_progress_grpc_response(
        grpc_response: workflow_service_pb2.UpdateJobProgressResponse,
    ) -> UpdateJobProgressResponse:
        return UpdateJobProgressResponse(success=grpc_response.success)

    # --- SaveJobCheckpoint ---

    @staticmethod
    def build_grpc_save_job_checkpoint_request(
        request: SaveJobCheckpointRequest,
    ) -> workflow_service_pb2.SaveJobCheckpointRequest:
        return workflow_service_pb2.SaveJobCheckpointRequest(
            job_id=request.job_id,
            checkpoint_json=request.checkpoint_json,
        )

    @staticmethod
    def serialize_save_job_checkpoint_grpc_response(
        grpc_response: workflow_service_pb2.SaveJobCheckpointResponse,
    ) -> SaveJobCheckpointResponse:
        return SaveJobCheckpointResponse(success=grpc_response.success)

    # --- CompleteJob ---

    @staticmethod
    def build_grpc_complete_job_request(request: CompleteJobRequest) -> workflow_service_pb2.CompleteJobRequest:
        return workflow_service_pb2.CompleteJobRequest(
            job_id=request.job_id,
            result_json=request.result_json,
        )

    @staticmethod
    def serialize_complete_job_grpc_response(
        grpc_response: workflow_service_pb2.CompleteJobResponse,
    ) -> CompleteJobResponse:
        return CompleteJobResponse(success=grpc_response.success)

    # --- FailJob ---

    @staticmethod
    def build_grpc_fail_job_request(request: FailJobRequest) -> workflow_service_pb2.FailJobRequest:
        return workflow_service_pb2.FailJobRequest(
            job_id=request.job_id,
            error=request.error,
        )

    @staticmethod
    def serialize_fail_job_grpc_response(grpc_response: workflow_service_pb2.FailJobResponse) -> FailJobResponse:
        return FailJobResponse(success=grpc_response.success)

    # --- CancelJob ---

    @staticmethod
    def build_grpc_cancel_job_request(request: CancelJobRequest) -> workflow_service_pb2.CancelJobRequest:
        return workflow_service_pb2.CancelJobRequest(job_id=request.job_id)

    @staticmethod
    def serialize_cancel_job_grpc_response(grpc_response: workflow_service_pb2.CancelJobResponse) -> CancelJobResponse:
        return CancelJobResponse(success=grpc_response.success)
