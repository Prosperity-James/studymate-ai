# Design Document: Aurelius Dark UI Migration

## Overview

This document describes the technical architecture and implementation plan for the complete Aurelius Dark UI migration of StudyMate AI. The migration is a greenfield visual replacement: every legacy template, stylesheet rule, and UI component is deleted and rebuilt to satisfy the Aurelius Dark design system. The backend routes and API contracts are unchanged.

---

## Architecture

### Technology Stack (unchanged)
- **Backend:** Python / FastAPI with Jinja2 HTML templates served via `FileResponse`
- **Routing:** `app/api/routes/pages.py` — no route changes required
- **Styling:** Single stylesheet `app/static/product.css` (Aurelius Dark CSS custom properties, no Tailwind CDN, no Bootstrap light-theme)
- **JavaScript:** Two files only — `app/static/dashboard.js` (authenticated pages) and `app/static/landing.js` (public pages)
- **Fonts:** Inter from Google Fonts only — `Plus Jakarta Sans` removed everywhere

### File Inventory

| File | Role | Action |
|---|---|---|
| `app/templates/home.html` | Public landing page (`/`) | **Rebuild** — Aurelius Dark SCREEN_20 |
| `app/templates/landing.html` | Onboarding welcome | **Rebuild** — Aurelius Dark SCREEN_19 |
| `app/templates/personalize.html` | Onboarding personalize | **Rebuild** — Aurelius Dark SCREEN_14 |
| `app/templates/courses.html` | Public courses page | **Rebuild** — Aurelius Dark foundation |
| `app/templates/teachers.html` | Public teachers page | **Rebuild** — Aurelius Dark foundation |
| `app/templates/dashboard.html` | Legacy dashboard | **Delete** — not referenced by any active route |
| `app/templates/index.html` | Legacy index | **Delete** — not referenced by any active route |
| `app/templates/app_dashboard.html` | App dashboard (SCREEN_8) | **Rebuild** — add Recent Sessions, keep chat shell |
| `app/templates/app_summarizer.html` | Summarizer (SCREEN_5) | **Rebuild** — split-panel layout |
| `app/templates/app_explainer.html` | Explainer (SCREEN_16) | **Rebuild** — visualization card + study toolbox |
| `app/templates/app_quiz.html` | Quiz (SCREEN_4) | **Rebuild** — question card + stats sidebar |
| `app/templates/app_slides.html` | Slides (SCREEN_17) | **Rebuild** — three-column presenter view |
| `app/templates/app_audio.html` | Audio (SCREEN_7) | **Rebuild** — playback controls + voice selector |
| `app/templates/app_saved.html` | Saved Notes (SCREEN_6) | **Rebuild** — tabbed filter + hover-reveal grid |
| `app/templates/app_profile.html` | Profile (SCREEN_18) | **Rebuild** — avatar header + subscription card |
| `app/templates/app_customize.html` | Legacy customize | **Delete** — route redirects to `/app/profile` |
| `app/static/product.css` | Global stylesheet | **Rewrite** — remove legacy/unused rules, keep Aurelius Dark vars |
| `app/static/dashboard.js` | App JS | **Rewrite** — wire new page layouts and interactions |
| `app/static/landing.js` | Public JS | **Rewrite** — wire new landing page interactions |

---

## Design System Constants

All pages import `product.css` which defines:

```css
:root {
  --surface:               #121414;
  --surface-container-low: #1a1c1c;
  --surface-container:     #1e2020;
  --surface-container-high:#292a2a;
  --surface-bright:        #38393a;
  --primary:               #f59e0b;
  --primary-hover:         #d97706;
  --primary-muted:         rgba(245,158,11,0.12);
  --primary-border:        rgba(245,158,11,0.30);
  --on-surface:            #e3e2e2;
  --on-surface-muted:      #9ca3af;
  --radius-md:             8px;
  --radius-lg:             12px;
  --sidebar-w:             260px;
  --topbar-h:              60px;
}
```

---

