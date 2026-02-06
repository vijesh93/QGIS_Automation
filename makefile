dev:
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

prod:
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up --build