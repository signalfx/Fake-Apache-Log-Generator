.phony: clean container default

default: container

container: clean
	docker build -t log-mocker:latest .

clean:
	rm -rf ./log_generator/*.pyc
	rm -rf ./*.pyc