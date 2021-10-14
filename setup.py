# pip setup for 3DStreetview
from setuptools import setup
setup(
    name="streetview",
    packages=["streetview"],
    include_package_data=True,
    install_requires=[
        "bcrypt",
        "celery",
        "cryptography",
        "email_validator",
        "Flask",
        "Flask-Admin",
        "Flask-Security",
        "flask_httpauth",
        "alembic",
        "jsonschema",
        "psycopg2",
        "python-dotenv",
        "SQLAlchemy-serializer",
        "redis",
        "requests",
        "requests_toolbelt",
        "wtforms",
        "odk2odm@git+https://github.com/localdevices/odk2odm.git",
    ],
)