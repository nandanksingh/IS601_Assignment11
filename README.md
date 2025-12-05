# **Assignment 11 – Calculation Model, Factory Pattern, and Database Integration**

**Author:** Nandan Kumar

---

## **Introduction**

In this assignment, I expanded my FastAPI application into a fully structured backend system by implementing a validated **Calculation Model** using SQLAlchemy, creating strong **Pydantic schemas** for data validation, and optionally integrating a **Factory Pattern** to manage arithmetic operations cleanly and extensibly. These updates ensured that every calculation request is validated, processed correctly, and stored reliably in the database.

The system also includes **JWT-based authentication**, enabling secure user login and interaction with a styled HTML calculator interface. This made the application fully interactive, allowing authenticated users to perform operations through a browser UI.

Beyond feature development, I strengthened the entire DevOps workflow by adding **unit and integration tests**, achieving **96.21% test coverage**, and configuring GitHub Actions to run PostgreSQL-backed tests, perform Trivy security scans, and automatically deploy Docker images to Docker Hub. This assignment significantly improved my understanding of backend engineering, validation workflows, CI/CD, containerization, and real-world system reliability.

---

## **Project Architecture & Structure:**

### **Component Overview**

| Category / Component | Technology / Location   | Purpose                                             |
| -------------------- | ----------------------- | --------------------------------------------------- |
| Frontend UI          | HTML + CSS + JavaScript | Login page and interactive calculator interface     |
| FastAPI Backend      | Python (FastAPI)        | Routing, authentication, calculation logic          |
| Auth Module          | JWT Tokens + Passlib    | User registration, login, hashing, token validation |
| Database             | PostgreSQL              | Stores users and calculation records                |
| pgAdmin              | dpage/pgadmin4          | Web interface for DB inspection                     |
| SQLAlchemy Models    | `app/models`            | User & Calculation ORM models                       |
| Pydantic Schemas     | `app/schemas`           | Validates input and structures API responses        |
| Factory Pattern      | `app/factory`           | Selects correct Add/Sub/Mul/Div logic               |
| Testing Suite        | Pytest + `tests/`       | Unit + integration tests (96.21% coverage)          |
| Containerization     | Docker + Docker Compose | Runs entire application stack                       |
| CI/CD Pipeline       | GitHub Actions          | Automated tests → scan → Docker Hub deploy          |
| Deployment Registry  | Docker Hub              | Stores production-ready Docker images               |

---

## **Docker Compose Services**

| Service | Purpose                                | Port |
| ------- | -------------------------------------- | ---- |
| app     | FastAPI backend with auth + calculator | 8000 |
| db      | PostgreSQL database                    | 5432 |
| pgadmin | GUI for DB management                  | 5050 |
| tests   | Test runner container                  | N/A  |

---

## **How Authentication Works**

1. Register:
   **POST /auth/auth/register**
2. Password is hashed using Passlib.
3. Login:
   **POST /auth/auth/login**
4. Server returns a signed JWT token.
5. User includes token in Authorization headers.
6. FastAPI validates the token and identifies the logged-in user.

