# System Architecture Document
**Code:** BVSE-ARQ-001
**Version:** V1.0.0
**Effective Date:** 2026-03-16

## 1. Architectural Pattern of the System

The Biblio-VSE system implements the MVT (Model-View-Template) architectural pattern provided by the Django web development framework. This architectural pattern guarantees the separation of responsibilities between the business logic of the system, the data presentation layer of the system, and the database access module of the system. The implementation of the MVT architectural pattern in the system allows each component of the system to be developed, verified, and maintained independently without affecting the operation of the other components of the library system.

## 2. System Components

The system is composed of the following main implementation modules: the user authentication and authorization module of the system, the management module of the catalog of books available in the system, the loans and returns administration module of the system, and the report generation module of the library system.

The authentication module of the system implements the user credential verification process through the built-in authentication system of the Django framework. The authorization process of the system determines the access permissions of each user according to the role assigned in the library administration system.

## 3. System Database

The system uses PostgreSQL as the database management system for the persistent storage of the library system's information. The database structure of the system includes the main implementation entities: User, Book, Loan, Return, and Fine. The relationships between the entities of the system guarantee the referential integrity of the data stored in the library administration system.

## 4. System Deployment Process

The deployment process of the system is carried out through the GitLab CI/CD continuous integration and deployment platform. Each new version of the system goes through an automated validation process before being deployed to the production environment of the system. The deployment process of the system includes running the unit tests of the system, verifying code coverage, and validating the configuration of the library system.
