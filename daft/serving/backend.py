from __future__ import annotations

import abc
import logging
from typing import Any, Callable, Dict, List, Optional, Type

from daft.env import DaftEnv
from daft.serving.definitions import Endpoint

logger = logging.getLogger(__name__)


# Default configs to use if nothing detected from user's environment
BackendConfigRaw = Dict[str, Any]
DEFAULT_CONFIGS = {"default": {"type": "docker"}}


def get_serving_backend(
    name: str = "default", configs: Optional[Dict[str, BackendConfigRaw]] = None
) -> AbstractEndpointBackend:
    # TODO(jay): Ensure that all endpoint subclasses have been imported and registered with factory - is there a better way to do this?
    pass

    # TODO(jay): Implement support for detecting configs from a user's environment (e.g. a ~/.daft.yaml file)
    if configs is None:
        configs = DEFAULT_CONFIGS
    if name not in configs:
        raise ValueError(f"Unknown backend {name}, expected one of: {list(configs.keys())}")
    return EndpointBackendFactory.create(configs[name])


class EndpointBackendFactory:

    registry: Dict[str, Type[AbstractEndpointBackend]] = {}

    @classmethod
    def register(cls, backend_class: Type[AbstractEndpointBackend]):
        cls.registry[backend_class.config_type_id()] = backend_class

    @classmethod
    def create(cls, config: Dict[str, Any]) -> AbstractEndpointBackend:
        backend_type = config["type"]
        if backend_type not in cls.registry:
            raise ValueError(f"Unknown backend type {backend_type}, expected one of {list(cls.registry.keys())}")
        return cls.registry[backend_type].from_config(config)


class AbstractEndpointBackend(abc.ABC):
    """Manages Daft Serving endpoints for a given backend"""

    def __init_subclass__(cls) -> None:
        EndpointBackendFactory.register(cls)

    @classmethod
    @abc.abstractmethod
    def from_config(cls, config: Dict[str, Any]) -> AbstractEndpointBackend:
        """Instantiates an endpoint manager for the given backend configuration"""
        ...

    @staticmethod
    @abc.abstractmethod
    def config_type_id() -> str:
        """Returns the literal string that is used to indicate that this backend is to be used in a config file"""
        ...

    @abc.abstractmethod
    def list_endpoints(self) -> List[Endpoint]:
        """Lists all endpoints managed by this endpoint manager"""
        ...

    @abc.abstractmethod
    def deploy_endpoint(
        self,
        endpoint_name: str,
        endpoint: Callable[[Any], Any],
        custom_env: Optional[DaftEnv] = None,
    ) -> Endpoint:
        """Deploys an endpoint managed by this endpoint manager"""
        ...