## Component Architecture

### 1. Shared Sidebar (all `app_*.html` pages)

Every authenticated page contains the identical sidebar HTML block. The active nav link is set per-page by adding `class="active"` to the matching `<a>` element.

**Structure:**
```
.dashboard-shell (CSS grid: sidebar | topbar / main)
  .sidebar-backdrop (mobile overlay close)
  aside.dashboard-sidebar
    .sidebar-header → brand lockup + close btn
    .sidebar-new-summary → "New Summary" CTA
    nav.sidebar-nav → 8 links (Dashboard…Profile)
    .sidebar-user → avatar + name + role
  header.app-topbar → hamburger + title | authState + profile + logout
  main (page-specific content)
```

**Responsive behaviour:**
- ≥ 1200px: sidebar always visible; `.sidebar-toggle-btn` hidden
- < 1200px: sidebar hidden by default; hamburger toggles `.sidebar-open` class on `.dashboard-shell`; `.sidebar-backdrop` shown as overlay

### 2. Public Nav (all public pages)

```
nav.product-nav (glassmorphism: rgba(18,20,20,0.92) + blur)
  .container
    a.brand-lockup (left)
    .nav-actions (right) → Home | Courses | Teachers | Personalize | Login | Get Started
```

---

## Page Layouts

### Landing Page — `home.html` (SCREEN_20)

```
body.landing-body
  nav.product-nav
  main
    section.hero → headline + description + CTA pair + stats strip
    section.feature-grid → 6 feature cards
    section.how-it-works → 4 numbered step cards (01–04)
    section.persona-section → 4 clickable persona cards + preview block
  footer (minimal: brand + copyright)
  #authModal (login/register tabs)
script: landing.js
```

### Onboarding — `landing.html` (Welcome / SCREEN_19)

```
body.landing-body
  nav.product-nav
  main.onboarding-page
    .onboarding-card → hero icon + "Academic Edge" headline + description + CTA
script: landing.js
```

### Personalize — `personalize.html` (SCREEN_14)

```
body.landing-body
  nav.product-nav
  main.onboarding-page
    h1 "Choose your learning mode"
    .persona-grid (4 cards: Student, Teacher, Tutor, Self-Learner)
    .persona-preview-block (updated on card click)
    a.btn-primary "Continue to StudyMate"
script: landing.js
```

### Dashboard — `app_dashboard.html` (SCREEN_8)

```
.dashboard-shell
  [sidebar — Dashboard active]
  [topbar]
  main.chat-main
    .chat-messages#chatMessages
      .chat-welcome → icon + "What would you like to study today?" + tool pills
      #recentSessions → last 3 session cards (loaded by JS)
    .chat-composer-wrap
      .chat-tool-bar → tool pills + level switcher
      .chat-composer → attach btn + textarea + send btn
      .chat-composer-meta → file name + word count + save btn
```

### Summarizer — `app_summarizer.html` (SCREEN_5)

```
.dashboard-shell
  [sidebar — Summarizer active]
  [topbar — "Summarizer"]
  main.dashboard-main
    .split-view (CSS grid: 1fr 1fr; stacks < 768px)
      .split-left.panel-card
        .panel-head → "Summary" heading + action buttons
        .chip-row#keywordResults → key themes
        ul#summaryResults.result-list → generated bullets
      .split-right.panel-card
        .panel-head → "Original Text"
        textarea#noteText.study-textarea
        .action-row → upload btn + summarize btn + save btn
```

### Explainer — `app_explainer.html` (SCREEN_16)

```
.dashboard-shell
  [sidebar — Explainer active]
  [topbar — "Explainer"]
  main.dashboard-main
    .explainer-layout (CSS grid: 1fr 260px; stacks < 900px)
      .explainer-main
        .panel-card.viz-placeholder → "AI Generated Visualization" card
        .panel-card
          .panel-head → "Key Principles" + level buttons
          div#explanationResults.stack-list
      .explainer-toolbox.panel-card
        h3 "Study Toolbox"
        btn Copy | btn Save Session | btn Listen
```

