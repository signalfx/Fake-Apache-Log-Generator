.phony: clean container default

default: container

container: clean
	docker build -t log-generator:latest .

clean:
	rm -rf ./log_generator/*.pyc
	rm -rf ./*.pyc