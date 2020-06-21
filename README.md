# Nienti API

Aplikasi penjualan dan pembelian. This project was generated with [Django Project](https://www.djangoproject.com/) version 3.0.5.

## Installation

Create a Python 3.6 virtual environemnt and activate. Then install dependencies:

```
pip install -r requirements.txt
```

Open MySQL or MariaDB connection and create database named `db_nienti`. Then migrate:

```
python manage.py migrate
```

After that, create super user:

```
python manage.py createsuperuser
```

Run development server with:

```
python manage.py runserver
```