### Quiz — `app_quiz.html` (SCREEN_4)

```
.dashboard-shell
  [sidebar — Quiz active]
  [topbar — "Quiz"]
  main.dashboard-main
    .quiz-layout (CSS grid: 1fr 240px; stacks < 900px)
      .quiz-main
        .panel-card#inputCard → textarea + generate btn (shown when no quiz)
        .panel-card#questionCard (hidden until quiz generated)
          #questionText
          #optionsList → 4 option buttons (A–D)
          .action-row → Next / Finish btns
      .quiz-stats.panel-card
        .stat-item → ✓ Correct: #correctCount
        .stat-item → ✗ Incorrect: #incorrectCount
        .stat-item → 🔥 Streak: #streakCount
      #completionCard.panel-card (hidden) → score summary
```

### Slides — `app_slides.html` (SCREEN_17)

```
.dashboard-shell
  [sidebar — Slides active]
  [topbar — "Slides"]
  main.dashboard-main
    #inputState (shown when no slides) → textarea + generate btn
    #presenterState.slides-presenter (hidden until generated; grid: 200px 1fr 240px)
      .slides-thumb-list#slidesList → numbered thumbnail cards
      .slides-canvas.panel-card#activeSlide → slide title + bullets
      .slides-settings.panel-card
        h3 "Presentation Settings"
        select#slideStyleSelect
        btn Export
        btn Toggle (shown < 1024px)
```

### Audio — `app_audio.html` (SCREEN_7)

```
.dashboard-shell
  [sidebar — Audio active]
  [topbar — "Audio"]
  main.dashboard-main
    .panel-card
      textarea#audioText.study-textarea
      .audio-controls → Play | Pause | Stop
      #audioStatus (hidden unless playing)
    .panel-card
      .audio-settings
        label Speed: input[type=range]#speedSlider + #speedReadout
        label Voice: select#voiceSelect
```

### Saved Notes — `app_saved.html` (SCREEN_6)

```
.dashboard-shell
  [sidebar — Saved Notes active]
  [topbar — "Saved Notes"]
  main.dashboard-main
    .tab-bar → All | Summaries | Quizzes | Slides | Explanations
    .saved-grid#savedGrid → Session_Card items (populated by JS)
    #emptyState (shown when no sessions)
```

Session_Card structure:
```html
<article class="saved-note-card" data-type="summary">
  <span class="status-badge">Summary</span>
  <h4>Note Title</h4>
  <p class="small-feedback">Date</p>
  <p class="panel-copy">Preview text...</p>
  <div class="card-hover-action">
    <a class="btn btn-primary" href="/app/summarizer">View Session</a>
  </div>
</article>
```

### Profile — `app_profile.html` (SCREEN_18)

```
.dashboard-shell
  [sidebar — Profile active]
  [topbar — "Profile"]
  main.dashboard-main
    .profile-hero → avatar (≥72px) + name + email
    .panel-card → Personal Information form (name, email)
    .panel-card.subscription-card → "Premium" amber-bordered card
    .panel-card → Learning Preferences (persona, summary length, explanation style)
    .panel-card → Voice Selection dropdown
    .action-row → Save Preferences btn + Reset to defaults btn
```

### Courses — `courses.html`

```
body.landing-body
  nav.product-nav
  main.container
    h1 "Courses"
    .courses-grid → course cards (Aurelius Dark styled)
script: landing.js
```

### Teachers — `teachers.html`

```
body.landing-body
  nav.product-nav
  main.container
    h1 "For Teachers"
    teacher feature cards (Aurelius Dark styled)
script: landing.js
```

---

## JavaScript Architecture

### `dashboard.js` — responsibilities per page

