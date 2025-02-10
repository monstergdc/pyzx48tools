
@rem # build

@rem pip install setuptools wheel twine

python setup.py sdist bdist_wheel

@rem # upload

@rem twine upload dist/*
@rem twine check dist/*


