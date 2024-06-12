from kubernetes import client, config

class KubernetesClient:
    def __init__(self) -> None:
        # Load in-cluster configuration
        config.load_incluster_config()
        self.__service_count = 0

    def create_service(self, port):
        v1 = client.CoreV1Api()

        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(name=f"plebi-service-{self.__service_count}"),
            spec=client.V1ServiceSpec(
                selector={"app": "Plebiscito"},
                type="NodePort",
                ports=[client.V1ServicePort(port=int(port), target_port=int(port), node_port=int(port))]
            )
        )

        v1.create_namespaced_service(namespace="default", body=service)
        self.__service_count += 1