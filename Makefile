
generate-docs:
	mkdocs new .

serve-docs:
	mkdocs serve -a localhost:8010

build-docs:
	mkdocs build