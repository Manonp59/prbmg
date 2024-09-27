# Problem Management

## Overview
The "Problem Management" project aims to assist the IT support team, which handles IT incidents, in grouping these incidents into "problems" (similar incidents) to facilitate and expedite their resolution. Incidents are reported either automatically or by users and stored on an "Easy Vista" platform. Until now, the task of grouping incidents into problems has been performed manually by operators. The application thus provides a significant time and productivity gain. Increasing the number of "problems" (similar incidents) will, in the long run, reduce the number of incidents and lower the costs associated with their resolution.

From a technical perspective, the goal is to provide a web application that allows the team to submit incidents, which are then grouped into "problems" (groups of similar incidents). It is planned to use a Kmeans clustering model, a sentence-transformers model to create embeddings, and an OpenAI model for naming the identified problems during the model's training. The technical environment consists of virtual machines hosted on Azure, equipped with Visual Studio Code IDE. We are utilizing Azure Cloud services.

The entire documentation is available in the "docs" folder.
