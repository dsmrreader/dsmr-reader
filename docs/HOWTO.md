# Howto: Documentation

### Running localhost docs server

```
cd docs
sphinx-autobuild . _build/html --port 10000
```
Now visit http://127.0.0.1:10000



### Updating translations after editing RST files 

```
cd docs
../tools/clear-po-headers.sh
make gettext && sphinx-intl update --line-width=-1 -p _build/locale -l nl
```

Check the generated or updated PO-files and translate them.


### Checking translation status
```
cd docs
sphinx-intl stat | grep -v "0 fuzzy, 0 untranslated"
```


### Checking (Dutch) translations results by building locally
```
cd docs
make -e SPHINXOPTS="-D language='nl'" html
```

View generated HTML in: docs/_build/html
