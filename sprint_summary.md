# Sprint Summary & Team Progress

This section summarizes the work completed on the **SEPTA Discord Status Bot** across the project timeline. Issues are grouped by the week they were created in Jira.

---

## Sprint 1: Week of Oct 20 – Oct 26

- **Total issues:** 2  
- **Ownership by teammate:**
  - **Chris Breeden — 2 issues**
- **Key completed work:**
  - **KAN-1:** Initial project proposal + bot architecture outline  
  - **KAN-4:** Setup of Jira board, workflow statuses, and team processes

---

## Sprint 2: Week of Oct 27 – Nov 02

- **Total issues:** 5  (Done: 5)
- **Ownership by teammate:**
  - **Justin Pham — 4 issues**
  - **Christine Kapp — 1 issue**
- **Work completed this sprint:**
  - Initial dropdown menu concept  
  - Next-train navigation logic via SEPTA API  
  - Major refactor: helper functions moved into separate file  
  - First implementation of station listing

---

## Sprint 3: Week of Nov 03 – Nov 09

- **Total issues:** 10  (Done: 10)
- **Ownership by teammate:**
  - **Jerry Lin — 4 issues**
  - **Christine Kapp — 3 issues**
  - **Justin Pham — 2 issues**
  - **Fares Hagos — 1 issue**
- **Notable work completed:**
  - Typo-tolerant station search (“Temple” from “tem”)  
  - Enhanced next-train logic & station grouping  
  - Station-to-line mapping system  
  - Fun bot interactions (cat spin, compliments)

---

## Sprint 4: Week of Nov 10 – Nov 16

- **Total issues:** 12  (Done: 7, In Progress: 5)
- **Ownership by teammate:**
  - **Justin Pham — 6 issues 
  - **Jerry Lin — 3 issues 
  - **Fares Hagos — 2 issues 
  - **Christine Kapp — 1 issue 
  - **Chris Breeden — 1 issue 
- **Key completed work:**
  - **KAN-13 — Alerts for when a station is down** 
  - Delay/status messaging improvements  
  - Per-line station sorting for dropdown menus  
  - Station list builder for Lansdale Line  
  - API error-handling improvements  
  - User-facing enhancements for commands

- **In-progress work this sprint:**
  - Finalizing dropdown menus  
  - Hardening subscription logic  
  - Finishing error-handling rewrite  
  - Mapping & dynamic menu enhancements

---

## Overall Contribution Summary

### **Chris Breeden**
- Led **initial project setup and workflow design**
- Built early API routing & logic used by the bot (KAN-3)
- Implemented **station-down alerting system** (KAN-13)
- Contributed to subscription system behavior & message routing

### **Justin Pham**
- Main developer for slash commands, UI components, dropdowns  
- Major contributor to SEPTA API integration work

### **Jerry Lin**
- Responsible for much of the station → line mapping  
- Improved `next_train` logic and fixed multiple edge cases  
- Created station grouping & refactor work

### **Christine Kapp**
- Subscription logic, removal of deprecated commands, bug fixes  
- Helped with alerts and dropdown improvements

### **Fares Hagos**
- Error handling rewrite, `/check line status` improvements  
- Documentation, architecture creation, overall polishing

---
