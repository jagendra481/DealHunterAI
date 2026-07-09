# 🏗 DealHunterAI Architecture

## Overview

DealHunterAI is an AI-powered affiliate price tracking platform that monitors products, detects price drops, and notifies users through Telegram while providing a modern web dashboard.

---

## System Flow

User
│
▼
Dashboard (Flask)
│
▼
ProductService
│
▼
Database (SQLite)
│
▼
Scheduler
│
▼
Amazon Provider
│
▼
Rainforest API
│
▼
Price Comparator
│
▼
Telegram Bot

---

## Project Structure

DealHunterAI/

admin/

config/

dashboard/

database/

docs/

engine/

providers/

scheduler/

services/

sources/

utils/

---

## Technologies

- Python
- Flask
- SQLite
- Rainforest API
- Telegram Bot API
- Bootstrap 5

---

## Future Architecture

- Analytics Engine
- AI Deal Score
- Multi-user Authentication
- REST API
- Cloud Deployment
