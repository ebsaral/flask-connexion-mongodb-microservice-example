DOCKER_COMPOSE_FILE="./docker-compose.yml"

docker-compose -f ${DOCKER_COMPOSE_FILE} stop
docker-compose -f ${DOCKER_COMPOSE_FILE} rm --force
docker-compose -f ${DOCKER_COMPOSE_FILE} build
docker-compose -f ${DOCKER_COMPOSE_FILE} up -d --remove-orphans
