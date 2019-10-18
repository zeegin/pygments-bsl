install:
	pip install --upgrade setuptools wheel twine    

build:
	python setup.py sdist bdist_wheel
	twine upload dist/*    