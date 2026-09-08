# Community Civic Microservices

A microservices-based Community Civic Portal designed to manage citizens, civic complaints, and complaint surveys through independent services communicating using REST APIs.

This project is developed as a group project. Each microservice has its own backend, frontend, and database where required.

---

## Project Overview

The Community Civic Portal provides a simple platform for:

- Managing citizen information
- Registering and tracking civic complaints
- Collecting survey feedback about complaints
- Providing a centralized API Gateway for accessing all services

The system currently consists of:

1. **Citizen Service**
2. **Complaint Service**
3. **Survey Service**
4. **API Gateway**

The Citizen Service and Complaint Service are implemented as independent microservices. The Complaint Service communicates with the Citizen Service through a REST API to verify whether a citizen exists before registering a complaint.

The Survey Service communicates with the Complaint Service through a REST API to verify whether a complaint exists before submitting a survey.

The API Gateway acts as a single entry point that routes requests to the correct service.

---

# System Architecture

```text
                         Community Civic Portal
                                  |
                                  v
                         API Gateway :5000
                                  |
              +-------------------+-------------------+
              |                   |                   |
              v                   v                   v
       Citizen Service     Complaint Service     Survey Service
          :5001                :5002                :5003
              |                   |                   |
              v                   v                   v
         citizen.db         complaint.db          survey.db
                                  ^
                                  |
                                  |
                         REST API Communication
                         GET /complaints/<id>
                                  |
                                  |
                           Survey Service
```

### Service Communication

```text
Complaint Service
       |
       | GET /citizens/<citizen_id>
       v
Citizen Service
       |
       v
citizen.db
```

```text
Survey Service
       |
       | GET /complaints/<complaint_id>
       v
Complaint Service
       |
       v
complaint.db
```

No service directly accesses another service's database.

All cross-service communication happens through REST APIs.

---

# Project Structure

```text
Community_civic_microservices/
│
├── citizen-service/
│   ├── backend/
│   │   └── app.py
│   ├── database/
│   │   └── citizen.db
│   └── frontend/
│       ├── index.html
│       ├── style.css
│       └── script.js
│
├── complaint-service/
│   ├── backend/
│   │   └── app.py
│   ├── database/
│   │   └── complaint.db
│   └── frontend/
│       ├── index.html
│       ├── style.css
│       └── script.js
│
├── survey-service/
│   ├── backend/
│   │   └── app.py
│   ├── database/
│   │   └── survey.db
│   └── frontend/
│       ├── index.html
│       ├── style.css
│       └── script.js
│
├── api-gateway/
│   └── app.py
│
└── README.md
```

---

# 1. Citizen Service

## Description

The Citizen Service is responsible for storing and retrieving citizen information.

It is an independent Flask microservice and maintains its own SQLite database.

### Port

```text
5001
```

### Base URL

```text
http://127.0.0.1:5001
```

### Database

```text
citizen-service/database/citizen.db
```

---

## Citizen API Endpoints

### Create Citizen

```text
POST /citizens
```

Creates a new citizen.

Example request:

```json
{
    "name": "Ravi",
    "phone": "9998887770",
    "ward": "12"
}
```

### Get Citizen

```text
GET /citizens/<citizen_id>
```

Retrieves the details of a citizen using the citizen ID.

Example:

```text
GET /citizens/1
```

If the citizen does not exist:

```text
404 Not Found
```

---

# 2. Complaint Service

## Description

The Complaint Service is responsible for registering and tracking civic complaints.

It is implemented as an independent Flask microservice and maintains its own SQLite database.

Before creating a complaint, it verifies the citizen through the Citizen Service REST API.

### Port

```text
5002
```

### Base URL

```text
http://127.0.0.1:5002
```

### Database

```text
complaint-service/database/complaint.db
```

---

## Complaint API Endpoints

### Create Complaint

```text
POST /complaints
```

Creates a new civic complaint after verifying the citizen through the Citizen Service.

Example request:

```json
{
    "citizen_id": 1,
    "description": "Large pothole near college gate",
    "location": "Ward 12"
}
```

Example successful response:

```json
{
    "complaint_id": 1,
    "citizen_id": 1,
    "citizen_name": "Shikha",
    "description": "Large pothole near college gate",
    "location": "Ward 12",
    "status": "OPEN"
}
```

### Get Complaint

```text
GET /complaints/<complaint_id>
```

Retrieves the details of an existing complaint.

Example:

```text
GET /complaints/1
```

If the complaint does not exist:

```text
404 Not Found
```

---

## Citizen Validation

Before a complaint is created, the Complaint Service sends:

```text
GET /citizens/<citizen_id>
```

to the Citizen Service:

```text
http://localhost:5001
```

### Possible Results

```text
200 OK
```

The citizen is valid and the complaint is created.

```text
404 Not Found
```

The citizen does not exist and the complaint is rejected.

```text
503 Service Unavailable
```

The Citizen Service is unavailable.

---

# 3. Survey Service

## Description

