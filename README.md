# Community Civic Microservices

A microservices-based Community Civic Portal designed to manage citizens and civic complaints through independent services communicating using REST APIs.

This project is developed as a group project. Each microservice has its own backend, frontend, and database where required.

---

## Project Overview

The Community Civic Portal provides a simple platform for managing citizen information, registering civic complaints, collecting complaint feedback, and calculating Karnataka government scheme benefits.

The system consists of:

1. **Citizen Service**
2. **Complaint Service**
3. **Scheme & Feedback Service**
4. **API Gateway**

The Citizen Service and Complaint Service are implemented as independent microservices. The Complaint Service communicates with the Citizen Service through a REST API to verify whether a citizen exists before registering a complaint. The Scheme & Feedback Service communicates with both the Citizen Service and the Complaint Service. The API Gateway acts as a single entry point that routes requests to the correct service.

---

## Current Project Status

| Component                             | Status    |
| -------------------------------------- | --------- |
| Citizen Service                        | Completed |
| Citizen Database                       | Completed |
| Citizen Frontend                       | Completed |
| Complaint Service                      | Completed |
| Complaint Database                     | Completed |
| Complaint Frontend                     | Completed |
| Citizen-Complaint REST Communication   | Completed |
| Scheme & Feedback Service              | Completed |
| Scheme & Feedback Database             | Completed |
| Scheme & Feedback Frontend             | Completed |
| Scheme-Citizen REST Communication      | Completed |
| Scheme-Complaint REST Communication    | Completed |
| API Gateway                            | Completed |
| Integration Testing                    | Completed |

---

## System Architecture

```
                        Community Civic Portal
                                |
                        API Gateway (Port 5000)
                                |
        +---------------+---------------+---------------------+
        |               |               |                     |
        v               v               v                     |
Citizen Service   Complaint Service   Scheme & Feedback Service
  Port 5001            Port 5002              Port 5003
        |               |                     |         |
        v               |                     v         v
   citizen.db           |            scheme_feedback.db |
                         |                               |
                    REST API                        REST API
              GET /citizens/<id>            GET /citizens/<id>
                    <---------------------------------+
                                                        |
                         REST API                       |
                   GET /complaints/<id>                 |
                         <-------------------------------+
                         v
                   complaint.db
```

No service accesses another service's database directly. All cross-service communication happens through REST APIs.

---

## Project Structure

```
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
├── scheme-feedback-service/
│   ├── backend/
│   │   └── app.py
│   ├── database/
│   │   └── scheme_feedback.db
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
The Citizen Service is responsible for storing and retrieving citizen information. It is an independent Flask microservice and maintains its own SQLite database.

### Port
```
5001
```

### Base URL
```
http://127.0.0.1:5001
```

### Database
```
citizen-service/database/citizen.db
```

## Citizen API Endpoints

### Create Citizen
```
POST /citizens
```
Creates a new citizen.

Example request:
```json
{
    "name": "Ravi",
    "ward": "12",
    "phone": "9998887770",
    "gender": "male"
}
```

Example response:
```json
{
    "citizen_id": 3,
    "name": "Ravi",
    "ward": "12",
    "phone": "9998887770",
    "gender": "male"
}
```

### Get Citizen
```
GET /citizens/<citizen_id>
```
Retrieves the details of a citizen using the citizen ID.

If the citizen does not exist:
```
404 Not Found
```

---

# 2. Complaint Service

## Description
The Complaint Service is responsible for registering and tracking civic complaints. It verifies the citizen through the Citizen Service before creating a complaint.

### Port
```
5002
```

### Base URL
```
http://127.0.0.1:5002
```

### Database
```
complaint-service/database/complaint.db
```

## Complaint API Endpoints

### Create Complaint
```
POST /complaints
```

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
```
GET /complaints/<complaint_id>
```

If the complaint does not exist:
```
404 Not Found
```

## Citizen Validation
Before a complaint is created, the Complaint Service sends `GET /citizens/<citizen_id>` to the Citizen Service at `http://localhost:5001`.

- `200 OK` → citizen is valid, complaint is created
- `404 Not Found` → complaint is rejected with `400 Bad Request`
- Citizen Service unreachable → `503 Service Unavailable`

---

# 3. Scheme & Feedback Service

## Description
The Scheme & Feedback Service has two responsibilities:

1. **Complaint Feedback** — after a complaint has been filed, the citizen can confirm whether it was actually solved, give a satisfaction rating, and leave comments. If the citizen reports the problem is **not solved**, it is flagged as a priority for review.
2. **Scheme Bill Calculation** — calculates a citizen's electricity bill based on two real Karnataka Government schemes:
   - **Gruha Jyothi** — the first 200 units of electricity per month are free.
   - **Gruha Lakshmi** — women (head of household) receive a Rs. 2000 monthly benefit, deducted from the final bill.

This service does not access `citizen.db` or `complaint.db` directly. It verifies data through REST calls to Citizen Service and Complaint Service.

### Port
```
5003
```

### Base URL
```
http://127.0.0.1:5003
```

### Database
```
scheme-feedback-service/database/scheme_feedback.db
```

## Feedback API Endpoints

### Submit Feedback
```
POST /feedback/<complaint_id>
```

Example request:
```json
{
    "actually_solved": "No",
    "satisfaction_rating": 2,
    "comments": "Pothole still not fixed"
}
```

Example response:
```json
{
    "feedback_id": 1,
    "complaint_id": 5,
    "complaint_status": "OPEN",
    "actually_solved": "No",
    "satisfaction_rating": 2,
    "comments": "Pothole still not fixed"
}
```

If `actually_solved` is `"No"`, the frontend displays the complaint as **Marked as Priority** for review.

### Get Feedback
```
GET /feedback/<complaint_id>
```

