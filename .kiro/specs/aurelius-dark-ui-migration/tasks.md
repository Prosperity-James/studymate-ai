# Implementation Plan: Aurelius Dark UI Migration

## Overview

Complete greenfield visual replacement of all StudyMate AI templates and static assets to the Aurelius Dark design system. No backend routes are changed. Every legacy template is deleted and rebuilt from scratch.

## Tasks

- [x] 1. Rewrite product.css — Aurelius Dark foundation
  - Remove every CSS rule block referencing Bootstrap light-theme color values (`#fff`, `#f8f9fa`, `.bg-white`, `.text-dark`, `.navbar-light`) unless they are intentional Aurelius Dark overrides
  - Keep all existing `:root` custom property definitions intact
  - Add `.split-view` — CSS grid `1fr 1fr`, gap 24px, stacks to single column at `< 768px`
  - Add `.explainer-layout` — CSS grid `1fr 260px`, gap 24px, stacks at `< 900px`
  - Add `.quiz-layout` — CSS grid `1fr 240px`, gap 24px, stacks at `< 900px`
  - Add `.slides-presenter` — CSS grid `200px 1fr 240px`, gap 0, right panel collapses at `< 1024px`
  - Add `.tab-bar` and `.tab-btn` — filter tab strip; active tab with amber underline
  - Add `.persona-grid` — CSS grid `repeat(auto-fill, minmax(200px, 1fr))`, gap 16px
  - Add `.persona-card` — panel-card variant; amber border + glow when `.active`
  - Add `.hero-stats-strip` and `.stat-chip` — flex row of stat pills
  - Add `.how-it-works-grid` and `.step-card` — numbered step card layout
  - Add `.subscription-card` — panel-card with amber border and header accent
  - Add `.profile-hero` — flex row, gap 20px, avatar min 72px
  - Add `.card-hover-action` — absolute overlay on `.saved-note-card`, opacity 0 → 1 on parent hover
  - Add `.onboarding-page` — centered flex column, min-height 100vh, padding 40px 20px
  - Add `.slides-thumb-card` — thumbnail card for slides left panel; amber border when `.active`
  - Add `.viz-placeholder` — panel-card with dashed amber border, centered label
  - Ensure `.sidebar-toggle-btn` and `.sidebar-close-btn` are `display:none` at ≥ 1200px and `display:flex` at < 1200px
  - Add `.sidebar-open .dashboard-sidebar` rule for mobile overlay (transform translateX(0))
  - Add `.sidebar-open .sidebar-backdrop` rule (`display: block`)
  - Requirements: 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 2.1, 2.8, 2.9, 14.2, 14.4, 14.5

- [x] 2. Rebuild home.html — Landing Page (SCREEN_20)
  - Head: Inter from Google Fonts, product.css, Bootstrap 5 JS bundle only (no Bootstrap CSS), viewport meta, favicon; remove any Plus+Jakarta+Sans import
  - Body class `landing-body accent-amber`
  - Nav `nav.product-nav`: glassmorphism rgba(18,20,20,0.92) + backdrop-filter blur(14px), brand lockup left, nav links (Home, Courses, Teachers, Personalize) + Login and "Get Started" buttons on right; both buttons open `#authModal` with correct `data-auth-view`
  - Hero section: large headline, description, "Create Free Account" CTA (opens register modal) and "Open Dashboard" secondary button, `.hero-stats-strip` with 3 stat chips ("6+ AI tools", "3 explanation depths", "4 persona presets")
  - Feature grid section: 6 `.feature-card` cards (Summarizer, Explainer, Quiz, Slides, Audio, Saved Notes) each with title and description
  - How It Works section: 4 `.step-card` elements numbered 01–04
  - Persona section: 4 `.persona-card` elements with `data-persona` attributes and `#personaPreview` block below
  - Auth modal `#authModal`: login panel `#loginPanel` + register panel `#registerPanel`, tab buttons `#loginTabBtn` / `#registerTabBtn`, forms `#loginForm` / `#registerForm`, feedback divs `#loginFeedback` / `#registerFeedback`
  - Script: `/static/landing.js` only — no inline scripts or styles
  - Requirements: 1.1, 1.2, 1.3, 1.5, 1.7, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 14.1, 14.4, 14.6, 14.7