| Feature | Elements wired |
|---|---|
| Sidebar toggle | `[data-sidebar-open]`, `[data-sidebar-close]`, `.sidebar-backdrop` |
| Auth state | `#profileAvatar`, `#profileName`, `#authState`, `#logoutBtn` |
| Dashboard | `#sendBtn`, tool pills, `#recentSessions` load, `#saveBtn` |
| Summarizer | `#summarizeBtn`, file upload, feedback panel, copy, regenerate |
| Explainer | `#explainBtn`, level buttons, study toolbox (copy, save, TTS) |
| Quiz | `#generateQuizBtn`, option selection, next/finish, stats counters |
| Slides | `#generateSlidesBtn`, thumbnail click → canvas, settings panel toggle |
| Audio | `#playAudioBtn`, `#pauseAudioBtn`, `#stopAudioBtn`, speed slider, voice dropdown, audio status indicator |
| Saved Notes | tab filter buttons, `#savedGrid` load, "View Session" navigation |
| Profile | `#savePrefsBtn` → POST `/api/study/preferences`, `#resetPrefsBtn` → restore defaults |

### `landing.js` — responsibilities

| Feature | Elements wired |
|---|---|
| Auth modal | `#authModal`, `#loginTabBtn`, `#registerTabBtn` |
| Login form | `#loginForm` → POST `/api/auth/login` → store JWT → redirect |
| Register form | `#registerForm` → POST `/api/auth/register` → redirect |
| Persona cards | `.persona-card` click → highlight + update `#personaPreview` |
| Scroll reveal | `.reveal-up` stagger on DOMContentLoaded |

---

## CSS Architecture

`product.css` is reorganised into clear sections. Legacy classes that reference Bootstrap light-theme colors (`#fff`, `#f8f9fa`, `.bg-white`, `.text-dark`, `.navbar-light`) are removed. New sections added:

- `.split-view` — two-column grid for Summarizer
- `.explainer-layout` — main + toolbox sidebar
- `.quiz-layout` — question area + stats sidebar
- `.slides-presenter` — three-column presenter
- `.tab-bar` — filter tab strip for Saved Notes
- `.persona-grid` — 4-card onboarding grid
- `.hero-stats-strip` — stat chips below hero CTAs
- `.how-it-works` — numbered step cards
- `.subscription-card` — amber-accented Premium card
- `.profile-hero` — large avatar header section
- `.card-hover-action` — overlay "View Session" on hover

Responsive breakpoints:
- `< 1200px`: sidebar collapses to overlay
- `< 1024px`: slides right panel collapses
- `< 900px`: explainer and quiz sidebars stack
- `< 768px`: summarizer split view stacks; dashboard shell single column

---

## Data Flow (unchanged from current backend)

```
Browser ──GET──► FastAPI pages.py ──FileResponse──► HTML template
                                                       │
                                                  loads product.css
                                                  loads dashboard.js / landing.js
                                                       │
                                            JS reads localStorage (token, user)
                                                       │
                                            JS ──POST/GET──► FastAPI API routes
                                                              /api/auth/*
                                                              /api/study/*
```

No backend changes are required for this migration.

---

## Deletion List

Files to delete after migration:
1. `app/templates/dashboard.html` — legacy, no active route
2. `app/templates/index.html` — legacy, no active route
3. `app/templates/app_customize.html` — route already redirects to `/app/profile`

---

## Implementation Order

1. **`product.css`** — update first so all subsequent templates render correctly
2. **`home.html`** — landing page (most visible, tests auth flow)
3. **`app_dashboard.html`** — primary authenticated entry point
4. **`app_summarizer.html`** — split view layout
5. **`app_explainer.html`** — explainer + toolbox
6. **`app_quiz.html`** — quiz card + stats
7. **`app_slides.html`** — three-column presenter
8. **`app_audio.html`** — audio controls
9. **`app_saved.html`** — tabbed library
10. **`app_profile.html`** — profile + preferences
11. **`landing.html`**, **`personalize.html`**, **`courses.html`**, **`teachers.html`** — remaining public pages
12. **`dashboard.js`** — full rewrite wiring all new layouts
13. **`landing.js`** — update for new landing page elements
14. Delete legacy files
