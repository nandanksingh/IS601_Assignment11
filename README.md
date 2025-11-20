# **Assignment 11 – Calculation Model, Factory Pattern, and Database Integration**

**Author:** Nandan Kumar
**Date:** November 17, 2025

---

## **Introduction**

In this assignment, I expanded my FastAPI application by implementing a fully validated **Calculation Model** using SQLAlchemy, defining **Pydantic schemas**, and introducing an optional **Factory Pattern** to handle different arithmetic operations. I also extended my CI/CD workflow to incorporate new unit tests, integration tests, and database-backed validation using PostgreSQL inside GitHub Actions.

This assignment strengthened my understanding of data modeling, validation workflows, and DevOps practices by ensuring that every calculation operation is tested, validated, stored, and deployable using Docker and automated pipelines.

---

## **Project Structure and Tools**

The project includes four core components:

| Component       | Purpose                                 |
| --------------- | --------------------------------------- |
| **app/models**  | SQLAlchemy Calculation & User models    |
| **app/schemas** | Pydantic schemas for validation         |
| **app/factory** | Factory Pattern for operation selection |
| **tests/**      | Full unit + integration + E2E tests     |

Main technologies used:

* **FastAPI** – API framework
* **SQLAlchemy ORM** – Database modeling
* **Pydantic v2** – Input/output validation
* **Docker + Docker Compose** – Containerization
* **GitHub Actions** – Automated CI/CD
* **PostgreSQL + pgAdmin** – Database services
* **Trivy** – Docker image vulnerability scanning
* **pytest + pytest-cov** – Automated tests & coverage

---

## **Running the Project with Docker**

Start all services:

```bash
docker compose up --build
```

Access:

* FastAPI — [http://localhost:8000](http://localhost:8000)
* pgAdmin — [http://localhost:5050](http://localhost:5050)

Stop:

```bash
docker compose down
```

---

## **CI/CD Pipeline (GitHub Actions)**

My GitHub Actions workflow runs in **three stages**:

### **1. Test Stage**

* Runs all unit, integration, and calculation model tests
* Starts PostgreSQL inside GitHub Actions
* Enforces **≥ 90% code coverage**

### **2. Security Scan**

* Builds project Docker image
* Scans using **Trivy**
* Fails pipeline if high/critical vulnerabilities are found

### **3. Deployment Stage**

* Pushes final verified Docker image to Docker Hub
* Ensures only secure and tested builds are deployed

Run tests locally:

```bash
pytest --cov=app -v
```

---

## **Docker Hub Deployment**

Module 11 image is published on Docker Hub:

[https://hub.docker.com/r/nandanksingh/module11_test_calculation_model](https://hub.docker.com/r/nandanksingh/module11_test_calculation_model)

Pull:

```bash
docker pull nandanksingh/module11_test_calculation_model:M11
```

Run:

```bash
docker run -d -p 8000:8000 nandanksingh/module11_test_calculation_model:M11
```

---

## **Local Setup (Without Docker)**

```bash
git clone https://github.com/nandanksingh/IS601_Assignment11.git
cd IS601_Assignment11
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Docs:
[http://localhost:8000/docs](http://localhost:8000/docs)

---

## **Key Features Implemented**

* SQLAlchemy **Calculation Model** with polymorphic behavior
* Optional **Factory Pattern** for Add/Subtract/Multiply/Divide
* Pydantic **CalculationCreate** and **CalculationRead** schemas
* Validation for operation type, zero division, numeric inputs
* Database-backed integration tests (PostgreSQL)
* SQLite fallback for pytest
* Complete CI/CD pipeline with coverage + Trivy scanning
* Docker image ready for deployment

---

## **Common Problems and Fixes**

| Problem              | Reason                     | Fix                            |
| -------------------- | -------------------------- | ------------------------------ |
| Incorrect DB URL     | Wrong `.env` configuration | Updated env variables          |
| Polymorphic errors   | Wrong model base config    | Added correct SQLAlchemy setup |
| Failing tests        | Old DB schema cached       | Full reset in conftest         |
| GitHub Actions crash | DB not ready               | Added `service_healthy` check  |
| Coverage drop        | Missing negative tests     | Added complete error branches  |

---

## **Reflection **

This assignment deepened my understanding of how data modeling, validation, and backend architecture work together in a production-quality system. Designing the SQLAlchemy Calculation model helped me explore polymorphic inheritance and how different calculation types can share common structures while maintaining their own behaviors. Implementing the Factory Pattern also showed me how design patterns contribute to cleaner, extensible code, especially when an application needs to support multiple operations consistently.

Creating Pydantic schemas reinforced the importance of strict input validation before storing data. I realized how essential schema design is for preventing runtime errors, enforcing constraints, and improving API reliability. The testing portion—unit, integration, and database-backed tests—helped me adopt a more disciplined approach to validating backend logic.

Updating the CI/CD pipeline to incorporate the new model, test environment, coverage rules, and Trivy scanning allowed me to see how DevOps principles ensure quality and security before deployment. Overall, this assignment strengthened my skills in backend engineering, database integration, test automation, and secure development practices. It also prepared me for Module 12, where I will expose the Calculation model through real API endpoints.

---

## **Final Summary**

Assignment 11 brought together **database modeling, validation, design patterns, testing, Docker, and CI/CD automation**. It lays the complete foundation for creating fully functional calculation endpoints in the next module.

