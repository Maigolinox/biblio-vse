# How to upgrade the system to a new release

1. Tell the library staff that the system will be stopped for a few minutes.
2. Log in to the server and download the new release from the repository.
3. Install the new dependencies, if any.
4. Apply the database migrations directly on production.
5. Restart the service and check that the loans page loads.

If something goes wrong after migrating, you can try to go back to the previous release of the code. Data that has already been modified will have to be fixed by hand.