- [x] 3. Rebuild app_dashboard.html — Chat Dashboard (SCREEN_8)
  - Head: Inter, product.css, Bootstrap 5 JS, viewport meta; no inline styles or scripts
  - Body `dashboard-body accent-amber`, full `.dashboard-shell` grid
  - Sidebar: Dashboard link `class="active"`, all 8 nav links with correct hrefs and SVG icons, brand lockup, New Summary CTA button, user footer (`#profileAvatar`, `#profileName`)
  - Topbar: hamburger `[data-sidebar-open]`, title "StudyMate AI", `#authState`, profile gear link, `#logoutBtn`
  - Main `chat-main`: `#chatMessages` containing `.chat-welcome` (brand icon + "What would you like to study today?" h2 + description + `.chat-tool-pills` with Summarize/Explain/Quiz/Slides pills)
  - `#recentSessions` section below chat messages: heading "Recent Sessions", `#sessionsGrid` div with "No saved sessions yet." empty state
  - Chat composer: tool bar with tool pills + level switcher `#levelSwitcher`, composer with attach button `#attachBtn` + attach menu `#attachMenu` (4 items) + `#fileInput` hidden + `#noteText` textarea + send button `#sendBtn`, meta row with `#selectedFileName`, word count `#wordCount`, `#saveBtn`
  - Hidden elements: `#summaryResults`, `#explanationResults`, `#keywordResults`, `#noteTitle`
  - `#feedback` toast, `#spinner` overlay
  - Script: `/static/dashboard.js` only
  - Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 14.1, 14.3, 14.4

- [x] 4. Rebuild app_summarizer.html — Split View (SCREEN_5)
  - Standard shell: sidebar (Summarizer link active), topbar "Summarizer"
  - Main `dashboard-main` with `.split-view` grid container:
    - Left `.split-left.panel-card`: heading "Summary", `.chip-row#keywordResults`, `ul#summaryResults.result-list`, feedback action row (`#summaryLikeBtn`, `#summaryDislikeBtn`, `#copySummaryBtn`, `#regenerateSummaryBtn`, `#toggleSummaryEditorBtn`, `#submitSummaryFeedbackBtn`), `#summaryFeedbackPanel` hidden by default, `textarea#summaryCorrectionInput` hidden editor, `#summaryEditorWrap`
    - Right `.split-right.panel-card`: heading "Original Text", `textarea#noteText.study-textarea`, action row with upload trigger + `#summarizeBtn` + `#saveBtn`, `#fileInput` hidden, `#selectedFileName` pill, word/char count pills `#wordCount` `#charCount`
  - Stacks to single column at < 768px with right (input) panel on top
  - Standard hidden elements `#noteTitle`, `#feedback`, `#spinner`
  - Script: `/static/dashboard.js` only
  - Requirements: 2.1, 2.5, 2.7, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 14.1, 14.4

- [x] 5. Rebuild app_explainer.html — Explainer + Study Toolbox (SCREEN_16)
  - Standard shell: sidebar (Explainer link active), topbar "Explainer"
  - Main `dashboard-main` with `.explainer-layout` grid:
    - Left `.explainer-main`: `.viz-placeholder.panel-card` (dashed amber border, "AI Generated Visualization" label); `.panel-card` with heading "Key Principles", `.level-switcher` (buttons `#basicBtn` / `#intermediateBtn` / `#advancedBtn`, first active), `div#explanationResults.stack-list`, `div#keywordResults.chip-row`; input area with `textarea#noteText.study-textarea`, `#explainBtn` "Explain Concepts", `#saveBtn`, `#fileInput` hidden, `#selectedFileName`
    - Right `.explainer-toolbox.panel-card`: heading "Study Toolbox", `#copyExplanationBtn` "Copy", `#saveSessionToolboxBtn` "Save Session", `#listenBtn` "Listen"
  - `#explanationFeedbackPanel` hidden: like/dislike buttons `#explanationLikeBtn` `#explanationDislikeBtn`, `textarea#explanationCorrectionInput`, `#submitExplanationFeedbackBtn`
  - Standard hidden elements, `#feedback`, `#spinner`
  - Script: `/static/dashboard.js` only
  - Requirements: 2.1, 2.5, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 14.1, 14.4

