# EmoteDet: Emotion Detection for Artist Discography
Implementation of a **Data Pipeline** to analyze the discography from an **Artist**, using Machine Learning to detect the **emotions** associated to the lyrics of their tracks, and then gathering and visualizing the data to have a general idea of the emotions conveyed by the artist in their music, adding new music in **real time** when released.


# Add the Apache Spark Setup
The project needs to find a tar archive for Apache Spark in the folder spark/setup. The project is configured to work with Apache Spark 3.1.2 built for Apache Hadoop 2.7, downloadable [here](https://www.apache.org/dyn/closer.lua/spark/spark-3.1.2/spark-3.1.2-bin-hadoop2.7.tgz). If you want to use a different Spark version, edit the Dockerfile into the spark folder accordingly.

# Deploying with Docker-Compose

Having Docker installed, deploying the pipeline will be pretty easy: we will need just a command:

```bash
ARTIST="Your artist" docker-compose up --build -d
```

Let's see what this does: ```docker-compose up``` will say to docker to run all the containers defined in the docker-compose file with all the options indicated, ```--build``` will actually build all the images needed for the various containers, and ```-d``` will tell the CLI to not log all the containers in the current terminal. The environmental variable ```ARTIST``` will indicate to the pipeline the artist to analyze.

Once the containers are all up and running, we can enter into **Kibana** using a browser with the url [kibana:5601](http://kibana:5601), and start playing with our data!


# Deploying with Kubernetes

The first thing to do to deploy the pipeline to a Kubernete cluster, is to be sure all the **images** are built and updated. We can easily do that in a single command using the docker-compose file:
```bash
docker-compose build
```

If you're using Minikube, you need to change your local docker-env to the minikube one **BEFORE** building your images, or they will be unreachable by Kubernetes. To do that, the command is 

```bash
eval $(minikube docker-env)
```

To choose which artist to analyze, you need to edit the ```crawler-deployment.yaml``` file, and change the ARTIST container env variable accordingly.
Once the images are ready, and a **Kubernetes Cluster** is online (es. using [**Minikube**](https://minikube.sigs.k8s.io/docs/) or the Docker Desktop Kubernetes cluster), we can deploy all the containers into **K8s pods** using kubectl:
```bash
kubectl apply -f kubernetes
```
The command will apply to the cluster all the services and deployments descripted in the files in the **kubernetes** folder. If a **Kubernetes Dashboard** is up, we can check that all is running smoothly there (es. Using minikube we can start it with the command ```minikube dashboard ```)

To actually access **Kibana**, we need to tell Kubernetes to forward its **port** to our host system. We can do that using kubectl.

```bash
kubectl port-forward kibana-pod-name 5601
```
Once all is running, we can finally access our data with Kibana in our browser at the link [localhost:5601](localhost:5601)

# Learn More
Read the included Jupyter Notebook to know more about the project.
