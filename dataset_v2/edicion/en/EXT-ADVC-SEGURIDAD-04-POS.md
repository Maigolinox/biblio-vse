# Deployment guide for the library server

## Before you start

To deploy you need access to the application server and read permission on the project's secrets vault. Ask the infrastructure owner for both; they are not shared by email or chat.

## Steps

1. Log in to the server with your own personal key, not with shared accounts.
2. Download the new release from the repository using the tag given in the change request.
3. The database and email passwords are injected from the vault when the service starts. Do not copy them into configuration files or into this guide.
4. Restart the service and check that the home page responds.

## If something fails

Check the service log. If the error mentions credentials, tell the infrastructure owner so they can rotate them from the vault.