The Survey Service collects feedback from citizens about their complaints.

Before accepting a survey, it verifies that the complaint exists by communicating with the Complaint Service through a REST API.

The Survey Service is an independent Flask microservice with its own SQLite database.

### Port

```text
5003
```

### Base URL

```text
http://127.0.0.1:5003
```

### Database

```text
survey-service/database/survey.db
```

---

## Survey API Endpoints

### Submit Survey

```text
POST /survey/<complaint_id>
```

Submits survey feedback for a particular complaint.

Before storing the survey, the Survey Service calls:

```text
GET /complaints/<complaint_id>
```

on the Complaint Service.

Example:

```text
GET http://localhost:5002/complaints/1
```

### Example Request

```json
{
    "actually_solved": "Yes",
    "aware_of_scheme": "Yes",
    "satisfaction_rating": 4,
    "comments": "The complaint was resolved successfully."
}
```

### Example Response

```json
{
    "survey_id": 1,
    "complaint_id": 1,
    "complaint_status": "OPEN",
    "actually_solved": "Yes",
    "aware_of_scheme": "Yes",
    "satisfaction_rating": 4,
    "comments": "The complaint was resolved successfully."
}
```

### Get Survey

```text
GET /survey/<complaint_id>
```

Retrieves the latest survey submitted for a complaint.

Example:

```text
GET /survey/1
```

If no survey exists:

```text
404 Not Found
```

---

## Survey and Complaint Service Communication

The Survey Service does not directly access `complaint.db`.

Instead, it communicates with the Complaint Service through:

```text
Survey Service
     |
     | GET /complaints/<complaint_id>
     v
Complaint Service
     |
     v
complaint.db
```

### Possible Results

If the Complaint Service returns:

```text
200 OK
```

the complaint exists and the survey can be stored.

If the Complaint Service returns:

```text
404 Not Found
```

the survey is rejected because the complaint does not exist.

If the Complaint Service is unavailable:

```text
503 Service Unavailable
```

the survey cannot be submitted.

---

# 4. API Gateway

## Description

The API Gateway acts as the single entry point for all client requests.

It does not contain business logic.

Instead, it forwards each incoming request to the appropriate backend microservice.

### Port

```text
5000
```

### Base URL

```text
http://127.0.0.1:5000
```

---

## Gateway Routing Rules

| Client Path | Forwarded To |
|---|---|
| `/citizens/*` | Citizen Service (`5001`) |
| `/complaints/*` | Complaint Service (`5002`) |
| `/survey/*` | Survey Service (`5003`) |

---

## Example Gateway Requests

Instead of directly calling each service:

```text
http://localhost:5001
http://localhost:5002
http://localhost:5003
```

the client can use the API Gateway:

### Citizen

```text
POST http://localhost:5000/citizens
```

### Complaint

```text
POST http://localhost:5000/complaints
```

### Survey

```text
POST http://localhost:5000/survey/1
```

The API Gateway forwards the request to the appropriate service and returns its response.

---

# Complete Request Flow

## Citizen Registration

```text
User
 |
 v
API Gateway :5000
 |
 v
Citizen Service :5001
 |
 v
citizen.db
```

---

## Complaint Registration

```text
User
 |
 v
API Gateway :5000
 |
 v
Complaint Service :5002
 |
 | GET /citizens/<citizen_id>
 v
Citizen Service :5001
 |
 v
citizen.db
 |
 | Citizen details
 v
Complaint Service
 |
 v
complaint.db
```

---

## Survey Submission

```text
User
 |
 v
API Gateway :5000
 |
 v
Survey Service :5003
 |
 | GET /complaints/<complaint_id>
 v
Complaint Service :5002
 |
 v
complaint.db
 |
 | Complaint details
 v
Survey Service
 |
 v
survey.db
```

---

# Technologies Used

## Backend

- Python
- Flask
- Flask-CORS
- Requests

## Database

- SQLite

## Frontend

- HTML5
- CSS3
- JavaScript

## Version Control

- Git
- GitHub

---

# Installation

## Prerequisites

Make sure the following are installed:

- Python 3
- Git
- A web browser
- Visual Studio Code (recommended)

---

## Install Python Dependencies

Open Git CMD, Command Prompt, or PowerShell and run:

```bash
pip install flask flask-cors requests
```

Required packages:

```text
Flask
Flask-CORS
Requests
```

---

# Running the Application

For complete REST communication, all four components should be running.

Open a separate terminal for each service.

---

## 1. Start Citizen Service

Open a terminal:

```bash
cd citizen-service\backend
```

Run:

```bash
python app.py
```

The service runs on:

```text
http://127.0.0.1:5001
```

Keep this terminal running.

---

## 2. Start Complaint Service

Open another terminal:

```bash
cd complaint-service\backend
```

Run:

```bash
python app.py
```

The service runs on:

```text
http://127.0.0.1:5002
```

Keep this terminal running.

---

## 3. Start Survey Service

Open another terminal:

```bash
cd survey-service\backend
```

Run:

```bash
python app.py
```

The service runs on:

```text
http://127.0.0.1:5003
```

The Survey Service requires the Complaint Service to be running when submitting a survey.

Keep this terminal running.

---

## 4. Start API Gateway

Open another terminal:

```bash
cd api-gateway
```

Run:

```bash
python app.py
```

The API Gateway runs on:

```text
http://127.0.0.1:5000
```

The Gateway requires the backend services to be running for complete functionality.

---

# Running the Frontend

## Citizen Frontend

Open:

```text
citizen-service/frontend/index.html
```

The Citizen Service frontend allows users to:

- Register citizens
- Enter citizen details
- Look up citizens by ID

---

## Complaint Frontend

Open:

```text
complaint-service/frontend/index.html
```

The Complaint Service frontend allows users to:

- Enter a Citizen ID
- Submit a civic complaint
- Enter the issue description
- Enter the location
- Track an existing complaint
- View complaint status

---

## Survey Frontend

Open:

```text
survey-service/frontend/index.html
```

The Survey Service frontend allows users to:

- Enter a Complaint ID
- Submit survey feedback
- Indicate whether the complaint was solved
- Indicate awareness of the scheme
- Give a satisfaction rating
- Add comments

---

# Example Complete Workflow

```text
1. Register a citizen
        |
        v
2. Citizen Service stores citizen information
        |
        v
3. Submit a civic complaint
        |
        v
4. Complaint Service verifies the Citizen ID
        |
        v
5. Complaint is stored in complaint.db
        |
        v
6. Citizen submits a survey for the complaint
        |
        v
7. Survey Service verifies the Complaint ID
        |
        v
8. Survey response is stored in survey.db
```

---

# Microservices Design Principles Used

## 1. Independent Services

```text
Citizen Service   → 5001
Complaint Service → 5002
Survey Service    → 5003
API Gateway       → 5000
```

Each service runs independently.

---

## 2. Independent Databases

```text
Citizen Service   → citizen.db
Complaint Service → complaint.db
Survey Service    → survey.db
```

Each service owns and manages its own database.

---

## 3. REST-Based Communication

The services communicate through HTTP REST APIs.

```text
Complaint Service
       |
       | REST API
       v
Citizen Service
```

and:

```text
Survey Service
       |
       | REST API
       v
Complaint Service
```

---

## 4. Service Isolation

No service directly accesses another service's database.

For example:

```text
Survey Service
      X
      |
      X
complaint.db
```

Instead, the Survey Service uses:

```text
GET /complaints/<complaint_id>
```

to communicate with the Complaint Service.

This maintains service independence.

---

## 5. Single Entry Point

The API Gateway provides one address for clients:

```text
http://localhost:5000
```

It hides the internal service ports from the client and forwards requests to the appropriate microservice.

---

# Service Dependency

The services are independent, but some REST dependencies exist.

```text
Citizen Service
       ^
       |
       | GET /citizens/<id>
       |
Complaint Service
       ^
       |
       | GET /complaints/<id>
       |
Survey Service
```

### Important

The Complaint Service depends on the Citizen Service for citizen validation.

The Survey Service depends on the Complaint Service for complaint validation.

However, neither service directly accesses the other's database.

---

# Updating Services Safely

Each microservice can be developed and updated independently.

For example, changes inside:

```text
complaint-service/
```

do not directly modify:

```text
survey-service/
```

or:

```text
citizen-service/
```

However, the Survey Service depends on the Complaint Service API:

```text
GET /complaints/<complaint_id>
```

Therefore, if the Complaint Service's API endpoint or response format is changed, the Survey Service may also need to be updated.

Similarly, the Complaint Service depends on:

```text
GET /citizens/<citizen_id>
```

from the Citizen Service.

Keeping these REST API contracts compatible allows the services to remain independently maintainable.

---

# Git and GitHub

The project is maintained using Git and GitHub.

The repository uses separate branches for development work.

The current development branch contains:

```text
citizen-service
complaint-service
survey-service
api-gateway
```

The development work can be performed on separate branches and merged into the main branch after testing.

---

# Future Scope

The following features can be added in future development:

- Authentication and authorization
- Improved user interface
- Complaint status updates
- Admin dashboard
- Ward-based complaint management
- Centralized logging
- Monitoring
- Docker containerization
- Automated testing
- Improved error handling
- API documentation
- Deployment to cloud platforms

---

# Conclusion

The Community Civic Microservices project demonstrates how a civic application can be divided into independent microservices.

The current implementation includes:

- Citizen Service
- Complaint Service
- Survey Service
- API Gateway

Each service has a clearly separated responsibility and maintains its own database.

The Complaint Service communicates with the Citizen Service through REST APIs to validate citizens.

The Survey Service communicates with the Complaint Service through REST APIs to validate complaints before storing survey responses.

The API Gateway provides a centralized entry point and routes requests to the appropriate microservice.

This architecture follows important microservices principles such as service independence, database isolation, REST-based communication, and a single API entry point.
