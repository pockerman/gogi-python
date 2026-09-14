import pytest
from unittest.mock import MagicMock

from gogi.clients.workflow_client import WorkflowClient
from gogi.clients.grpc_helpers.workflow_client_grpc_helpers import WorkflowClientGRPCHelper
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
from gogi.models.workflow.workflow_spec import WorkflowSpec
from gogi.models.workflow.scaling_config import ScalingConfig
from gogi.models.workflow.resource_config import ResourceConfig
from gogi.models.workflow.reliability_config import ReliabilityConfig


@pytest.fixture
def client():
    # Avoid calling __init__ since it creates a gRPC channel.
    client = object.__new__(WorkflowClient)
    client._grpc_helper = WorkflowClientGRPCHelper()
    client._route_metadata = ()
    client._stub = MagicMock()
    return client


def _grpc_spec(**overrides):
    defaults = dict(
        name="wf-1",
        api_path="/wf-1",
        container_image="img:latest",
        response_mode="sync",
        scaling=MagicMock(min_replicas=1, max_replicas=3, target_cpu_percent=80),
        resources=MagicMock(cpu="500m", memory="512Mi", gpu_type="", num_gpus=0),
        reliability=MagicMock(timeout_seconds=30, max_retries=2),
        version=1,
    )
    defaults.update(overrides)
    # "name" is reserved by Mock's constructor (sets the mock's repr name),
    # so it must be assigned as an attribute afterwards instead.
    name = defaults.pop("name")
    mock = MagicMock(**defaults)
    mock.name = name
    return mock


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------

def test_register_workflow_calls_stub(client):
    grpc_response = MagicMock(workflow_id="wf-1", version=1)
    client._stub.RegisterWorkflow.return_value = grpc_response

    spec = WorkflowSpec(
        name="wf-1",
        api_path="/wf-1",
        container_image="img:latest",
        response_mode="sync",
        scaling=ScalingConfig(min_replicas=1, max_replicas=3, target_cpu_percent=80),
        resources=ResourceConfig(cpu="500m", memory="512Mi"),
        reliability=ReliabilityConfig(timeout_seconds=30, max_retries=2),
    )
    response = client.register_workflow(RegisterWorkflowRequest(spec=spec))

    client._stub.RegisterWorkflow.assert_called_once()
    grpc_request = client._stub.RegisterWorkflow.call_args.args[0]
    assert grpc_request.spec.name == "wf-1"
    assert grpc_request.spec.scaling.max_replicas == 3

    assert response.workflow_id == "wf-1"
    assert response.version == 1


def test_get_workflow_calls_stub(client):
    grpc_response = MagicMock()
    grpc_response.spec = _grpc_spec()
    client._stub.GetWorkflow.return_value = grpc_response

    response = client.get_workflow(GetWorkflowRequest(name="wf-1"))

    client._stub.GetWorkflow.assert_called_once()
    grpc_request = client._stub.GetWorkflow.call_args.args[0]
    assert grpc_request.name == "wf-1"

    assert response.spec.name == "wf-1"
    assert response.spec.resources.cpu == "500m"


def test_list_workflows_calls_stub(client):
    grpc_response = MagicMock(specs=[_grpc_spec(), _grpc_spec(name="wf-2")])
    client._stub.ListWorkflows.return_value = grpc_response

    response = client.list_workflows(ListWorkflowsRequest())

    client._stub.ListWorkflows.assert_called_once()
    assert [s.name for s in response.specs] == ["wf-1", "wf-2"]


def test_update_workflow_calls_stub(client):
    grpc_response = MagicMock(version=2)
    client._stub.UpdateWorkflow.return_value = grpc_response

    spec = WorkflowSpec(name="wf-1", version=2)
    response = client.update_workflow(UpdateWorkflowRequest(spec=spec))

    client._stub.UpdateWorkflow.assert_called_once()
    assert response.version == 2


def test_delete_workflow_calls_stub(client):
    grpc_response = MagicMock(success=True)
    client._stub.DeleteWorkflow.return_value = grpc_response

    response = client.delete_workflow(DeleteWorkflowRequest(name="wf-1"))

    client._stub.DeleteWorkflow.assert_called_once()
    grpc_request = client._stub.DeleteWorkflow.call_args.args[0]
    assert grpc_request.name == "wf-1"
    assert response.success is True


# ---------------------------------------------------------------------------
# deployment
# ---------------------------------------------------------------------------

def test_deploy_workflow_calls_stub(client):
    grpc_deployment = MagicMock(
        workflow_id="wf-1", deployment_id="dep-1", version=1, status="healthy",
        current_replicas=1, desired_replicas=1, healthy_endpoints=["http://localhost:8080"],
    )
    grpc_response = MagicMock(deployment=grpc_deployment)
    client._stub.DeployWorkflow.return_value = grpc_response

    request = DeployWorkflowRequest(workflow_id="wf-1", version=1, container_id="c-1", endpoint="http://localhost:8080")
    response = client.deploy_workflow(request)

    client._stub.DeployWorkflow.assert_called_once()
    grpc_request = client._stub.DeployWorkflow.call_args.args[0]
    assert grpc_request.workflow_id == "wf-1"
    assert grpc_request.container_id == "c-1"

    assert response.deployment.status == "healthy"
    assert response.deployment.healthy_endpoints == ["http://localhost:8080"]


