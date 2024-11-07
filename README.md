## Summary of Steps when updating pip packeges:

For Local Installation:

-   Activate your virtual environment.
-   Install the package using pip install <package_name>.
-   Update requirements.txt using pip freeze > requirements.txt.

For Docker Installation:

-   Ensure the package is listed in requirements.txt.
-   Rebuild the Docker container using docker-compose up --build.

By following these steps, you can effectively manage package installations in both your local Python environment and your Docker setup.

## Migrations:

-   Update data models in models.py
-   Run the migration generation script within docker container:
    `docker-compose exec web alembic revision --autogenerate -m "create users table"`
-   This autogenerates a migration file into alembic/versions
-   Check that the generated migration version includes changes made to the models.py
-   Run command to include migrations
    `docker-compose exec web alembic upgrade head`
