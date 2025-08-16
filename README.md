# 🎓 Better Transfer  
**AI-powered transfer planning for community college students**

Better Transfer is a research project exploring how **Retrieval Augmented Generation (RAG)** can help community college students plan their academic path when transferring to four-year universities. It consolidates articulation agreements, university requirements, and course data into clear, optimized transfer plans.  

---

## 🚀 Features

- **RAG-Powered Plans** – Uses OpenAI embeddings + GPT to generate transfer plans.  
- **Multi-University Support** – Build a single plan that satisfies multiple target universities and majors.  
- **Configurable Dashboard** – Adjust difficulty, semesters, and course preferences via an interactive board.  
- **Optimized Course Sequencing** – Plans respect prerequisites and minimize duplicate courses.  
- **Caching for Speed** – Redis + MongoDB caching accelerates responses.  
- **Developer-Friendly** – Includes seeding scripts, Docker compose stack, and FastAPI endpoints.  

---

## 🖥️ Screenshots

| Configuration Board | Transfer Plan |
|---------------------|---------------|
| <img width="1911" height="912" alt="Config Board" src="https://github.com/user-attachments/assets/aee57166-5478-4fac-8436-a121c91e40bb" /> | <img width="1738" height="827" alt="Plan" src="https://github.com/user-attachments/assets/5cb0c9da-f2bd-41b3-9441-4176e18bc388" /> |

---

## 📦 Sample Response  

Example: Better Transfer generates a plan that satisfies:  
- 🎯 **UCLA – Computer Science**  
- 🎯 **UC Berkeley – Data Science**  
- 🏫 From: **Pasadena City College**  

👉 View the full optimized JSON plan:  
[`examples/multi_university_sample.json`](./examples/multi_university_sample.json)  

---

## 🛠️ Tech Stack  

- **Backend:** FastAPI (async endpoints)  
- **Database:** MongoDB (vector index, transfer data)  
- **Caching:** Redis + MongoDB  
- **AI Layer:** OpenAI embeddings + GPT synthesis  
- **Deployment:** Docker Compose  

---

## ⚙️ Getting Started  

1. Install Python dependencies:  
   ```bash
   pip install -r requirements.txt