def test_get_deployment_status_calls_stub(client):
    grpc_deployment = MagicMock(
        workflow_id="wf-1", deployment_id="dep-1", version=1, status="deploying",
        current_replicas=0, desired_replicas=1, healthy_endpoints=[],
    )
    grpc_response = MagicMock(deployment=grpc_deployment)
    client._stub.GetDeploymentStatus.return_value = grpc_response

    response = client.get_deployment_status(GetDeploymentStatusRequest(workflow_id="wf-1"))

    client._stub.GetDeploymentStatus.assert_called_once()
    assert response.deployment.status == "deploying"


def test_rollback_workflow_calls_stub(client):
    grpc_deployment = MagicMock(
        workflow_id="wf-1", deployment_id="dep-1", version=1, status="healthy",
        current_replicas=1, desired_replicas=1, healthy_endpoints=[],
    )
    grpc_response = MagicMock(deployment=grpc_deployment)
    client._stub.RollbackWorkflow.return_value = grpc_response

    request = RollbackWorkflowRequest(workflow_id="wf-1", target_version=1)
    response = client.rollback_workflow(request)

    client._stub.RollbackWorkflow.assert_called_once()
    grpc_request = client._stub.RollbackWorkflow.call_args.args[0]
    assert grpc_request.target_version == 1
    assert response.deployment.version == 1


# ---------------------------------------------------------------------------
# routing
# ---------------------------------------------------------------------------

def test_register_route_calls_stub(client):
    grpc_response = MagicMock(success=True)
    client._stub.RegisterRoute.return_value = grpc_response

    request = RegisterRouteRequest(api_path="/wf-1", endpoint="http://localhost:8080")
    response = client.register_route(request)

    client._stub.RegisterRoute.assert_called_once()
    grpc_request = client._stub.RegisterRoute.call_args.args[0]
    assert grpc_request.api_path == "/wf-1"
    assert response.success is True


def test_list_routes_calls_stub(client):
    grpc_response = MagicMock(routes=[MagicMock(api_path="/wf-1", endpoint="http://localhost:8080")])
    client._stub.ListRoutes.return_value = grpc_response

    response = client.list_routes(ListRoutesRequest())

    client._stub.ListRoutes.assert_called_once()
    assert response.routes[0].api_path == "/wf-1"


# ---------------------------------------------------------------------------
# async jobs
# ---------------------------------------------------------------------------

def test_create_job_calls_stub(client):
    grpc_response = MagicMock(job_id="job-1")
    client._stub.CreateJob.return_value = grpc_response

    request = CreateJobRequest(workflow_id="wf-1", input_json="{}", assigned_endpoint="http://localhost:8080")
    response = client.create_job(request)

    client._stub.CreateJob.assert_called_once()
    grpc_request = client._stub.CreateJob.call_args.args[0]
    assert grpc_request.workflow_id == "wf-1"
    assert response.job_id == "job-1"


def test_get_job_status_calls_stub(client):
    grpc_job = MagicMock(
        job_id="job-1", workflow_id="wf-1", status="running", progress_message="halfway",
        input_json="{}", result_json="", error="", checkpoint_json="", assigned_endpoint="",
        created_at=1, updated_at=2,
    )
    grpc_response = MagicMock(job=grpc_job)
    client._stub.GetJobStatus.return_value = grpc_response

    response = client.get_job_status(GetJobStatusRequest(job_id="job-1"))

    client._stub.GetJobStatus.assert_called_once()
    assert response.job.status == "running"
    assert response.job.progress_message == "halfway"


def test_update_job_progress_calls_stub(client):
    grpc_response = MagicMock(success=True)
    client._stub.UpdateJobProgress.return_value = grpc_response

    request = UpdateJobProgressRequest(job_id="job-1", progress_message="50%")
    response = client.update_job_progress(request)

    client._stub.UpdateJobProgress.assert_called_once()
    grpc_request = client._stub.UpdateJobProgress.call_args.args[0]
    assert grpc_request.progress_message == "50%"
    assert response.success is True


def test_save_job_checkpoint_calls_stub(client):
    grpc_response = MagicMock(success=True)
    client._stub.SaveJobCheckpoint.return_value = grpc_response

    request = SaveJobCheckpointRequest(job_id="job-1", checkpoint_json='{"step": 1}')
    response = client.save_job_checkpoint(request)

    client._stub.SaveJobCheckpoint.assert_called_once()
    grpc_request = client._stub.SaveJobCheckpoint.call_args.args[0]
    assert grpc_request.checkpoint_json == '{"step": 1}'
    assert response.success is True


def test_complete_job_calls_stub(client):
    grpc_response = MagicMock(success=True)
    client._stub.CompleteJob.return_value = grpc_response

    request = CompleteJobRequest(job_id="job-1", result_json='{"ok": true}')
    response = client.complete_job(request)

    client._stub.CompleteJob.assert_called_once()
    assert response.success is True


def test_fail_job_calls_stub(client):
    grpc_response = MagicMock(success=True)
    client._stub.FailJob.return_value = grpc_response

    request = FailJobRequest(job_id="job-1", error="boom")
    response = client.fail_job(request)

    client._stub.FailJob.assert_called_once()
    grpc_request = client._stub.FailJob.call_args.args[0]
    assert grpc_request.error == "boom"
    assert response.success is True


def test_cancel_job_calls_stub(client):
    grpc_response = MagicMock(success=True)
    client._stub.CancelJob.return_value = grpc_response

    response = client.cancel_job(CancelJobRequest(job_id="job-1"))

    client._stub.CancelJob.assert_called_once()
    grpc_request = client._stub.CancelJob.call_args.args[0]
    assert grpc_request.job_id == "job-1"
    assert response.success is True
