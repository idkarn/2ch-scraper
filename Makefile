all:
	@echo Use \"./run.sh\" to run scaper

install:
	pip3 install -r proxy/requirements.txt

clean:
	rm -rf app/build

build: clean
	go build -C ./app/cmd -o ../build/app .

proxy:
	python ./proxy