- [x] 6. Rebuild app_quiz.html — Question Card + Stats Sidebar (SCREEN_4)
  - Standard shell: sidebar (Quiz link active), topbar "Quiz"
  - Main `dashboard-main` with `.quiz-layout` grid:
    - Left `.quiz-main`: `#inputCard.panel-card` (visible initially — heading "Generate a Quiz", `textarea#noteText.study-textarea`, `#generateQuizBtn`, `#fileInput` hidden, `#selectedFileName`); `#questionCard.panel-card` (hidden — `#questionNumber` label, `#questionText` h3, `#optionsList` with 4 option buttons each with `data-option` and `data-correct`, `#feedbackMsg`, `#nextBtn`, `#finishBtn`); `#completionCard.panel-card` (hidden — "Quiz Complete" heading, `#finalScore`, `#restartBtn`)
    - Right `.quiz-stats.panel-card`: heading "Session Stats", stat items for `#correctCount`, `#incorrectCount`, `#streakCount`
  - Standard hidden elements, `#feedback`, `#spinner`
  - Script: `/static/dashboard.js` only
  - Requirements: 2.1, 2.5, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 14.1, 14.4

- [x] 7. Rebuild app_slides.html — Three-Column Presenter View (SCREEN_17)
  - Standard shell: sidebar (Slides link active), topbar "Slides"
  - Main `dashboard-main`:
    - `#inputState.panel-card` (visible initially): heading "Generate Slides", `textarea#noteText.study-textarea`, `#generateSlidesBtn`, `#fileInput` hidden, `#selectedFileName`
    - `#presenterState.slides-presenter` (hidden initially): `.slides-thumb-list` left panel with heading "Slides" and `#slidesList` div; `.slides-canvas.panel-card` center with `#slideTitle` h2 and `#slidePoints` ul; `.slides-settings.panel-card` right with heading "Presentation Settings", `#slideStyleSelect`, `#exportBtn`, `#toggleSettingsBtn`
  - Standard hidden elements, `#feedback`, `#spinner`
  - Script: `/static/dashboard.js` only
  - Requirements: 2.1, 2.5, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 14.1, 14.4

- [x] 8. Rebuild app_audio.html — Audio Player (SCREEN_7)
  - Standard shell: sidebar (Audio link active), topbar "Audio"
  - Main `dashboard-main`:
    - `.panel-card` input + controls: heading "Listen to Notes", `textarea#audioText.study-textarea`, `#fileInput` hidden + upload trigger, `.audio-controls` row with `#playAudioBtn`, `#pauseAudioBtn`, `#stopAudioBtn`, `#audioStatus` div hidden initially (contains `.audio-bars` with 5 spans + "Playing..." label)
    - `.panel-card` settings: heading "Playback Settings", `.audio-settings` with speed range `#speedSlider` (min 0.5 max 2.0 step 0.1 default 1.0) + `#speedReadout` span, voice label + `select#voiceSelect`
  - Standard `#feedback`, `#spinner`
  - Script: `/static/dashboard.js` only
  - Requirements: 2.1, 2.5, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 14.1, 14.4

- [x] 9. Rebuild app_saved.html — Tabbed Library (SCREEN_6)
  - Standard shell: sidebar (Saved Notes link active), topbar "Saved Notes"
  - Main `dashboard-main`: page heading "Saved Sessions", `.tab-bar` with 5 `.tab-btn` buttons (data-filter: all [active], summary, quiz, slides, explanation), `#savedGrid.saved-grid` div, `#emptyState` div "No saved sessions yet."
  - Session card structure rendered by JS: article `.saved-note-card` with `data-type`, status badge, title h4, date, preview paragraph, `.card-hover-action` overlay with "View Session" anchor
  - Standard `#feedback`, `#spinner`
  - Script: `/static/dashboard.js` only
  - Requirements: 2.1, 2.5, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 14.1, 14.4

