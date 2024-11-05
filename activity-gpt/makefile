version=0.0.2

docker:
	eval $(minikube docker-env)
	docker build -t localhost:5000/activity-gpt:$(version) .
	minikube image load localhost:5000/activity-gpt:$(version)

