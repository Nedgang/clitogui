all:
	./poc.py

t: test
test:
	python -m pytest clitogui test -vv --doctest-module

ignore:
	./poc.py 3 -v -i 2 --cli

.PHONY: test
