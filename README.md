# AI-Powered Food Saving & Smart Billing System for Restaurants

> From billing to intelligence — automatically reducing food waste through seamless AI integration.

## 🎯 Project Overview

An AI-powered system that silently learns from restaurant billing data to predict food demand, optimize inventory, and reduce food waste by up to **30%**. No ML expertise required from restaurant staff.

## 🏗️ Architecture

```
restaurant-ai-system/
├── frontend-react/          # React UI (Admin Dashboard, Billing Interface)
├── backend-springboot/      # Spring Boot REST API (Business Logic, Auth)
├── ml-service-python/       # Python Flask ML Service (Prediction Engine)
└── database/                # SQL Schema, Data Pipelines, BOM Mapping
```

## 🛠️ Technology Stack

| Layer       | Technology                                        |
| ----------- | ------------------------------------------------- |
| Frontend    | React, HTML/CSS                                   |
| Backend     | Spring Boot 3.2 (Java 17)                         |
| ML Engine   | Python, Pandas, Scikit-learn, XGBoost              |
| Database    | MySQL                                             |
| Security    | Spring Security, JWT, RBAC                        |

## 📊 Datasets

| Dataset                          | Records | Description                                  |
| -------------------------------- | ------- | -------------------------------------------- |
| Sales Data Analysis              | 255     | Western fast food transactions                |
| Balaji Fast Food Sales           | 1,000   | Indian street food transactions               |
| Restaurant Inventory (100 Days)  | 1,000   | Daily stock, usage, waste, supplier data      |

## 🚀 Getting Started

### Prerequisites
- Java 17+
- Node.js 18+
- Python 3.10+
- MySQL 8.0+

### Setup

1. **Database**: Run `database/schema.sql` to create tables
2. **Data Import**: Run `python database/import_and_preprocess.py`
3. **Backend**: `cd backend-springboot && mvn spring-boot:run`
4. **ML Service**: `cd ml-service-python && pip install -r requirements.txt && python app.py`
5. **Frontend**: `cd frontend-react && npm install && npm start`

## 📝 License

This project is for academic and research purposes.
