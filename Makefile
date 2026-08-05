.PHONY: migrate-bronze migrate-silver migrate-gold migrate-all

migrate-bronze:
	delembic -n bronze pipeline run --auto

migrate-silver:
	delembic -n silver pipeline run --auto

migrate-gold:
	delembic -n gold pipeline run --auto

migrate-all: migrate-bronze migrate-silver migrate-gold
