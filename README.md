Apex News Ninja

An AI-powered personalized news aggregation platform that fetches, analyzes, categorizes, and delivers relevant news in real time.

Overview

Apex News Ninja is a full-stack AI-powered news aggregation platform built to solve one major problem:

People waste hours scrolling through dozens of news websites to find information that actually matters to them.

Instead of visiting multiple websites, Apex News Ninja automatically collects news from multiple trusted sources, removes duplicates, categorizes articles using AI, analyzes sentiment, and delivers a personalized news feed based on each user's interests.

The platform was designed using a modern asynchronous architecture that prioritizes speed, scalability, and clean software engineering principles.

Features
Personalized News Feed

Users choose the topics they care about.

Examples include:

Artificial Intelligence
Technology
Cryptocurrency
Forex
Business
Politics
Sports
Entertainment
Health
World News

The backend only returns news matching the user's selected interests.

Multi-Source News Aggregation

Instead of relying on one provider, Apex News Ninja aggregates news from multiple APIs and RSS feeds.

Supported sources include:

NewsAPI
GNews
The Guardian API
MediaStack
Currents API
RSS Feeds
Additional configurable news providers

The system normalizes every response into one common format regardless of the original API.

AI Categorization

Every article is automatically categorized.

Example:

Input:

"Nvidia launches new AI chips for enterprise"

↓

Category:

Artificial Intelligence
Technology
Business

This allows articles from different APIs to be grouped consistently.

AI Sentiment Analysis

Using Google's Gemini API, every article is analyzed for sentiment.

Possible outputs:

Positive

Neutral

Negative

Example:

Headline	Sentiment
Bitcoin reaches new all-time high	Positive
Global recession fears increase	Negative
Apple announces quarterly earnings	Neutral
Duplicate Detection

Multiple news providers often publish the exact same story.

The backend detects duplicates by comparing:

Title
URL
Source
Published timestamp

Only one version is stored.

User Authentication

Supports:

JWT Authentication
Email registration
Password hashing
Google OAuth Login

Users have individual accounts and personalized feeds.

Search

Users can search articles by:

Keyword
Category
Source
Date
Filters

Users can filter by:

Category
News source
Date
Sentiment
Trending articles
Scheduler

The backend automatically updates itself.

Using APScheduler:

06:00 UTC

14:00 UTC

22:00 UTC

At every scheduled run the system:

Fetches articles
Removes duplicates
Runs AI categorization
Runs sentiment analysis
Saves results

No manual work required.

Admin Endpoints

Administrators can:

Trigger manual news fetch
Rebuild database
Refresh categories
View logs
Monitor API health
System Architecture
                 +---------------------+
                 |     React Frontend  |
                 +----------+----------+
                            |
                            |
                     REST API (FastAPI)
                            |
        +-------------------+-------------------+
        |                                       |
 Authentication                    News Service
        |                                       |
        |                            Fetch Multiple APIs
        |                                       |
 MongoDB Users                       Normalization
                                            |
                                     Duplicate Removal
                                            |
                                  AI Categorization
                                            |
                                  Gemini Sentiment
                                            |
                                      MongoDB News
Technology Stack
Frontend
React
Vite
Tailwind CSS
React Router
Axios
Framer Motion
Backend
FastAPI
Python
Pydantic
Motor
JWT
OAuth2
APScheduler
HTTPX
Database

MongoDB

Async access through Motor.

Collections:

users

news

logs

preferences

tokens
AI

Google Gemini

Used for:

News categorization
Sentiment analysis
Future article summarization
Authentication

JWT Tokens

Password hashing

Google OAuth

Development Tools
VS Code / Claude Code
Git
GitHub
Postman
MongoDB Compass
Folder Structure
apex-news-ninja/

│
├── app/
│   ├── api/
│   ├── auth/
│   ├── config/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── scheduler/
│   ├── ai/
│   ├── utils/
│   └── main.py
│
├── frontend/
│   ├── src/
│   ├── pages/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   └── assets/
│
├── tests/
│
├── requirements.txt
│
├── .env
│
└── README.md
Database Design
Users
{
  "_id": ObjectId,
  "name": "John Doe",
  "email": "john@email.com",
  "password": "...",
  "preferences": [
      "AI",
      "Crypto",
      "Business"
  ],
  "created_at": "...",
  "updated_at": "..."
}
News
{
  "_id": ObjectId,
  "title": "...",
  "summary": "...",
  "content": "...",
  "category": "AI",
  "sentiment": "Positive",
  "source": "NewsAPI",
  "url": "...",
  "image": "...",
  "published_at": "...",
  "created_at": "..."
}
Logs
{
  "_id": ObjectId,
  "type": "FETCH",
  "status": "SUCCESS",
  "message": "...",
  "timestamp": "..."
}
API Workflow
Scheduler

↓

Fetch Articles

↓

Normalize Response

↓

Remove Duplicates

↓

Run AI Categorization

↓

Run Gemini Sentiment Analysis

↓

Store in MongoDB

↓

Serve Personalized Feed

↓

Display in React
REST API
Authentication
POST /auth/register

POST /auth/login

POST /auth/google

POST /auth/refresh
Users
GET /users/me

PATCH /users/preferences

DELETE /users/account
News
GET /news/feed

GET /news/trending

GET /news/category/{category}

GET /news/search

GET /news/{id}
Admin
POST /admin/fetch

POST /admin/rebuild

GET /admin/logs
Security
JWT Authentication
Password hashing (bcrypt/Argon2)
Environment variables
Request validation using Pydantic
Rate limiting
Duplicate request prevention
Input sanitization
Secure API key management
CORS configuration
Performance Optimizations
Fully asynchronous FastAPI backend
Async MongoDB driver (Motor)
Connection pooling
Scheduled background jobs
Duplicate detection
Indexed MongoDB collections
Lazy loading on frontend
Pagination
Response caching (planned)
AI processing pipeline optimization
Future Roadmap
AI-generated summaries for every article
Topic clustering using embeddings
Breaking news notifications
Email newsletter delivery
Mobile application (React Native)
User bookmarks and reading history
AI chatbot for querying news
Personalized recommendation engine
Voice news summaries
Multilingual support
Real-time WebSocket updates
Analytics dashboard
Docker and Kubernetes deployment
CI/CD with GitHub Actions
Redis caching
Elasticsearch-powered search
Role-based access control (RBAC)
Installation
git clone https://github.com/yourusername/apex-news-ninja.git

cd apex-news-ninja

Install backend dependencies:

pip install -r requirements.txt

Run MongoDB locally or configure a MongoDB Atlas connection in your .env file.

Start the backend:

uvicorn app.main:app --reload

Navigate to the frontend directory:

cd frontend
npm install
npm run dev

The backend will be available at http://127.0.0.1:8000, and the frontend at the Vite development server (typically http://localhost:5173).

What I Learned

Building Apex News Ninja strengthened practical experience in:

Designing scalable REST APIs with FastAPI
Building asynchronous Python applications
Integrating multiple third-party news APIs
Designing MongoDB schemas and indexes
Implementing JWT-based authentication
Creating scheduled background jobs with APScheduler
Applying AI for text classification and sentiment analysis
Building responsive React interfaces
Managing API rate limits, duplicate detection, and data normalization
Structuring production-ready full-stack applications using modern software engineering practices
License

This project is licensed under the MIT License.
