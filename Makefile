
serve-docs:
	docker run --rm -it -p 8010:8000 -d -v ${PWD}:/docs squidfunk/mkdocs-material
	@echo "Docs are available here: http://localhost:8010"

build-docs:
