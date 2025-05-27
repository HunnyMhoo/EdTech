# MVP Scope: Thai Self-Learning App (No Tutors, No Video)

## MVP Goal
Validate that Thai high school students can learn core exam content effectively via text-based micro-lessons and adaptive practice — without live tutors or videos.

---

## Core Feature Scope

### 1. Subject Focus
- GAT เชื่อมโยง only (logical reading, low media dependency, high demand)
- Approximately 5–7 core concepts
- 50–100 total questions
- Manual + AI-assisted lesson generation

### 2. Core Features (Student App)

| Feature | Description |
|--------|-------------|
| Daily Mission | 5 auto-selected questions from GAT เชื่อมโยง bank |
| Text-based Lessons | Scrollable cards: concept → example → 1–2 quiz questions |
| Instant Feedback | Thai-language rationale shown for each wrong answer |
| Adaptive Flow | System picks easier/harder questions based on performance |
| LINE OA Integration | Daily quiz links, streak reminders |
| Progress Tracker | Percent mastery per topic, basic XP/streak dashboard |

### 3. Admin + CMS

| Module | Description |
|--------|-------------|
| Content Builder | Create/edit lessons, quizzes, distractors |
| AI Assist (Optional) | GPT prompt templates to auto-generate explanations |
| Analytics | Track question difficulty, error rates, session time |

### 4. Platform & Stack

| Layer | Tech |
|-------|------|
| Frontend | React Native or Flutter (mobile-only) |
| Backend | Node.js or Python (FastAPI), MongoDB |
| AI Integration | OpenAI API or fine-tuned Thai LLM for explanation generation |
| Messaging | LINE OA with webhook triggers |
| Hosting | Firebase / Vercel / AWS (based on speed and team size) |

---

## Success Criteria (MVP Validation)

| Metric | Target |
|--------|--------|
| Mission Completion Rate | 60%+ users complete 1 full mission per session |
| Concept Mastery | 40%+ improvement in post-quiz scores after 5 missions |
| Retention | 30%+ return on Day 3 |
| Feedback Score | 80%+ say “Easy to understand without tutor” |
| Waitlist Signups | More than 1,000 users during MVP promo phase |

---

## MVP Timeline (6–8 Weeks)

| Week | Milestone |
|------|-----------|
| Week 1 | Finalize subject and curriculum outline |
| Week 2 | Build CMS and lesson authoring tool |
| Week 3 | Build MVP mobile UI (lesson, quiz, feedback) |
| Week 4 | Integrate adaptive engine and LINE OA |
| Week 5 | QA and user test with 10–20 students |
| Week 6–7 | Launch MVP pilot (closed beta) |
| Week 8 | Collect analytics and iterate core features |

---

## Out-of-Scope (for MVP)

- No video content
- No multiple subjects
- No full login/auth system (LINE-based identity only)
- No payment system (MVP is free)
