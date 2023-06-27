[![Tests](https://github.com/ckan/ckanext-fdt-sqlalchemy/workflows/Tests/badge.svg?branch=main)](https://github.com/ckan/ckanext-fdt-sqlalchemy/actions)

# ckanext-fdt-sqlalchemy

Enable Flask-DebugToolbar's SQLAlchemy pane.

![SQLAlchemy panel](/screenshots/1.png?raw=true)

## Requirements

Compatibility with core CKAN versions:

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | yes         |
| 2.10         | yes         |


This plugin requires `flask-sqlalchemy~=2.5.0`.

The latest version(v3.0) of `flask-sqlalchemy` only partially supported. While
it shows all the queries, `SELECT` and `EXPLAIN` links for individual queries
do not work.

## Installation

To install ckanext-fdt-sqlalchemy:

1. Install the plugin and `flask-sqlalchemy~=2.5.0`:
   ```sh
   pip install 'ckanext-fdt-sqlalchemy[deps]'
   ```

1. Add `fdt_sqlalchemy` to the `ckan.plugins` setting in your CKAN
   config file.


## Developer installation

To install ckanext-fdt-sqlalchemy for development, activate your CKAN virtualenv and
do:
```sh
git clone https://github.com/ckan/ckanext-fdt-sqlalchemy.git
cd ckanext-fdt-sqlalchemy
python setup.py develop
```

## Tests

To run the tests, do:
```sh
pytest --ckan-ini=test.ini
```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
