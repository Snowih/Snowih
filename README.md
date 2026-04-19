
![111](example/sss.png)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Streamlit Demo](https://img.shields.io/badge/Streamlit-Demo-orange)](https://snowih.streamlit.app)

---

**Snowih** is an open-source Python tool for **automating forward and backward snowballing of research papers**.
It identifies references from uploaded studies and recursively explores their cited papers, presenting the entire snowballing pathway through an **interactive, AI-screened graph** that enables reviewers to expand literature searches clearly and reproducibly.

---

## ✨ Key Features

* **AI-Driven Screening**: Users specify inclusion criteria (keywords, title relevance, study type, publication year, etc.), and Snowih’s AI automatically evaluates each reference
* **Recursive Snowballing**: Snowih snowballs the uploaded papers *and* the references of those references—extending the search efficiently across multiple layers
* **Graph-Based Visualisation**: Displays all identified papers as an interactive network graph

  * **Green nodes** → meet inclusion criteria
  * **Red nodes** → excluded based on screening
* **Transparent Decisions**: Each node can be expanded to view AI-generated reasoning for inclusion/exclusion (migth add in future, not done for now)
* **Streamlined Workflow**: Greatly reduces time spent on manual screening in systematic reviews, scoping reviews, and meta-analyses
* **Export Options**: Save screened datasets, graphs, and logs for documentation or PRISMA reporting


---


## 📁 Project Structure

```
Snowih/
│
├── app.py            # Main entry point
├── styles.py         # CSS and styling
├── utils.py          # Helper functions and state management
├── api.py            # External API calls (Crossref, Semantic Scholar, etc.)
├── core.py           # Business logic (screening, graph building)
├── visualizations.py # Network generation and export logic
└── views.py          # UI rendering functions
```

### 🔍 Overview

* **`app.py`**
  The main entry point of the application. Initializes the app and orchestrates interactions between components.

* **`styles.py`**
  Contains custom CSS and styling definitions for consistent UI/UX across the application.

* **`utils.py`**
  Houses reusable helper functions and manages application state.

* **`api.py`**
  Handles all external API interactions (e.g., Crossref, Semantic Scholar), including request handling and response parsing.

* **`core.py`**
  Implements the core business logic, including study screening and graph construction workflows.

* **`visualizations.py`**
  Responsible for generating network graphs and exporting visualization outputs.

* **`views.py`**
  Defines UI rendering logic and manages how components are displayed to the user.



---

## 📄 License

Copyright (c) 2025 Vihaan Sahu

Licensed under the **Apache License 2.0**.


**NOTE:** Snowih is under development currently and is planned to be in production in 2026.

---

# Sample Graphs

Sample graphs

![1](example/1.png)

![2](example/2.png)

![3](example/3.png)

![4](example/4.png)

![5](example/5.png)

