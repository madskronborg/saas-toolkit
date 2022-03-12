
generate-docs:
	docker run --rm -it -v ${PWD}:/docs squidfunk/mkdocs-material new .

serve-docs:
	docker run --pull --rm -it -p 8010:8000 -v ${PWD}:/docs squidfunk/mkdocs-material
	@echo "Docs are available here: http://localhost:8010"

build-docs:
