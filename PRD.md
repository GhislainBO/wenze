# WENZE - MVP Product Requirements Document (PRD)

**Concept:** Digital neighborhood marketplace
**Target cities:** Kinshasa 🇨🇩 (DRC) & Brazzaville 🇨🇬 (RC)

**Version:** 1.0
**Date:** April 2026

> **Language policy:** The final application is intended for French-speaking users.
> All UI text, labels, categories, button names, messages, and user-facing content
> MUST remain in French throughout the entire codebase.

---

## 1. PROJECT OVERVIEW

### 1.1 Mission

Mobile application enabling users to find and offer local services in Kinshasa (DRC) 🇨🇩 and Brazzaville (RC) 🇨🇬.

**Core concept:** Digital neighborhood marketplace

### 1.2 Vision

**UX objective:** Open → View → Contact (WhatsApp) in under 10 seconds

### 1.3 Critical product rules

- Open → View → Contact in < 10 seconds
- Maximum 1 tap to select the city
- Never display a standard country selector (dropdown / picker)
- Simple and clean design
- Do not over-engineer
- Comply with Android constraints

---

## 2. CONTEXTUAL ONBOARDING

Displayed on first launch only. Show a simple screen with the following text:

```
"Voir les Wenze près de :"
[ Kinshasa 🇨🇩 ]
[ Brazzaville 🇨🇬 ]
```

### Rules

- Maximum 1 tap
- No text input fields
- Simple design

### Persistence

- Store the user's choice locally (e.g. SharedPreferences or local JSON file)
- Never display this screen again after the first choice

### Automatic country detection

| Dialing code | Country | Internal code |
|--------------|---------|---------------|
| +243 | Democratic Republic of Congo (DRC) | RDC |
| +242 | Republic of Congo (RC) | RC |

---

## 3. FUNCTIONAL SPECIFICATIONS

### 3.1 MVP Scope - Phase 1

**Included features**

- Contextual onboarding screen (Kinshasa / Brazzaville)
- Service categories with Unicode emojis
- Multi-currency support (CDF for DRC, FCFA for RC)
- Price logic: `0` = display `"À discuter"`
- Direct WhatsApp button with automatic phone number sanitization
- Boost system (`is_boosted`, `boost_expiry`)
- Preloading: 5 Kinshasa services + 5 Brazzaville services at startup
- Click tracking endpoint

**Excluded from Phase 1**

- Integrated payment
- In-app chat
- Review / rating system

### 3.2 Service categories with emojis

> All category labels must remain in French in the UI.

| Emoji | Category (French label — keep as-is in UI) |
|-------|---------------------------------------------|
| 📚 | Soutien scolaire |
| 🔧 | Électricité & Maçonnerie |
| 💇 | Beauté & Coiffure |
| 🌿 | Jardinage |
| 🎣 | Pêche & Chasse |
| 🍽️ | Restauration & Promo |
| 🚗 | Transport & Livraison |
| 📱 | Téléphone & Informatique |

**Display rules**

- 1 emoji per category
- Emoji displayed in list views and service cards
- No emoji in form inputs

### 3.3 Currency management

| Country | Currency | Display format |
|---------|----------|----------------|
| DRC 🇨🇩 | CDF | 5000 CDF |
| RC 🇨🇬 | FCFA | 5000 FCFA |

**Price logic:**

- The `price` field is an Integer
- If `price == 0` → display French string `"À discuter"`
- Otherwise display the numeric price followed by the country's currency symbol

### 3.4 WhatsApp integration

**Implementation rules:**

- DRC → country code prefix `+243`
- RC → country code prefix `+242`
- Automatic phone number sanitization:
  - Strip spaces, dashes, dots
  - Prepend country code if missing
- One direct WhatsApp button per service card

### 3.5 Boost system

Add the following fields to the `Service` table:

- `is_boosted` : Boolean
- `boost_expiry` : DateTime (nullable)

> **Important:** No payment logic at this stage. Data structure only.

### 3.6 Location management

**Principle: Free-text input only — never a forced dropdown list**

Fields present in both `User` and `Service` tables:

- `country` : String — value is either `"RDC"` or `"RC"`
- `city_village` : String (free text)
- `neighborhood` : String (free text)

### 3.7 Performance strategy

**Preloading at startup:**

- 5 services from Kinshasa
- 5 services from Brazzaville

**Goal:** Instant display on app launch, no loading screen

---

## 4. TECHNICAL SPECIFICATIONS

### 4.1 Development environment

| Component | Technology |
|-----------|------------|
| OS | Ubuntu WSL |
| Terminal | Ghostty |
| Mobile framework | Kivy |
| Backend | FastAPI |
| Database | SQLite |

### 4.2 Backend API

**Phase 1 endpoints:**

- `GET /services` — List services
  - Query parameters: `country`, `city_village`, `category`
- `POST /services` — Create a service
- `POST /services/{id}/log-click` — Track a click event

### 4.3 Seed data

Create 20 realistic services:

**10 services — Kinshasa (DRC)**
- Neighborhoods: Gombe, Lingwala, Ngaliema, Lemba, Kintambo, etc.
- Prices in CDF
- Mixed prices (some set to `0` = `"À discuter"`)

