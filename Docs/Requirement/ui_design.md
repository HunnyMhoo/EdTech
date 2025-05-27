# Product Design Document – Thai Self-Learning App (MVP – Mobile)

## 1. Overview

### Product Goal
Build a mobile-first, no-video, no-tutor learning app to help Thai high school students self-study effectively for high-stakes exams (starting with GAT เชื่อมโยง). The app delivers adaptive, text-based content with instant feedback, gamified motivation, and minimal friction using LINE login.

---

## 2. User Flows Covered in MVP

1. Onboarding and LINE login  
2. Home screen with daily mission  
3. Lesson view (text-based scrollable format)  
4. Quiz interface with answer submission and feedback  
5. Progress tracking dashboard  
6. LINE OA integration trigger points  
7. Admin/CMS frontend (optional web-only version)

---

## 3. Screen Specifications

### 3.1 Onboarding + LINE Login

- **Screen: Welcome**
  - App name/logo
  - CTA: "Continue with LINE"
  - Privacy disclaimer (link)
- **Behavior:**
  - Opens external LINE login or in-app webview auth
  - After login, fetches user profile (display name, avatar)

---

### 3.2 Home Screen – Daily Mission Overview

- **Sections:**
  - Header with greeting ("Hi [Name], ready to study?")
  - Daily mission card
    - Today’s topics (auto-selected)
    - "Start Now" CTA
  - XP/Progress tracker (circular gauge)
  - Streak tracker (e.g., “3-day streak 🔥”)

- **Interaction:**
  - Tapping "Start Now" opens first lesson in mission queue
  - Pull to refresh for next mission

---

### 3.3 Lesson Screen (Text-Based)

- **Layout:**
  - Title ("Understanding Linkage Logic")
  - Section 1: Concept (plain text)
  - Section 2: Example with explanation
  - Section 3: Quiz question (1 MCQ)
  - CTA: "Submit"

- **Behavior:**
  - After submission, slide to feedback state
  - Scroll-to-progress indicators
  - Lessons are paginated in 1–2 screens max

---

### 3.4 Quiz + Feedback

- **Quiz Format:**
  - MCQ (radio style)
  - 4 choices, one correct
  - "Submit Answer" CTA

- **Feedback State:**
  - Highlight correct vs selected answer
  - Show Thai-language rationale: "Why this is correct"
  - CTA: “Next Question”

- **Adaptive Behavior:**
  - Correct: Next topic or harder question
  - Incorrect: Suggest retry or re-learn

---

### 3.5 Progress Tracking

- **Screen: Profile / Progress**
  - Circular XP tracker
  - Daily streak bar
  - Section-wise progress: e.g., Topic A – 60% mastered
  - “Review weak areas” CTA

- **Behavior:**
  - Updates after every completed mission
  - Syncs to local + backend for backup

---

### 3.6 LINE OA Trigger Points (Background)

- Trigger points:
  - Daily reminder if mission not started by 7PM
  - Encouragement if streak is broken
  - Motivational message on quiz mastery
- No UI for config in MVP (handled backend-side)

---

## 4. Admin / CMS (Web Only)

- Web-based dashboard
- Modules:
  - Lesson editor (markdown or WYSIWYG)
  - Quiz builder (MCQ with correct answer + explanation)
  - Tag-based topic taxonomy
  - Analytics panel (view completion, common errors)

---

## 5. Component Design Notes

| Component | Notes |
|----------|-------|
| Buttons | Use rounded primary buttons; disable on loading |
| Inputs | Radio group for MCQs; visually distinguish selected |
| Feedback | Color code: green = correct, red = wrong; Thai explanation in light card |
| Text | Thai fonts optimized for legibility; avoid small fonts below 14pt |
| Animations | Soft slide-in for transitions; no heavy animations in MVP |

---

## 6. Edge Case Handling

| Scenario | Behavior |
|----------|----------|
| No internet | Show offline banner + disable new quiz submission |
| Double submission | Disable CTA during async operation |
| Skipped questions | Prompt: “Are you sure you want to skip this mission?” |
| Repeat questions | Reorder from available pool unless user selects "Review Mode" |

---

## 7. Design Constraints

- Mobile-first only; screen ratio target = 16:9
- Thai as default language (no i18n in MVP)
- All fonts and spacing should work across Android and iOS
- Designed for Firebase/LINE login only
- Color palette: clean, academic (white, soft blue, green)

---

## 8. Deliverables

- Figma file with all screens (1x, 2x)
- Asset pack: logo, font, color tokens
- Component documentation (in progress.md or Figma notes)
- Developer-ready specs (margins, padding, font sizes)

---
