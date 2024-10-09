from kubernetes import client, config
from jinja2 import Template
import yaml

class KubernetesClient:
    def __init__(self) -> None:
        # Load in-cluster configuration
        config.load_incluster_config()
        self.__service_count = 0
        
    def deploy_book_application(self, allocation):
        if len(allocation) != 3:
            print("Error: Allocation must be of length 3")
            return
        
        for i, node_id in enumerate(allocation):
            if i == 0:
                with open('deploy/k8s/productpage.yaml') as file_:
                    template_content = file_.read()
            elif i == 1:
                with open('deploy/k8s/reviews.yaml') as file_:
                    template_content = file_.read()
            else:
                with open('deploy/k8s/ratings.yaml') as file_:
                    template_content = file_.read()
                    
            # Define the node name you want to assign dynamically
            context = {
                'node_name': node_id  # Example node name
            }

            # Render the YAML template using Jinja2
            template = Template(template_content)
            rendered_yaml = template.render(context)

            # Parse the rendered YAML into a Python object
            resource = yaml.safe_load(rendered_yaml)

            # Create the Kubernetes AppsV1 API client
            apps_v1_api = client.AppsV1Api()

            # Apply the Deployment resource to the cluster
            try:
                apps_v1_api.create_namespaced_deployment(
                    namespace='default',  # Change to your desired namespace
                    body=resource
                )
                print("Deployment successfully applied to node:", context['node_name'])
            except client.exceptions.ApiException as e:
                print(f"Error occurred: {e}")

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