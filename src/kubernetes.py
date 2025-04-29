from kubernetes import client, config
from kubernetes.utils import create_from_dict
from jinja2 import Template
import yaml

class KubernetesClient:
    def __init__(self) -> None:
        # Load in-cluster configuration
        config.load_incluster_config()
        self.__service_count = 0

    def __add_namespace(self, resource, target_namespace):
        if 'metadata' in resource:
            if 'namespace' not in resource['metadata']:
                # If no namespace is specified, set the target namespace
                resource['metadata']['namespace'] = target_namespace
            else:
                # Optionally, you can enforce the target namespace if needed
                resource['metadata']['namespace'] = target_namespace

    def deploy_iperf_application(self, allocation, job_id, cpus):
        target_namespace = 'offloaded-namespace'

        deployment_content = None
        service_content = None
        
        for i, node_id in enumerate(allocation):
            deployment_content = None
            service_content = None

            if i == 0:
                with open('deploy/k8s/iperf_server.yaml') as file_:
                    deployment_content = file_.read()
                with open('deploy/k8s/iperf_server_svc.yaml') as file_:
                    service_content = file_.read()
            else:
                with open('deploy/k8s/iperf_client.yaml') as file_:
                    deployment_content = file_.read()

            if service_content is not None:
                template = Template(deployment_content)
                deployment_content = template.render(node_name=str(node_id), dep_name=f"iperf-server-{job_id}", cpu_assigned=str(cpus[i]), num_workers=str(len(allocation) - 1))
                deployment_content = yaml.safe_load(deployment_content)

                template2 = Template(service_content)
                service_content = template2.render(svc_name=f"iperf-server-svc-{job_id}", dep_name=f"iperf-server-{job_id}")
                service_content = yaml.safe_load(service_content)
            else:
                template = Template(deployment_content)
                deployment_content = template.render(node_name=str(node_id), worker_id=str(i-1), ps_host=f"iperf-server-svc-{job_id}.{target_namespace}.svc.cluster.local", dep_name=f"iperf-client-{job_id}-{str(i-1)}", cpu_assigned=str(cpus[i]))
                deployment_content = yaml.safe_load(deployment_content)

            # Create the Kubernetes AppsV1 API client
            apps_v1_api = client.AppsV1Api()
            core_v1_api = client.CoreV1Api()

            # Apply the Deployment resource to the cluster
            try:
                apps_v1_api.create_namespaced_deployment(
                    namespace=target_namespace,  # Change to your desired namespace
                    body=deployment_content
                )
                #print(f"Deployment ({i}) successfully applied", flush=True)
            except Exception as e:
                print(f"Error occurred: {e}", flush=True)

            if service_content is not None:
                try:
                    core_v1_api.create_namespaced_service(
                        namespace=target_namespace,  # Change to your desired namespace
                        body=service_content
                    )
                    #print(f"Service successfully applied", flush=True)
                except Exception as e:
                    print(f"Error occurred: {e}", flush=True)

    def deploy_flower_application(self, allocation, job_id, cpus):
        target_namespace = 'offloaded-namespace'
        
        deployment_content = None
        service_content = None
        
        for i, node_id in enumerate(allocation):
            deployment_content = None
            service_content = None

            if i == 0:
                with open('deploy/k8s/flower_server.yaml') as file_:
                    deployment_content = file_.read()
                with open('deploy/k8s/flower_server_svc.yaml') as file_:
                    service_content = file_.read()
            else:
                with open('deploy/k8s/flower_client.yaml') as file_:
                    deployment_content = file_.read()

            if service_content is not None:
                template = Template(deployment_content)
                deployment_content = template.render(node_name=str(node_id), dep_name=f"flower-server-{job_id}", cpu_assigned=str(cpus[i]))
                deployment_content = yaml.safe_load(deployment_content)

                template2 = Template(service_content)
                service_content = template2.render(svc_name=f"flower-server-svc-{job_id}", dep_name=f"flower-server-{job_id}")
                service_content = yaml.safe_load(service_content)
            else:
                template = Template(deployment_content)
                deployment_content = template.render(node_name=str(node_id), partition_id=str(i-1), server_ip=f"flower-server-svc-{job_id}.{target_namespace}.svc.cluster.local", dep_name=f"flower-client-{job_id}-{str(i-1)}", cpu_assigned=str(cpus[i]))
                deployment_content = yaml.safe_load(deployment_content)

            # Create the Kubernetes AppsV1 API client
            apps_v1_api = client.AppsV1Api()
            core_v1_api = client.CoreV1Api()

            # Apply the Deployment resource to the cluster
            try:
                apps_v1_api.create_namespaced_deployment(
                    namespace=target_namespace,  # Change to your desired namespace
                    body=deployment_content
                )
                print(f"Deployment ({i}) successfully applied", flush=True)
            except Exception as e:
                print(f"Error occurred: {e}", flush=True)

            if service_content is not None:
                try:
                    core_v1_api.create_namespaced_service(
                        namespace=target_namespace,  # Change to your desired namespace
                        body=service_content
                    )
                    print(f"Service successfully applied", flush=True)
                except Exception as e:
                    print(f"Error occurred: {e}", flush=True)

            

        
    def deploy_book_application(self, allocation):
        target_namespace = 'offloaded-namespace'

        if len(allocation) != 3:
            print("Error: Allocation must be of length 3")
            return
        
        for i, node_id in enumerate(allocation):
            if i == 0:
                with open('deploy/k8s/productpage.yaml') as file_:
                    template_content = file_.read()
                with open('deploy/k8s/productpage_svc.yaml') as file_:
                    service_content = yaml.load(file_, Loader=yaml.SafeLoader)
                with open('deploy/k8s/productpage_svcacc.yaml') as file_:
                    service_account_content = yaml.load(file_, Loader=yaml.SafeLoader)
            elif i == 1:
                with open('deploy/k8s/reviews.yaml') as file_:
                    template_content = file_.read()
                with open('deploy/k8s/reviews_svc.yaml') as file_:
                    service_content = yaml.load(file_, Loader=yaml.SafeLoader)
                with open('deploy/k8s/reviews_svcacc.yaml') as file_:
                    service_account_content = yaml.load(file_, Loader=yaml.SafeLoader)
            else:
                with open('deploy/k8s/ratings.yaml') as file_:
                    template_content = file_.read()
                with open('deploy/k8s/ratings_svc.yaml') as file_:
                    service_content = yaml.load(file_, Loader=yaml.SafeLoader)
                with open('deploy/k8s/ratings_svcacc.yaml') as file_:
                    service_account_content = yaml.load(file_, Loader=yaml.SafeLoader)

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
            k8s_client = client.ApiClient()

            # Apply the Deployment resource to the cluster
            try:
                apps_v1_api.create_namespaced_deployment(
                    namespace=target_namespace,  # Change to your desired namespace
                    body=resource
                )
                print(f"Deployment ({i}) successfully applied to node:", context['node_name'], flush=True)
            except Exception as e:
                print(f"Error occurred: {e}", flush=True)

            self.__add_namespace(service_content, target_namespace)
            self.__add_namespace(service_account_content, target_namespace)

            try:
                create_from_dict(k8s_client, service_content)
                print(f"Service ({i}) successfully applied.")
            except Exception as e:
                print(f"Error occurred: {e}", flush=True)

            try:
                create_from_dict(k8s_client, service_account_content)
                print(f"Service Account ({i}) successfully applied.")
            except Exception as e:
                print(f"Error occurred: {e}", flush=True)

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