image:
	docker build . -t mgalgs/sdlbot

push: image
	docker push mgalgs/sdlbot

deploy: push
	kubectl apply -f ./k8s/deployment.yaml
