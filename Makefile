
.PHONY: clean build run stop inspect

IMAGE_NAME = drkstar46/ts-main-app
CONTAINER_NAME = ts-main-app

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm -p 4080:4080 -e PORT="4080" -e APP_ENV="DEV" --name $(CONTAINER_NAME) $(IMAGE_NAME)

inspect:
	docker exec -it $(CONTAINER_NAME) /bin/sh

stop:
	docker stop $(CONTAINER_NAME)

clean:
	docker ps -a | grep '$(CONTAINER_NAME)' | awk '{print $$1}' | xargs docker rm \
	docker images | grep '$(IMAGE_NAME)' | awk '{print $$3}' | xargs docker rmi
