from typing import Optional

from daft.env import DaftEnv
from daft.logical.logical_plan import HTTPResponse, LogicalPlan
from daft.logical.schema import ExpressionList
from daft.serving.backend import AbstractEndpointBackend, get_serving_backend
from daft.serving.definitions import Endpoint


class HTTPEndpoint:
    """A HTTP Endpoint that can be configured to run the same logic as a DataFrame, and be deployed onto various backends"""

    def __init__(self, request_schema: ExpressionList):
        self._request_schema = request_schema
        self._plan: Optional[LogicalPlan] = None

    def _set_plan(self, plan: LogicalPlan) -> None:
        if self._plan is not None:
            raise ValueError("Unable to .set_plan more than once on the same HTTPEndpoint")
        self._plan = HTTPResponse(input=plan)
        return

    def deploy(
        self,
        endpoint_name: str,
        backend: Optional[AbstractEndpointBackend] = None,
        custom_env: Optional[DaftEnv] = None,
    ) -> Endpoint:
        if self._plan is None:
            raise RuntimeError("Unable to deploy HTTPEndpoint without a plan")

        resolved_backend = backend if backend is not None else get_serving_backend()

        # TODO(jay): In the absence of a runner, we deploy whatever the ._plan is as a function. This is a hack and
        # is only meant to be used in unit tests by monkey-patching ._plan for now to test the e2e flow.
        if isinstance(self._plan, LogicalPlan):
            raise RuntimeError("HTTPEndpoint unable to deploy LogicalPlans until runners are implemented")
        endpoint_func = self._plan

        return resolved_backend.deploy_endpoint(endpoint_name, endpoint_func, custom_env=custom_env)