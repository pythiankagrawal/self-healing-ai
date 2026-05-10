# 📊 Intelligent Multi-Agent FinOps & Architecture Optimization System

## 🚀 Overview

This project is an AI-powered **multi-agent system** that analyzes cloud architecture descriptions and generates:

- 📦 Extracted cloud components  
- 🔍 Missing field detection & clarification  
- ⚙️ Architecture expansion (pipeline enrichment)  
- 💰 Cost estimation (multi-cloud ready)  
- 📈 Optimization recommendations *(in progress)*  

👉 Goal:  
**“Estimate cloud cost from plain English architecture + suggest optimizations.”**

---

## 🧠 Problem Statement

Modern cloud systems are:

- Complex (GCP, AWS, Azure mixed)
- Poorly documented
- Hard to estimate cost manually
- Require deep FinOps expertise

---

## 🎯 Solution

We built a **modular AI agent pipeline**:


User Input (Architecture)
↓
🧠 Intent Agent
↓
🤖 Parser Agent (LLM + Rules)
↓
🧹 Schema Validator (Normalizer)
↓
❓ Clarifier Agent (LLM-driven Q&A)
↓
⚙️ Expander Agent (Pipeline enrichment)
↓
💰 Cost Engine
↓
📊 Report + DAG Agent
↓
📈 Optimization Engine (future)


## 🏗️ Architecture (Agents)

### 1️⃣ Intent Agent
**Purpose:** Understand *what kind of system* user is describing

**Outputs:**
- LOGGING
- ETL
- STREAMING
- STORAGE
- API

**How it works:**
- Rule-based (fast)
- LLM fallback (smart)

---

### 2️⃣ Parser Agent
**Purpose:** Convert natural language → structured components

**Extracts:**
- `name`
- `type`
- `region`

**Features:**
- Rule-based parsing (reliable)
- LLM fallback (flexible)
- Handles messy input

---

### 3️⃣ Schema Validator (Core Layer)
**Purpose:** Fix LLM hallucinations

**Fixes:**
- Wrong keys (`namener`, `typetp`)
- Missing values
- Invalid formats

👉 Ensures **clean structured JSON always**

---

### 4️⃣ Clarifier Agent (🧠 Intelligent)

**Purpose:** Ask only *important missing questions*

### 🔥 Key Upgrade:
- LLM-driven questions (not rule-based)
- Max 2–3 questions only
- Focus on **cost drivers**

### Examples of smart questions:
- Data size per run
- Compute hours
- Throughput
- Frequency (daily/hourly)

### Features:
- Signal extraction (`daily`, `real-time`)
- Intent-aware questioning
- Fallback logic (if LLM fails)

---

### 5️⃣ Expander Agent

**Purpose:** Convert simple input → real pipeline

### Example:

Input:
GCS → BigQuery

Output:
GCS → Pub/Sub → Dataflow → BigQuery


### Features:
- Intent-aware expansion
- No over-expansion for simple cases (e.g., logging)
- Deduplication
- Logical pipeline building

---

### 6️⃣ Cost Engine

**Purpose:** Estimate cost per component

### Supports:
- Object Storage
- Streaming (Pub/Sub)
- Compute (Dataflow)
- Data Warehouse (BigQuery)
- API Layer

### Features:
- Region-aware pricing
- Component-wise breakdown
- Total cost calculation

---

### 7️⃣ Report + DAG Agent

**Purpose:** Make output understandable

### Generates:
- 🧩 DAG (ordered architecture)
- 📈 Mermaid diagram
- 💰 Cost distribution
- 🧠 Insights

### Example:

gcs → pubsub → dataflow → bigquery


---

### 8️⃣ Optimization Engine (🚧 In Progress)

**Goal:** Suggest cost savings

### Planned:
- Remove unnecessary services
- Replace expensive components
- Suggest batch vs streaming
- Region optimization

---

## 🧪 Example

🚀 Intelligent FinOps Advisor
----------------------------------
Paste your architecture (press ENTER twice to finish):

loads logs data into gcs


🤖 Intelligent Parser Agent starting...

🔍 RAW PARSER OUTPUT:
["gcs"]

🧠 EXTRACTED SERVICES:
['gcs']

✅ FINAL PARSED COMPONENTS
[
  {
    "name": "gcs",
    "type": "Object Storage",
    "provider": "gcp",
    "region": "global"
  }
]

🧠 LLM-Only Intent Agent starting...

