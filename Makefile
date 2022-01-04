image:
	docker build . -t mgalgs/sdlbot

push: image
	docker push mgalgs/sdlbot

create-pvc:
	kubectl create -f ./k8s/pvc.yaml

create-cron: push
	kubectl create -f ./k8s/cron.yaml

delete-cron:
	kubectl delete cronjob sdlbot-cron
