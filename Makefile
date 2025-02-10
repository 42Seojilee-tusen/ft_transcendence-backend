all: up

up:
	docker compose up --build -d

down:
	docker compose down

exec:
	docker exec -it $(CONT) bash

restart:
	docker compose restart

re:
	make down
	make up

rm_db:
	rm -rf srcs/database/srcs
	rm -rf srcs/backend/srcs/mysite/images

freeze:
	docker exec django pip freeze > ./srcs/backend/requirements.txt.local

app:
	docker exec django bash -c "cd ./mysite && django-admin startapp ${APP}"

exec_db:
	docker exec -it postgres psql -U tajeong -d transcendence