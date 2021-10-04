image:
	docker build . -t mgalgs/sdlbot

push: image
	docker push mgalgs/sdlbot
