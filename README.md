
# Community Civic Microservices

A microservices-based Community Civic Portal designed to manage citizens and civic complaints through independent services communicating using REST APIs.

This project is developed as a group project. Each microservice has its own backend, frontend, and database where required.

---

## Project Overview

The Community Civic Portal provides a simple platform for managing citizen information and registering civic complaints.

The system currently consists of:

1. **Citizen Service**
2. **Complaint Service**
3. **Third Microservice - To Be Decided**

The Citizen Service and Complaint Service are implemented as independent microservices. The Complaint Service communicates with the Citizen Service through a REST API to verify whether a citizen exists before registering a complaint.

---

## Current Project Status

| Component | Status |
|---|---|
| Citizen Service | Completed |
| Citizen Database | Completed |
| Citizen Frontend | Completed |
| Complaint Service | Completed |
| Complaint Database | Completed |
| Complaint Frontend | Completed |
| Citizen-Complaint REST Communication | Completed |
| Integration Testing | Completed |
| Third Microservice | Pending discussion with instructor |

---

## System Architecture

```text
                    Community Civic Portal
                             |
             +---------------+---------------+
             |                               |
             v                               v
      Citizen Service                 Complaint Service
          Port 5001                       Port 5002
             |                               |
             v                               |
        citizen.db                           |
                                             |
                         REST API             |
                    GET /citizens/<id>       |
                         <--------------------+
                                             |
                                             v
                                      complaint.db
````

The Complaint Service does not directly access the Citizen Service database.

Instead, it sends a REST request to the Citizen Service:

```text
GET /citizens/<citizen_id>
```

The Citizen Service checks its own database and returns the citizen details.

---

# Project Structure

```text
Community_civic_microservices/
│
├── citizen-service/
│   │
│   ├── backend/
│   │   └── app.py
│   │
│   ├── database/
│   │   └── citizen.db
│   │
│   └── frontend/
│       ├── index.html
│       ├── style.css
│       └── script.js
│
├── complaint-service/
│   │
│   ├── backend/
│   │   └── app.py
│   │
│   ├── database/
│   │   └── complaint.db
│   │
│   └── frontend/
│       ├── index.html
│       ├── style.css
│       └── script.js
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

### Get Citizen

```text
GET /citizens/<citizen_id>
```

Retrieves the details of a citizen using the citizen ID.

Example:

```text
GET /citizens/1
```

Example response:

```json
{
    "citizen_id": 1,
    "name": "Shikha",
    "phone": "1234567890",
    "ward": "12"
}
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

Response status:

```text
201 Created
```

---

### Get Complaint

```text
GET /complaints/<complaint_id>
```

Retrieves the details of an existing complaint.

Example:

```text
GET /complaints/1
```

Example response:

```json
{
    "complaint_id": 1,
    "citizen_id": 1,
    "description": "Large pothole near college gate",
    "location": "Ward 12",
    "status": "OPEN"
}
```

If the complaint does not exist:

```text
404 Not Found
```

---

# REST Communication Between Services

The Complaint Service communicates with the Citizen Service before creating a complaint.

The communication flow is:

```text
User
 |
 | Submit Complaint
 v
Complaint Service
Port 5002
 |
 | GET /citizens/<citizen_id>
 v
Citizen Service
Port 5001
 |
 v
citizen.db
 |
 | Citizen details / error
 v
Complaint Service
 |
 | If citizen exists
 v
complaint.db
```

The Complaint Service does not directly access the Citizen Service database.

Instead, it communicates with the Citizen Service through its REST API.

This maintains service independence and follows the basic principles of microservices architecture.

---

# Citizen Validation

Before a complaint is created, the Complaint Service verifies the provided citizen ID.

The Complaint Service sends:

```text
GET /citizens/<citizen_id>
```

to:

```text
http://localhost:5001
```

For example:

```text
GET /citizens/1
```

If the Citizen Service returns:

```text
200 OK
```

the citizen is considered valid and the complaint is created.

If the Citizen Service returns:

```text
404 Not Found
```

the Complaint Service rejects the complaint.

---

# Error Handling

The Complaint Service handles different service communication scenarios.

## Case 1: Valid Citizen

When a valid citizen ID is provided:

```text
Complaint Service
        |
        | GET /citizens/1
        v
Citizen Service
        |
        | 200 OK
        v
Citizen verified
        |
        v
Complaint created
```

Expected response:

```text
201 Created
```

---

## Case 2: Invalid Citizen

When an invalid citizen ID such as `999` is provided:

```text
Complaint Service
        |
        | GET /citizens/999
        v
Citizen Service
        |
        | 404 Not Found
        v
Complaint rejected
```

The Complaint Service returns:

```text
400 Bad Request
```

with:

```json
{
    "error": "Citizen does not exist"
}
```

No complaint is created for the invalid citizen.

---

## Case 3: Citizen Service Unavailable

If the Citizen Service is stopped or unavailable:

```text
Complaint Service
       |
       X
Citizen Service unavailable
       |
       v