- [x] 10. Rebuild app_profile.html — Profile & Settings (SCREEN_18)
  - Standard shell: sidebar (Profile link active), topbar "Profile & Settings"
  - Main `dashboard-main`:
    - `.profile-hero`: `div.profile-avatar#profileAvatar` ≥72px with initial letter, div with `#profileName` h2 and `#profileEmail` muted text
    - `.panel-card` Personal Information: inputs `#editName` (Full Name) and `#editEmail` (Email), update button
    - `.subscription-card.panel-card`: amber border, "Premium" badge, description
    - `.panel-card` Learning Preferences: `select#personaSelect`, `select#summaryLengthSelect`, `select#explanationStyleSelect`
    - `.panel-card` Voice Selection: `select#voiceSelect`
    - `.action-row`: `#savePrefsBtn` "Save Preferences" + `#resetPrefsBtn` "Reset to defaults", `#prefsFeedback` confirmation div
  - Hidden: `#noteTitle`, `#feedback`, `#spinner`
  - Script: `/static/dashboard.js` only
  - Requirements: 2.1, 2.5, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 14.1, 14.4

- [x] 11. Rebuild landing.html — Onboarding Welcome (SCREEN_19)
  - Head: Inter, product.css, Bootstrap 5 JS, viewport meta
  - Body `landing-body accent-amber`
  - `nav.product-nav` (same structure as home.html)
  - `main.onboarding-page`: `.onboarding-card.panel-card` centered with brand badge icon, h1 "Your Academic Edge", description paragraph, "Get Started" primary button linking to `/personalize`, "Back to Home" ghost button linking to `/`
  - Script: `/static/landing.js` only
  - Requirements: 1.1, 1.3, 1.5, 4.1, 4.3, 4.4, 14.1

- [x] 12. Rebuild personalize.html — Personalize Page (SCREEN_14)
  - Head: Inter, product.css, Bootstrap 5 JS, viewport meta; NO Plus+Jakarta+Sans
  - Body `landing-body accent-amber`
  - `nav.product-nav`
  - `main.onboarding-page`: h1 "Choose your learning mode", description paragraph, `.persona-grid` with 4 `.persona-card` elements (data-persona: student [active by default], teacher, tutor, self-learner) each showing icon + name + short description, `#personaPreview.panel-card` below grid updated on card click, "Continue to StudyMate" primary button `#continueBtn` linking to `/app/dashboard`
  - No legacy color values, no Plus Jakarta Sans
  - Script: `/static/landing.js` only
  - Requirements: 1.1, 1.3, 1.5, 4.1, 4.2, 4.3, 4.4, 14.1

- [x] 13. Rebuild courses.html and teachers.html
  - Both files: head with Inter, product.css, Bootstrap 5 JS, viewport meta; body `landing-body accent-amber`; `nav.product-nav`; script `/static/landing.js` only
  - courses.html main: page hero with h1 "Courses" + description, `.feature-grid` of course panel-cards (title + description) in Aurelius Dark style; remove all Bootstrap light-theme override classes
  - teachers.html main: page hero with h1 "For Teachers" + description, teacher feature highlight cards; remove all Bootstrap light-theme override classes
  - No legacy color values in any inline style; no Plus Jakarta Sans; no additional custom CSS files
  - Requirements: 1.1, 1.3, 1.5, 4.5, 4.6, 14.1

