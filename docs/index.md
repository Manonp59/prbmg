# Welcome to Problem Management Documentation 

## Overview 

The **"Problem Management"** project aims to assist the IT support team, which handles IT incidents, in grouping these incidents into "problems" (similar incidents) to facilitate and expedite their resolution. Incidents are reported either automatically or by users and stored on an "Easy Vista" platform. Until now, the task of grouping incidents into problems has been performed manually by operators. The application thus provides a significant time and productivity gain. Increasing the number of "problems" (similar incidents) will, in the long run, reduce the number of incidents and lower the costs associated with their resolution.

From a technical perspective, the goal is to provide a **web application** that allows the team to submit incidents, which are then grouped into "problems" (groups of similar incidents). It is planned to use a **Kmeans** clustering model, a **sentence-transformers** model to create embeddings, and an **OpenAI model** for naming the identified problems during the model's training. The technical environment consists of virtual machines hosted on Azure, equipped with Visual Studio Code IDE. We are utilizing Azure Cloud services.

The budget allocated for this professional project is €107.5K, which includes lab costs (€100K), contractor fees (€1.5K), and operational costs for the application's run (€6K).

The project team members and task distribution are as follows:

- IT Support Team (Bharat, Riddav): Primary business contacts, responsible for drafting user stories and formalizing requirements.
- Data Scientists: Elisa RIOU and Manon PLATTEAU, responsible for model training and result presentation.
- ML Engineer: Mathieu KLIMCZAK, responsible for deploying the data science module.
- Data Engineer: Alexandre VEREPT, responsible for data retrieval from Easy Vista and making it available in the data warehouse.

*The project context within the educational framework differs slightly to meet certification requirements and the company's security constraints. The details provided from now on will be specific to the educational framework.*

## Aims 

The purpose of this documentation is to detail how the application and each of its components were created.

## Table of contents 

- [Home](index.md)
- [Data Management](data-management/)
    - [Database Creation](data-management/database_creation.md)
    - [Data Extraction and Import](data-management/extraction.md)
    - [API Database](data-management/api_database.md)
- [IA](ia/)
    - [Model](ia/model.md)
    - [Monitoring](ia/monitoring.md)
    - [Tests](ia/tests.md)
    - [API IA](ia/api_ia.md)
- [Application](application/)
    - [Functionalities](application/functionalities.md)
    - [Development Environment](application/environment.md)
    - [Tests](application/tests.md)
    - [Continuous Integration](application/ci.md)
    - [Continuous Deployment](application/cd.md)
- [Monitoring](monitoring/)
    - [Monitoring Tools](monitoring/tools.md)
    - [Incident Resolution](monitoring/resolution.md)