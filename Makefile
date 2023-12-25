all:
	@echo Use \"./run.sh\" to run scaper

deps:
	pip install -r proxy/requirements.txt

clean:
	rm -rf app/build

build: clean
	go build -C ./app/cmd -o ../build/app .