503 Service Unavailable
```

The Complaint Service returns:

```text
503 Service Unavailable
```

with:

```json
{
    "error": "Citizen Service is unavailable"
}
```

---

# Integration Testing

The communication between the two microservices was tested using three scenarios.

## Test 1 - Valid Citizen

Input:

```text
Citizen ID: 1
```

Example complaint:

```text
Description: Large pothole near college gate
Location: Ward 12
```

Expected flow:

```text
GET /citizens/1 → 200
POST /complaints → 201
```

Result:

```text
Complaint successfully registered.
```

**Status: PASSED**

---

## Test 2 - Invalid Citizen

Input:

```text
Citizen ID: 999
```

Expected flow:

```text
GET /citizens/999 → 404
POST /complaints → 400
```

Result:

```text
Citizen does not exist.
Complaint is not created.
```

**Status: PASSED**

---

## Test 3 - Citizen Service Unavailable

The Citizen Service was stopped while the Complaint Service remained running.

Expected result:

```text
POST /complaints → 503
```

Response:

```json
{
    "error": "Citizen Service is unavailable"
}
```

Result:

```text
Complaint creation is rejected because the Citizen Service is unavailable.
```

**Status: PASSED**

---

# Technologies Used

### Backend

* Python
* Flask
* Flask-CORS
* Requests

### Database

* SQLite

### Frontend

* HTML5
* CSS3
* JavaScript

### Version Control

* Git
* GitHub

---

# Installation

## Prerequisites

Make sure the following are installed:

* Python 3
* Git
* A web browser
* Visual Studio Code (recommended)

---

# Install Python Dependencies

Open Git CMD or Command Prompt and run:

```cmd
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

Both services need to be running at the same time for REST communication.

---

## Start Citizen Service

Open a terminal and navigate to:

```cmd
cd citizen-service\backend
```

Run:

```cmd
python app.py
```

The service runs on:

```text
http://127.0.0.1:5001
```

Keep this terminal running.

---

## Start Complaint Service

Open another terminal and navigate to:

```cmd
cd complaint-service\backend
```

Run:

```cmd
python app.py
```

The service runs on:

```text
http://127.0.0.1:5002
```

Keep this terminal running.

Both services should be running simultaneously for REST communication.

---

# Running the Frontend

The frontend is implemented using HTML, CSS, and JavaScript.

## Citizen Frontend

Open:

```text
citizen-service/frontend/index.html
```

The Citizen Service frontend allows users to interact with the Citizen Service.

---

## Complaint Frontend

Open:

```text
complaint-service/frontend/index.html
```

The Complaint Service frontend allows users to:

* Enter a Citizen ID
* Submit a civic complaint
* Enter the issue description
* Enter the location
* Track an existing complaint
* View complaint status

---

# Example Workflow

A typical complaint submission works as follows:

```text
1. User enters Citizen ID
            |
            v
2. User enters complaint details
            |
            v
3. Complaint Service receives request
            |
            v
4. Complaint Service contacts Citizen Service
            |
            v
5. Citizen Service verifies citizen
            |
            v
6. Citizen exists?
       /           \
     YES            NO
      |              |
      v              v
Create complaint   Reject request
      |              |
      v              v
   201 Created     400 Error
```

If the Citizen Service is unavailable:

```text
Complaint Service
       |
       X
Citizen Service unavailable
       |
       v
503 Service Unavailable
```

---

# Microservices Design Principles Used

## Independent Services

Citizen Service and Complaint Service run independently on different ports.

```text
Citizen Service → 5001
Complaint Service → 5002
```

## Independent Databases

Each service owns its own database.

```text
Citizen Service → citizen.db
Complaint Service → complaint.db
```

## REST-Based Communication

The services communicate through HTTP REST APIs.

```text
Complaint Service
       |
       | REST API
       v
Citizen Service
```

## Service Isolation

The Complaint Service does not directly access the Citizen Service database.

Instead, it uses:

```text
GET /citizens/<citizen_id>
```

to communicate with the Citizen Service.

---

# Git and GitHub

The project is maintained using Git and GitHub.

The project uses separate branches to manage development work safely.

Current development branch:

```text
citizen-service
```

The Citizen Service implementation and Citizen-Complaint REST integration have been committed and pushed to the development branch.

The group repository's main branch is maintained separately to prevent accidental overwriting of other team members' work.

---

# Current Team Work

This is a group project consisting of multiple microservices.

Current services:

* **Citizen Service** - Implemented
* **Complaint Service** - Implemented
* **Third Microservice** - To be decided after discussion with the instructor

The third microservice will be added after the requirements are finalized.

---

# Future Scope

The following features can be added in future development:

* Third microservice
* Integration with the third service
* Improved user interface
* Authentication and authorization
* More detailed complaint tracking
* Complaint status updates
* Ward-based complaint management
* Centralized API gateway
* Logging and monitoring
* Docker containerization
* Automated testing
* Improved error handling

---

# Conclusion

The Community Civic Microservices project demonstrates how a civic application can be divided into independent microservices.

The current implementation includes a Citizen Service and Complaint Service with separate databases and REST-based communication.

The Complaint Service validates citizens through the Citizen Service before creating complaints and handles valid citizen, invalid citizen, and unavailable-service scenarios appropriately.

The third microservice will be added after discussion and approval of the requirements.