🔍 RAW INTENT OUTPUT:
 ```json
{
  "primary_intent": "Load logs data into GCS",
  "secondary_intents": [],
  "architecture_pattern": "",
  "workload_characteristics": {
    "stateful": false,
    "event_driven": false,
    "latency_sensitive": false,
    "compute_intensive": false,
    "storage_intensive": false
  },
  "signals": {
    "frequency": "",
    "realtime": false,
    "batch": true,
    "cloud_provider": "gcp",
    "region": "global"
  },
  "components_detected": [
    {
      "name": "gcs",
      "type": "Object Storage",
      "provider": "gcp",
      "region": "global"
    }
  ],
  "missing_information": [],
  "confidence": 0.8
}
```

✅ FINAL INTENT ANALYSIS
{
  "primary_intent": "Load logs data into GCS",
  "secondary_intents": [],
  "architecture_pattern": "",
  "workload_characteristics": {
    "stateful": false,
    "event_driven": false,
    "latency_sensitive": false,
    "compute_intensive": false,
    "storage_intensive": false
  },
  "signals": {
    "frequency": "",
    "realtime": false,
    "batch": true,
    "cloud_provider": "gcp",
    "region": "global"
  },
  "components_detected": [
    {
      "name": "gcs",
      "type": "Object Storage",
      "provider": "gcp",
      "region": "global"
    }
  ],
  "missing_information": [],
  "confidence": 0.8,
  "source": "llm"
}

🤖 Intelligent Expander Agent starting...

🔍 RAW EXPANDER OUTPUT:
[
  {
    "name": "pubsub",
    "region": "us-east1"
  }
]

✅ FINAL EXPANDED ARCHITECTURE
[
  {
    "name": "gcs",
    "type": "Object Storage",
    "provider": "gcp",
    "region": "global"
  },
  {
    "name": "pubsub",
    "type": "Streaming Queue",
    "provider": "gcp",
    "region": "us-east1"
  }
]

🤖 Intelligent Clarifier Agent starting...
⚠️ Retry 1 failed: Timeout

🔍 RAW CLARIFIER OUTPUT:
[
  {
    "field": "data_size_per_day",
    "question": "How much data is processed per day (GB/TB)?"
  },
  {
    "field": "retention_days",
    "question": "How long should logs/data be retained?"
  },
  {
    "field": "throughput_mb_per_sec",
    "question": "What is the expected throughput in MB/second for streaming data?"
  },
  {
    "field": "compute_hours_per_day",
    "question": "How many hours per day are required for compute processing?"
  },
  {
    "field": "monthly_storage",
    "question": "What is the estimated monthly storage requirement (GB/TB)?"
  }
]

🧠 Intelligent Workload Questions:

→ How much data is processed per day (GB/TB)?: 10 GB
→ How long should logs/data be retained?: 10 days
→ What is the expected throughput in MB/second for streaming data?: 3 mb/sec
→ How many hours per day are required for compute processing?: 3 hours
→ What is the estimated monthly storage requirement (GB/TB)?: 100 GB

✅ ENRICHED WORKLOAD PROFILE
[
  {
    "name": "gcs",
    "type": "Object Storage",
    "provider": "gcp",
    "region": "global",
    "workload_profile": {
      "data_size_per_day": "10 GB",
      "retention_days": "10 days",
      "throughput_mb_per_sec": "3 mb/sec",
      "compute_hours_per_day": "3 hours",
      "monthly_storage": "100 GB"
    }
  },
  {
    "name": "pubsub",
    "type": "Streaming Queue",
    "provider": "gcp",
    "region": "us-east1",
    "workload_profile": {
      "data_size_per_day": "10 GB",
      "retention_days": "10 days",
      "throughput_mb_per_sec": "3 mb/sec",
      "compute_hours_per_day": "3 hours",
      "monthly_storage": "100 GB"
    }
  }
]

📦 FINAL COMPONENTS:
[{'name': 'gcs', 'type': 'Object Storage', 'provider': 'gcp', 'region': 'global', 'workload_profile': {'data_size_per_day': '10 GB', 'retention_days': '10 days', 'throughput_mb_per_sec': '3 mb/sec', 'compute_hours_per_day': '3 hours', 'monthly_storage': '100 GB'}}, {'name': 'pubsub', 'type': 'Streaming Queue', 'provider': 'gcp', 'region': 'us-east1', 'workload_profile': {'data_size_per_day': '10 GB', 'retention_days': '10 days', 'throughput_mb_per_sec': '3 mb/sec', 'compute_hours_per_day': '3 hours', 'monthly_storage': '100 GB'}}]

💰 Intelligent Cost Agent starting...
⚠️ Retry 1 failed: Timeout

🔍 RAW COST OUTPUT:
{
  "total_cost": 20.0,
  "currency": "USD",
  "breakdown": [
    {
      "name": "gcs",
      "type": "Object Storage",
      "monthly_cost": 5.0,
      "reason": "Baseline cost for object storage"
    },
    {
      "name": "pubsub",
      "type": "Streaming Queue",
      "monthly_cost": 15.0,
      "reason": "Baseline cost for streaming queue, including compute hours"
    }
  ],
  "assumptions": [
    "Assuming baseline costs and no additional features or optimizations."
  ],
  "optimizations": [
    "Consider using more cost-effective storage classes if data access patterns allow."
  ]
}

💰 FINAL COST REPORT
{
  "total_cost": 20.0,
  "currency": "USD",
  "breakdown": [
    {
      "name": "gcs",
      "type": "Object Storage",
      "monthly_cost": 5.0,
      "reason": "Baseline cost for object storage"
    },
    {
      "name": "pubsub",
      "type": "Streaming Queue",
      "monthly_cost": 15.0,
      "reason": "Baseline cost for streaming queue, including compute hours"
    }
  ],
  "assumptions": [
    "Assuming baseline costs and no additional features or optimizations."
  ],
  "optimizations": [
    "Consider using more cost-effective storage classes if data access patterns allow."
  ]
}

📊 Intelligent Report Agent starting...

====================================
📘 FINAL FINOPS ARCHITECTURE REPORT
====================================

🧠 EXECUTIVE SUMMARY:
This architecture represents a Load logs data into GCS workload using 2 cloud services following a  design with an estimated monthly cost of $20.0.

🏗️ ARCHITECTURE COMPONENTS:
- pubsub (Streaming Queue) [us-east1]
- gcs (Object Storage) [global]

📈 MERMAID DIAGRAM:
graph LR
pubsub["pubsub<br/>Streaming Queue"]
gcs["gcs<br/>Object Storage"]
pubsub --> gcs

💰 TOTAL ESTIMATED MONTHLY COST:
$20.0

📦 COST BREAKDOWN:
- gcs (Object Storage) → $5.0
- pubsub (Streaming Queue) → $15.0

⚠️ RISKS:
- Streaming workloads should include monitoring/alerting

🧠 RECOMMENDATIONS:
- Enable lifecycle tiering for object storage
- Tune retention and throughput settings for streaming workloads

====================================

====================================
💰 FINAL FINOPS REPORT
====================================

TOTAL COST: 20.0 USD

BREAKDOWN:
- gcs (Object Storage) → $5.0
  Reason: Baseline cost for object storage
- pubsub (Streaming Queue) → $15.0
  Reason: Baseline cost for streaming queue, including compute hours

📘 ASSUMPTIONS:
- Assuming baseline costs and no additional features or optimizations.

🧠 OPTIMIZATIONS:
- Consider using more cost-effective storage classes if data access patterns allow.

====================================

```
### ⚠️ Key Challenges Solved
Problem	                  Solution
LLM hallucinations	 Schema Validator
Missing fields	         Clarifier Agent
Over-questioning	 LLM-based prioritization
Bad pipelines	         Intent-aware Expander
Cost inaccuracies	 Deterministic pricing


### 🧠 Key Learnings
❌ LLMs are not reliable structured parsers
✅ Always use validation layer
❌ Don’t rely only on rules
✅ Hybrid (Rules + LLM) = Best
❌ Ask everything → bad UX
✅ Ask only cost-critical questions


### 🚀 Current Status
Component	Status
Intent Agent	✅ Stable
Parser	        ✅ Stable
Schema Validator	✅ Done
Clarifier	⚠️ Improving
Expander	⚠️ Improving
Cost Engine	✅ Working
Report Agent	✅ Working
Optimization Engine	🚧 In Progress


🔮 Future Roadmap

## Phase 2 — Intelligence Upgrade
🧠 Dependency Graph Builder (true DAG)
💡 Smart Optimization Engine
🌍 Real Cloud Pricing APIs


## Phase 3 — Enterprise System
📄 PDF Report Generator
📊 Dashboard UI
🤖 Self-healing pipeline agent
📉 Cost heatmaps
🧩 Visual architecture graphs


## 🧰 Tech Stack

Python 3.10+
Ollama (LLM)
JSON / Regex parsing
Multi-agent architecture
Custom cost engine


## 🏁 Conclusion

This project evolves from:

➡️ Simple cost calculator
➡️ → AI-powered FinOps advisor
➡️ → Autonomous cloud intelligence system


## 👨‍💻 Use Cases
FinOps engineers
Cloud architects
DevOps teams
AI infra researchers


## 📌 Author Note

This system is designed to be:

Modular
Extensible
Production-scalable
LLM + deterministic hybrid

## ⭐ Future Vision

👉 “Describe your architecture in English → Get cost + optimization + architecture diagram instantly.”


