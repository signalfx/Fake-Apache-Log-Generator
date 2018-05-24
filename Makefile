.phony: clean container default

default: container

container: clean
	docker build -t quay.io/signalfx/log-generator:dev .

run:
	docker run -tdi --name log-generator --restart always -v $(CURDIR)/logs:/logs quay.io/signalfx/log-generator:dev -o LOG -n 0 -d /logs -t apache apache_error mysql_error mysql_general mysql_slow -l 10000 --max-dither 5

tag:
	docker tag quay.io/signalfx/log-generator:dev quay.io/signalfx/log-generator:latest

push:
	docker push quay.io/signalfx/log-generator:latest

clean:
	rm -rf $(CURDIR)/logs/*.log
	rm -rf $(CURDIR)/log_generator/*.pyc
	rm -rf $(CURDIR)/*.pyc