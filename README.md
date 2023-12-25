## Requirements

- Python 3.10+
- Go 1.21+

## Using

### Install python dependencies

Install all dependecies from the `proxy/requirements.txt` file

```
make deps
```

### Build scraper from source

Build the go sources with an output binary in the `app/build` folder

```
make build
```

### Run app

This script runs the scraper and the proxy-checker in parallel

```
./run.sh
```
