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