**10 services — Brazzaville (RC)**
- Neighborhoods: Poto-Poto, Moungali, Talangaï, Bacongo, Makélékélé, etc.
- Prices in FCFA
- Mixed prices (some set to `0` = `"À discuter"`)

> All service titles, descriptions, and location names in seed data must be in French.

---

## 5. DATA MODEL

### 5.1 Entity: User

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| name | String | User full name |
| phone_number | String | Phone number |
| country | String | `"RDC"` or `"RC"` |
| city_village | String | City or village (free text) |
| neighborhood | String | Neighborhood (free text) |
| created_at | DateTime | Record creation timestamp |

### 5.2 Entity: Service

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| user_id | UUID | Foreign key → User |
| title | String | Service title (in French) |
| category | Enum | Category (see section 3.2) |
| description | Text | Detailed description (in French) |
| price | Integer | `0` = display `"À discuter"` |
| country | String | `"RDC"` or `"RC"` |
| city_village | String | City or village (free text) |
| neighborhood | String | Neighborhood (free text) |
| whatsapp_number | String | WhatsApp phone number |
| phone_number | String | Regular phone number |
| is_boosted | Boolean | Whether the service is boosted |
| boost_expiry | DateTime | Boost expiration timestamp (nullable) |
| status | Enum | `"active"` / `"inactive"` |
| created_at | DateTime | Record creation timestamp |

---

## 6. PHASE 1 TASK DEFINITION

**Hard constraints:**

- Do not over-engineer
- Do not code the entire application at once
- Comply with Android constraints

### Deliverables — Phase 1

1. **Create SQLite database**
   - Tables: `User`, `Service`
   - Fields: `country` (RDC/RC), `city_village`, `neighborhood`

2. **Configure FastAPI backend**
   - `GET /services`
   - `POST /services`
   - `POST /services/{id}/log-click`

3. **Create onboarding screen (Kivy)**
   - Buttons: `Kinshasa` / `Brazzaville` (French labels, keep as-is)
   - Persist user's city choice locally

4. **Insert seed data**
   - 10 Kinshasa services (prices in CDF)
   - 10 Brazzaville services (prices in FCFA)

5. **Provide a precise summary**
   - Files created
   - Files modified

6. **STOP and wait for user validation**

---

## 7. AGENT INSTRUCTIONS (CRITICAL)

You are a developer agent. You must strictly follow these rules:

1. Do not implement the entire application at once
2. Work ONLY on Phase 1
3. Do not add features not listed in this document
4. Do not modify the architecture without justification
5. Do not use libraries incompatible with Android / Buildozer
6. Do not use Python features above version 3.10

### Strict execution order

1. SQLite database
2. `User` and `Service` models
3. FastAPI backend (endpoints)
4. Seed data
5. Kivy onboarding screen

> **Do not invert this order.**

### Prohibited

- No payment system
- No in-app chat
- No complex authentication system
- No GPS geolocation
- No global refactor
- No heavy third-party dependencies

### Mobile constraints (Kivy)

- Simple code only
- No KivyMD in Phase 1
- No complex logic in the UI layer
- Minimal functional UI

### Validation criteria

Phase 1 is VALIDATED when ALL of the following are true:

- SQLite database is functional
- FastAPI API is running and responding
- Seed data is inserted
- Onboarding screen is working
- Kinshasa / Brazzaville choice is persisted locally

### Expected output

At the end of Phase 1, provide:

1. List of created files
2. List of modified files
3. Instructions to start the backend
4. Instructions to run the mobile app
5. Any issues encountered

> **IMPORTANT:** At the end of Phase 1: **STOP** — Wait for user validation before proceeding.

---

## 8. PLUGIN USAGE INSTRUCTIONS

You have access to the following plugins:

- `context7`
- `frontend-design`
- `document-skills`

### Usage rules

1. **ALWAYS choose the plugin best suited to the current task.**
2. Before acting, briefly state:
   - which plugin you are using
   - why you are using it

3. **Expected usage per plugin:**

   - **`context7`** — for any technical decision: API, framework, library, Android compatibility, Kivy, FastAPI, SQLite, Buildozer, or up-to-date documentation
   - **`frontend-design`** — for any user interface work: mobile screens, UX, visual layout, readability, or user experience
   - **`document-skills`** — for analyzing the PRD, structuring tasks, producing summaries, or staying aligned with product constraints

4. **Priority rules:**
   - Technical task → prefer `context7`
   - UX / UI task → prefer `frontend-design`
   - Project understanding / task structuring → prefer `document-skills`

5. Do not activate a plugin unnecessarily.
6. Do not use multiple plugins simultaneously unless justified.

**Objective:** Always use the plugin that maximizes output quality for the current phase.

---

## 9. LANGUAGE POLICY SUMMARY

| Context | Language |
|---------|----------|
| Code (variables, functions, comments) | English |
| UI labels, buttons, screen text | French |
| Category names | French |
| Service titles and descriptions (seed data) | French |
| Neighborhood and city names (seed data) | French |
| Error messages shown to the user | French |
| Internal API error messages and logs | English |

---

*WENZE PRD v1.0 — Digital neighborhood marketplace — Kinshasa 🇨🇩 & Brazzaville 🇨🇬*