- [x] 14. Rewrite dashboard.js — App page interactions
  - Preserve unchanged: `getToken`, `getUser`, `requestJson`, `showFeedback`, `setLoading`, sidebar toggle logic, auth state rendering (`updateAuthState`, `populateProfile`), file upload handler, summarizer fetch+render, explainer fetch+render, feedback panel (like/dislike/copy/regenerate/submit), save session
  - Add dashboard recent sessions: when `#sessionsGrid` exists on page load, call history API and render last 3 session cards in `#sessionsGrid`; show "No saved sessions yet." when empty
  - Add dashboard `#sendBtn`: dispatch to active tool pill (summarize/explain/quiz/slides); hide `.chat-welcome` after first submit
  - Add quiz engine: `#generateQuizBtn` → POST `/api/study/quiz` → store questions, show `#questionCard`, hide `#inputCard`; option button clicks → highlight, show correct/incorrect, update `#correctCount` `#incorrectCount` `#streakCount`; `#nextBtn` → advance question; all answered or `#finishBtn` → show `#completionCard` with `#finalScore`; `#restartBtn` → reset to input
  - Add slides presenter: `#generateSlidesBtn` → POST `/api/study/slides` → populate `#slidesList` thumbnails, show `#presenterState`, hide `#inputState`; thumbnail click → update `#slideTitle` + `#slidePoints`; `#toggleSettingsBtn` → toggle `.slides-settings` at < 1024px
  - Add saved notes tabs: `.tab-btn` click → active class + filter `#savedGrid` cards by `data-type`; load all sessions into `#savedGrid` on page load when it exists
  - Add profile: `#savePrefsBtn` → gather selects → POST `/api/study/preferences` → show `#prefsFeedback`; `#resetPrefsBtn` → restore defaults without API call; simultaneous save+reset prioritises reset
  - Add study toolbox: `#listenBtn` → `speakText(explanationResults.innerText)`; `#saveSessionToolboxBtn` → same as `#saveBtn`
  - Add audio `#audioStatus`: show when `speechSynthesis.speaking`, hide on stop; `#stopAudioBtn` → `cancel()` then hide status; populate `#voiceSelect` on `speechSynthesis.onvoiceschanged`; `#speedSlider` input → update `#speedReadout`
  - Level buttons `.level-btn`: click → update `currentLevel`, toggle active class
  - Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.4, 6.6, 7.1, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 11.1, 11.2, 11.5, 11.6, 12.1, 12.6, 12.7, 12.8

- [x] 15. Rewrite landing.js — Public page interactions
  - Preserve unchanged: `submitAuth`, `saveSession`, login form submit → POST `/api/auth/login` → store JWT → redirect to `/app/dashboard`, register form submit → POST `/api/auth/register` → redirect to `/app/dashboard`, `setAuthView` tab switching, scroll reveal stagger on DOMContentLoaded
  - Update persona card logic: `.persona-card` click → `setPersona(card.dataset.persona)` → update active class on all cards + update `#personaPreview` innerHTML with title + description from `personaContent` map
  - Update `continueBtn` on personalize page: save selected persona to localStorage before navigation
  - Ensure auth modal `show.bs.modal` event handler calls `setAuthView` with correct view from `data-auth-view`
  - Requirements: 3.6, 3.7, 3.8, 3.9, 3.10, 4.1, 4.2

- [ ] 16. Delete legacy templates and audit dead code
  - Delete `app/templates/dashboard.html`
  - Delete `app/templates/index.html`
  - Delete `app/templates/app_customize.html`
  - Verify `app/api/routes/pages.py` has no `FileResponse` calls pointing to deleted files; confirm `/app/customize` route uses `RedirectResponse` to `/app/profile`
  - Audit all 14 remaining templates: confirm no `<style>` inline blocks and no `<script>` inline blocks exist
  - Audit all app templates (app_*.html): confirm each imports only `product.css` and `dashboard.js`
  - Audit all public templates (home.html, landing.html, personalize.html, courses.html, teachers.html): confirm each imports only `product.css` and `landing.js`
  - Audit `product.css` and remove any CSS class definitions not referenced in any template
  - Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7

## Task Dependency Graph

```json
{
  "waves": [
    { "wave": 1, "tasks": ["1"] },
    { "wave": 2, "tasks": ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"] },
    { "wave": 3, "tasks": ["14", "15"] },
    { "wave": 4, "tasks": ["16"] }
  ],
  "dependencies": {
    "2":  ["1"],
    "3":  ["1"],
    "4":  ["1"],
    "5":  ["1"],
    "6":  ["1"],
    "7":  ["1"],
    "8":  ["1"],
    "9":  ["1"],
    "10": ["1"],
    "11": ["1"],
    "12": ["1"],
    "13": ["1"],
    "14": ["3", "4", "5", "6", "7", "8", "9", "10"],
    "15": ["2", "11", "12", "13"],
    "16": ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
  }
}
```

## Notes

- All tasks depend on Task 1 (product.css) being completed first since templates rely on the CSS classes it defines
- Tasks 2–13 (template rebuilds) can run in parallel after Task 1
- Task 14 (dashboard.js) depends on all app templates (3–10) being complete so JS element IDs are confirmed
- Task 15 (landing.js) depends on all public templates (2, 11–13) being complete
- Task 16 (cleanup) must run last after all templates and JS are confirmed working
- The backend (`pages.py`) requires no changes — all routes already point to the correct template filenames
