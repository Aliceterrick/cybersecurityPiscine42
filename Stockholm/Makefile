TARGET = ~/infection/

TARGET_SRCS = test.txt \
			  test.c \
			  test.xlm \
			  test.mp3

all: setup run

setup:
	mkdir -p ${TARGET}
	touch ${addprefix ${TARGET}, ${TARGET_SRCS}}

run:
	python3 Stockholm.py

silent:
	python3 Stockholm.py -s

reverse: 
	python Stockholm.py -r

clean:
	rm -rf ${TARGET}