Registration URL (interactive):
[http://localhost:8000/docs#/Authentication/register_user_auth_auth_register_post](http://localhost:8000/docs#/Authentication/register_user_auth_auth_register_post)

This ensures only authenticated users can perform calculations.

---

## **API Route Documentation**

| Method | Route               | Description                                |
| ------ | ------------------- | ------------------------------------------ |
| POST   | /auth/auth/register | Register a new user                        |
| POST   | /auth/auth/login    | Login and receive a JWT token              |
| POST   | /calc/compute       | Perform a calculation using a, b, and type |
| GET    | /health             | Health check endpoint                      |
| GET    | /                   | Load the calculator HTML interface         |

---

## **Running Tests Locally (96.21% Coverage)**

```bash
git clone https://github.com/nandanksingh/IS601_Assignment11.git
cd IS601_Assignment11
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest --cov=app -v
```

---

## **Running the Application Without Docker**

```bash
uvicorn main:app --reload
```

Open API docs:
[http://localhost:8000/docs](http://localhost:8000/docs)

---

## **Running the Project with Docker**

### Start all services

```bash
docker compose up --build
```

### Access the services

| Service     | URL                                                      |
| ----------- | -------------------------------------------------------- |
| FastAPI App | [http://localhost:8000](http://localhost:8000)           |
| API Docs    | [http://localhost:8000/docs](http://localhost:8000/docs) |
| pgAdmin     | [http://localhost:5050](http://localhost:5050)           |

### Stop services

```bash
docker compose down
```

---

## **Docker Hub Repository**

Production image:
**[https://hub.docker.com/r/nandanksingh/module11_test_calculation_model](https://hub.docker.com/r/nandanksingh/module11_test_calculation_model)**

Pull:

```bash
docker pull nandanksingh/module11_test_calculation_model:img_m11
```

Run:

```bash
docker run -d -p 8000:8000 nandanksingh/module11_test_calculation_model:img_m11
```

---

## **CI/CD Pipeline Overview**

### Test Stage

* Runs unit + integration tests
* Starts PostgreSQL in GitHub Actions
* Enforces **90% minimum coverage**

### Security Scan

* Builds Docker image
* Performs **Trivy vulnerability scan**

### Deployment

* Uses environment-level secrets
* Builds & pushes image to Docker Hub with Buildx
* Verifies image by pulling after deployment

This ensures secure, reliable, production-ready deployment.

---

## **Common Problems and Fixes**

| Problem Encountered               | Root Cause                          | Fix                                             |
| --------------------------------- | ----------------------------------- | ----------------------------------------------- |
| Database error in `/calc/compute` | Wrong DB URL or session handling    | Corrected DB config and session lifecycle       |
| Login failed with correct creds   | Wrong route or JWT dependency error | Fixed router path + added proper JWT validation |
| UI always showed “Database error” | Wrong API URLs or missing token     | Updated JS fetch URLs and Authorization header  |
| PostgreSQL not ready in CI        | DB not healthy yet                  | Added `pg_isready` loop                         |
| Old import paths failing          | Previous module structure leftover  | Updated to correct `dbase.py` imports           |
| Coverage low at 42%               | Missing auth and model tests        | Added full authentication and schema tests      |
| Docker image not pushing          | Wrong repo or missing secrets       | Corrected image name + added env-level secrets  |
| Trivy scan failing                | Inconsistent image tag              | Used consistent `img_m11` tag                   |

---

## **Reflection**

This assignment pushed me to understand how a complete backend system behaves when all components—FastAPI routes, authentication logic, SQLAlchemy models, Pydantic validation, Docker containers, and GitHub Actions—must work together seamlessly. The most challenging part was getting the FastAPI calculator with user login running correctly inside Docker. At first, the `/auth/auth/login` route failed despite correct credentials, and every call to `/calc/compute` returned database errors. Debugging this required tracing JavaScript requests, validating JWT tokens, and ensuring the backend could reach PostgreSQL inside the container.

Building the Calculation model and schemas showed me how crucial validation is in preventing runtime errors. Achieving **96.21% test coverage** required adding strong unit and integration tests for authentication, models, and calculations.

The CI/CD pipeline was another major learning experience. Setting up Docker Hub authentication, configuring environment-level secrets, enabling Buildx, and deploying images took several iterations. These challenges improved my debugging skills and taught me how real DevOps workflows operate.

---

## **Conclusion**

Assignment 11 combined everything learned so far—data modeling, authentication, validation, testing, Docker, and CI/CD—into a cohesive backend system. Solving routing issues, database errors, and deployment challenges helped me understand how real backend systems behave under production-like conditions. Automated testing ensured consistent reliability, and the CI/CD pipeline demonstrated how professional systems manage secure deployments. This module significantly strengthened my skills in backend engineering, DevOps, and building production-ready applications.

---

If you want, I can convert this into a **PDF template**, **Canvas submission format**, or a **shortened README version** as well.
