# Community Civic Microservices

A microservices-based Community Civic Portal designed to manage citizen information, civic complaints, and emergency reports through independent services communicating using REST APIs.

This project is developed as a group project. Each microservice has its own backend, frontend, and database where required.

---

## Project Overview

The Community Civic Portal provides a platform for:

- Managing citizen information
- Registering and tracking civic complaints
- Reporting and managing emergencies
- Providing a centralized API Gateway
- Load balancing multiple Complaint Service instances
- Applying API rate limiting and basic security headers at the Gateway

The current `emergency-service` branch contains:

1. **Citizen Service**
2. **Complaint Service**
3. **Emergency Service**
4. **API Gateway**

The Citizen Service stores citizen information.

The Complaint Service verifies citizens through the Citizen Service before registering a complaint.

The Emergency Service verifies citizens through the Citizen Service before registering an emergency.

The API Gateway provides a single entry point and routes requests to the correct service. It also load-balances Complaint Service requests between ports `5002` and `5004`.

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
       Citizen Service     Complaint Service     Emergency Service
           :5001            :5002 / :5004            :5003
              |                   |                   |
              v                   v                   v
         citizen.db         complaint.db          emergency.db
```

### Service Communication

```text
Complaint Service
       |
       | GET /citizens/<citizen_id>
       v
Citizen Service :5001
       |
       v
citizen.db
```

```text
Emergency Service
       |
       | GET /citizens/<citizen_id>
       v
Citizen Service :5001
       |
       v
citizen.db
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
├── emergency-service/
│   ├── backend/
│   │   └── app.py
│   ├── database/
│   │   └── emergency.db
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

It is an independent Flask microservice with its own SQLite database.

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
    "ward": "12",
    "phone": "9998887770",
    "gender": "male"
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

It verifies the citizen through the Citizen Service before creating a complaint.

### Primary Port

```text
5002
```

### Second Instance

```text
5004
```

The API Gateway uses ports `5002` and `5004` as two Complaint Service instances for round-robin load balancing.

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

Example request:

```json
{
    "citizen_id": 1,
    "description": "Large pothole near college gate",
    "location": "Ward 12"
}
```

### Get Complaint

```text
GET /complaints/<complaint_id>
```

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

Before creating a complaint, the Complaint Service calls:

```text
GET http://localhost:5001/citizens/<citizen_id>
```

### Possible Results

- `200 OK` → citizen exists and complaint is created
- `404 Not Found` → citizen does not exist and complaint is rejected
- `503 Service Unavailable` → Citizen Service is unavailable

---

# 3. Emergency Service

## Description

The Emergency Service is responsible for reporting, retrieving, and updating emergency incidents.

It is an independent Flask microservice with its own SQLite database.

Before creating an emergency, it verifies that the supplied citizen ID exists by communicating with the Citizen Service.

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
emergency-service/database/emergency.db
```

---

## Emergency API Endpoints

### Report Emergency

```text
POST /emergencies
```

Required information includes:

- Citizen ID
- Emergency type
- Description
- Location
- Severity

Example request:

```json
{
    "citizen_id": 1,
    "type": "Medical",
    "description": "Medical emergency reported",
    "location": "Ward 12",
    "severity": "HIGH"
}
```

A newly reported emergency starts with:

```text
REPORTED
```

---

### Get All Emergencies

```text
GET /emergencies
```

Returns all emergency records.

---

### Get Emergency by ID

```text
GET /emergencies/<emergency_id>
```

Example:

```text
GET /emergencies/1
```

If the emergency does not exist:

```text
404 Not Found
```

---

### Update Emergency Status

```text
PUT /emergencies/<emergency_id>/status
```

Example request:

```json
{
    "status": "IN_PROGRESS"
}
```

Supported statuses:

```text
REPORTED
IN_PROGRESS
RESOLVED
CANCELLED
```

---

## Emergency Service and Citizen Service Communication

The Emergency Service does not directly access `citizen.db`.

Instead, it sends:

```text
GET /citizens/<citizen_id>
```

to the Citizen Service.

The communication flow is:

```text
Emergency Service :5003
          |
          | REST API
          v
