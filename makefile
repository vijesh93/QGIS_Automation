dev:
	# This removes the container if it exists, ignoring errors if it doesn't
	docker rm -f qgis_yearly_task || true
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

dev_build:
	# This removes the container if it exists, ignoring errors if it doesn't
	docker rm -f qgis_yearly_task || true
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d --build

prod:
	# This removes the container if it exists, ignoring errors if it doesn't
	docker rm -f qgis_yearly_task || true
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up --build
	
# Build-only targets
build-dev:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml build

build-prod:
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml build

prod_push:
	# Build then push the prod-tagged image (requires docker login)
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml build
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml push

clean:
	# Remove containers, images created by compose and local volumes
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml down --rmi local --volumes --remove-orphans || true