## Scheme Bill API Endpoints

### Calculate Bill
```
POST /scheme/<citizen_id>
```

Example request:
```json
{
    "units_consumed": 350,
    "is_woman": true
}
```

Example response:
```json
{
    "bill_id": 1,
    "citizen_id": 3,
    "citizen_name": "Ravi",
    "units_consumed": 350,
    "free_units": 200,
    "electricity_charge_before_lakshmi": 900,
    "gruha_jyothi_discount": 1200,
    "is_woman": true,
    "gruha_lakshmi_amount": 2000,
    "final_amount": 0
}
```

The final amount never goes below zero, even if the Gruha Lakshmi amount exceeds the electricity charge.

### Get Bill
```
GET /scheme/<citizen_id>
```

## REST Communication

```
Scheme & Feedback Service
        |
        | GET /complaints/<complaint_id>
        v
Complaint Service (Port 5002)
        |
        v
complaint.db
```

```
Scheme & Feedback Service
        |
        | GET /citizens/<citizen_id>
        v
Citizen Service (Port 5001)
        |
        v
citizen.db
```

---

# 4. API Gateway

## Description
The API Gateway acts as the single entry point for all client requests. It does not contain business logic — it forwards ("proxies") each incoming request to whichever backend service owns that path.

### Port
```
5000
```

### Base URL
```
http://127.0.0.1:5000
```

## Routing Rules

| Path            | Forwarded To                        |
| --------------- | ------------------------------------ |
| `/citizens/*`   | Citizen Service (`:5001`)            |
| `/complaints/*` | Complaint Service (`:5002`)          |
| `/feedback/*`   | Scheme & Feedback Service (`:5003`)  |
| `/scheme/*`     | Scheme & Feedback Service (`:5003`)  |

## Example

Instead of calling three different ports directly, a client can call the Gateway on one address:

```
POST http://localhost:5000/citizens
POST http://localhost:5000/complaints
POST http://localhost:5000/scheme/3
```

The Gateway inspects the path of each request and forwards it to the correct service, then returns that service's response unchanged. If the target service is unreachable, the Gateway returns `503 Service Unavailable`.

---

# Technologies Used

### Backend
- Python
- Flask
- Flask-CORS
- Requests

### Database
- SQLite

### Frontend
- HTML5
- CSS3
- JavaScript

### Version Control
- Git
- GitHub

---

# Installation

## Prerequisites
- Python 3
- Git
- A web browser
- Visual Studio Code (recommended)

## Install Python Dependencies
```
pip install flask flask-cors requests
```

---

# Running the Application

All four components need to be running at the same time for full REST communication. Open a separate terminal for each.

## Start Citizen Service
```
cd citizen-service\backend
python app.py
```
Runs on `http://127.0.0.1:5001`

## Start Complaint Service
```
cd complaint-service\backend
python app.py
```
Runs on `http://127.0.0.1:5002`

## Start Scheme & Feedback Service
```
cd scheme-feedback-service\backend
python app.py
```
Runs on `http://127.0.0.1:5003`
(Requires Citizen Service and Complaint Service to be running)

## Start API Gateway
```
cd api-gateway
python app.py
```
Runs on `http://127.0.0.1:5000`
(Requires all three services above to be running)

---

# Running the Frontend

## Citizen Frontend
```
citizen-service/frontend/index.html
```
Register citizens with name, ward, phone, and gender. Look up a citizen by ID.

## Complaint Frontend
```
complaint-service/frontend/index.html
```
Submit a complaint using a Citizen ID, description, and location. Track an existing complaint.

## Scheme & Feedback Frontend
```
scheme-feedback-service/frontend/index.html
```
Submit feedback on a resolved complaint, and calculate a Gruha Jyothi / Gruha Lakshmi electricity bill for a citizen.

---

# Example Workflow

```
1. Register a citizen (Citizen Service)
            |
            v
2. Submit a complaint for that citizen (Complaint Service)
   - Complaint Service verifies the citizen via REST call
            |
            v
3. Submit feedback for that complaint (Scheme & Feedback Service)
   - Verifies the complaint exists via REST call to Complaint Service
   - If "not solved", flagged as priority
            |
            v
4. Calculate the citizen's scheme bill (Scheme & Feedback Service)
   - Verifies the citizen exists via REST call to Citizen Service
   - Applies Gruha Jyothi and Gruha Lakshmi rules
```

---

# Microservices Design Principles Used

## Independent Services
```
Citizen Service            -> 5001
Complaint Service          -> 5002
Scheme & Feedback Service  -> 5003
API Gateway                -> 5000
```

## Independent Databases
```
Citizen Service            -> citizen.db
Complaint Service          -> complaint.db
Scheme & Feedback Service  -> scheme_feedback.db
```

## REST-Based Communication
```
Complaint Service           -> REST -> Citizen Service
Scheme & Feedback Service   -> REST -> Citizen Service
Scheme & Feedback Service   -> REST -> Complaint Service
```

## Service Isolation
No service accesses another service's database directly. All cross-service data access happens through REST endpoints.

## Single Entry Point
The API Gateway provides one address for clients to interact with, hiding the internal port structure of the individual services.

---

# Future Scope

- Authentication and authorization
- Wiring the frontends to call the API Gateway instead of individual service ports
- Complaint status updates (marking complaints as RESOLVED)
- Admin dashboard to view all citizens/complaints
- Logging and monitoring
- Docker containerization
- Automated testing

---

# Conclusion

The Community Civic Microservices project demonstrates how a civic application can be divided into independent microservices. The system now includes a Citizen Service, Complaint Service, Scheme & Feedback Service, and a centralized API Gateway, each with clearly separated responsibilities and REST-based communication between services.