Citizen Service :5001
          |
          v
     citizen.db
```

If the citizen does not exist, the emergency is not created.

---

# 4. API Gateway

## Description

The API Gateway acts as the single entry point for client requests.

It forwards requests to the appropriate microservice and hides the internal service ports from clients.

The Gateway also provides:

- API versioning
- Complaint Service load balancing
- Round-robin request distribution
- Rate limiting
- Request logging
- Basic security headers
- Service-unavailable handling

### Port

```text
5000
```

### Base URL

```text
http://127.0.0.1:5000
```

---

## API Gateway Routing

| Gateway Route | Target Service |
|---|---|
| `/api/v1/citizens/*` | Citizen Service `:5001` |
| `/api/v1/complaints/*` | Complaint Service `:5002` / `:5004` |
| `/api/v1/emergencies/*` | Emergency Service `:5003` |

---

## Citizen Route

```text
/api/v1/citizens/*
```

Forwarded to:

```text
http://localhost:5001
```

Example:

```text
POST http://localhost:5000/api/v1/citizens
```

---

## Complaint Route

```text
/api/v1/complaints/*
```

Requests are distributed between:

```text
http://localhost:5002
http://localhost:5004
```

The Gateway uses **Round Robin** load balancing.

Example:

```text
Request 1 → Complaint Service :5002
Request 2 → Complaint Service :5004
Request 3 → Complaint Service :5002
Request 4 → Complaint Service :5004
```

---

## Emergency Route

```text
/api/v1/emergencies/*
```

Forwarded to:

```text
http://localhost:5003
```

Example:

```text
POST http://localhost:5000/api/v1/emergencies
```

The Gateway forwards the request to:

```text
POST http://localhost:5003/emergencies
```

---

# API Gateway Rate Limiting

The Gateway applies a rate limit of:

```text
100 requests per minute per client
```

If the client exceeds the limit:

```text
429 Too Many Requests
```

---

# API Gateway Security Headers

The Gateway adds security headers such as:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

---

# API Gateway Request Logging

The Gateway logs incoming requests including:

- HTTP method
- Request path
- Client IP address

This helps with monitoring and debugging.

---

# Service Unavailability Handling

If a backend service cannot be reached, the Gateway returns:

```text
503 Service Unavailable
```

---

# Complete Request Flow

## Citizen Registration

```text
Client
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
Client
  |
  v
API Gateway :5000
  |
  v
Complaint Service
 :5002 or :5004
  |
  | GET /citizens/<citizen_id>
  v
Citizen Service :5001
  |
  v
citizen.db
```

The Complaint Service then stores the complaint in:

```text
complaint.db
```

---

## Emergency Reporting

```text
Client
  |
  v
API Gateway :5000
  |
  v
Emergency Service :5003
  |
  | GET /citizens/<citizen_id>
  v
Citizen Service :5001
  |
  v
citizen.db
```

After successful citizen verification:

```text
Emergency Service
       |
       v
emergency.db
```

---

# Running the Application

For complete functionality, run the required services in separate terminals.

## 1. Start Citizen Service

```bash
cd citizen-service\backend
python app.py
```

Runs on:

```text
http://127.0.0.1:5001
```

---

## 2. Start Complaint Service Instance 1

```bash
cd complaint-service\backend
python app.py
```

Runs on:

```text
http://127.0.0.1:5002
```

---

## 3. Start Complaint Service Instance 2

The API Gateway is configured for a second Complaint Service instance on:

```text
http://127.0.0.1:5004
```

Run the Complaint Service using the appropriate port configuration for the second instance.

---

## 4. Start Emergency Service

```bash
cd emergency-service\backend
python app.py
```

Runs on:

```text
http://127.0.0.1:5003
```

---

## 5. Start API Gateway

```bash
cd api-gateway
python app.py
```

Runs on:

```text
http://127.0.0.1:5000
```

---

# Running the Frontend

## Citizen Frontend

```text
citizen-service/frontend/index.html
```

Used to:

- Register citizens
- Enter citizen details
- Retrieve citizens using their ID

---

## Complaint Frontend

```text
complaint-service/frontend/index.html
```

Used to:

- Enter a Citizen ID
- Submit a civic complaint
- Enter complaint description
- Enter location
- Track a complaint

---

## Emergency Frontend

```text
emergency-service/frontend/index.html
```

Used to:

- Report an emergency
- Enter Citizen ID
- Select emergency type
- Enter description
- Enter location
- Specify severity
- View emergency information
- Update emergency status

---

# Installation

## Prerequisites

Install:

- Python 3
- Git
- A web browser
- Visual Studio Code (recommended)

## Install Python Dependencies

```bash
pip install flask flask-cors requests
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

## Architecture

- Microservices
- REST APIs
- API Gateway
- Load Balancing
- Rate Limiting

## Version Control

- Git
- GitHub

---

# Microservices Design Principles

## Independent Services

```text
Citizen Service    → 5001
Complaint Service  → 5002 / 5004
Emergency Service  → 5003
API Gateway        → 5000
```

Each service has a separate responsibility.

---

## Independent Databases

```text
Citizen Service    → citizen.db
Complaint Service  → complaint.db
Emergency Service  → emergency.db
```

Each service owns its own database.

---

## REST-Based Communication

```text
Complaint Service
       |
       | REST API
       v
Citizen Service
```

```text
Emergency Service
       |
       | REST API
       v
Citizen Service
```

---

## Service Isolation

No service directly accesses another service's database.

For example:

```text
Emergency Service
       X
       |
       X
citizen.db
```

Instead, the Emergency Service requests citizen information through:

```text
GET /citizens/<citizen_id>
```

---

## Single Entry Point

The API Gateway provides one central endpoint:

```text
http://localhost:5000
```

It routes requests to the appropriate microservice.

---

## Load Balancing

The Complaint Service has two instances:

```text
Complaint Service :5002
Complaint Service :5004
```

The API Gateway distributes requests using:

```text
Round Robin
```

---

## Rate Limiting

The Gateway limits clients to:

```text
100 requests per minute
```

This helps prevent excessive requests from a single client.

---

# Service Dependency

The current service dependencies are:

```text
Complaint Service
        |
        | REST
        v
Citizen Service
```

```text
Emergency Service
        |
        | REST
        v
Citizen Service
```

The API Gateway connects clients to all services:

```text
                  API Gateway
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
    Citizen       Complaint      Emergency
    Service        Service        Service
```

---

# Updating Services Safely

Each microservice can be developed and updated independently.

For example, changes inside:

```text
emergency-service/
```

do not directly modify:

```text
complaint-service/
```

or:

```text
citizen-service/
```

However, the Emergency Service depends on the Citizen Service API:

```text
GET /citizens/<citizen_id>
```

Therefore, if the Citizen Service API endpoint or response format is changed, the Emergency Service may also need to be updated.

Similarly, the Complaint Service depends on the Citizen Service API.

As long as the REST API contracts remain compatible, each service can be maintained independently.

---

# Future Scope

- Authentication and authorization
- Improved frontend design
- Emergency notifications
- Real-time emergency updates
- Admin dashboard
- Advanced emergency prioritization
- Centralized logging and monitoring
- Docker containerization
- Automated testing
- API documentation
- Cloud deployment
- More sophisticated load balancing
- Service health checks and automatic failover

---

# Conclusion

The Community Civic Microservices project demonstrates how a civic application can be divided into independent microservices.

The current `emergency-service` branch contains:

- Citizen Service
- Complaint Service
- Emergency Service
- API Gateway

Each service has a clearly separated responsibility and its own database.

The Complaint Service and Emergency Service communicate with the Citizen Service through REST APIs for citizen validation.

The API Gateway provides a centralized entry point, routes requests using versioned API paths, load-balances Complaint Service instances, applies rate limiting, logs requests, and adds basic security headers.

This architecture demonstrates important microservices principles including service independence, database isolation, REST-based communication, API Gateway routing, load balancing, and controlled request handling.
