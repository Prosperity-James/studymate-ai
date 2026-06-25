# Requirements Document

## Introduction

StudyMate AI currently has a split personality in its UI: the app-shell pages (`app_*.html`) are already styled with the Aurelius Dark design system (deep charcoal `#121414`, amber `#f59e0b`, Inter font, Tailwind-compatible custom properties in `product.css`), while the public-facing pages (`home.html`, `landing.html`, `personalize.html`, `courses.html`, `teachers.html`, `dashboard.html`, `index.html`) use a legacy mix of Plus Jakarta Sans, Bootstrap-only layout, and old color conventions that do not match the design system.

Additionally, several app pages lack the richer layouts specified in the Aurelius Dark design spec (SCREEN references): the Dashboard needs four quick-action tiles; the Summarizer needs a split-panel view; the Quiz page needs a question card + stats sidebar; the Slides page needs a three-column presenter view; the Saved Notes page needs tabbed filtering with hover-reveal actions; and the Profile page needs a large avatar header, subscription card, and voice preference control.

This migration replaces every legacy template with fully Aurelius Dark–compliant pages, upgrades the app pages to their specified layouts, consolidates the static assets, and removes all dead code — delivering a single, visually consistent premium experience across the entire product.

## Glossary

- **Aurelius_Dark_System**: The design system defined by surface color `#121414`, primary accent `#f59e0b`, Inter font, 8px base radius, and the CSS custom properties already present in `product.css`.
- **Dashboard_Shell**: The two-column grid layout (`dashboard-shell` CSS class) comprising the 260px sticky sidebar and the main content area used by all authenticated app pages.
- **Sidebar**: The vertical navigation component (260px wide, sticky) containing the brand lockup, "New Summary" CTA, nav links, and user identity footer.
- **App_Page**: Any Jinja2/HTML template served under the `/app/*` route prefix, requiring authentication.
- **Public_Page**: Any HTML template served without authentication: the landing/home page, onboarding flow pages, `courses.html`, `teachers.html`, and `personalize.html`.
- **Landing_Page**: The marketing entry point at `/` (currently `home.html`).
- **Onboarding_Flow**: The sequence of pages a new user sees before entering the app: Welcome (`landing.html`), Personalize (`personalize.html`), and the Ready screen.
- **product.css**: The single Aurelius Dark stylesheet at `app/static/product.css` that all pages must import.
- **dashboard.js**: The single JavaScript file at `app/static/dashboard.js` that drives all authenticated app page interactions.
- **landing.js**: The JavaScript file at `app/static/landing.js` that drives public page interactions (auth modal, persona preview, scroll animations).
- **Session_Card**: A card in the Saved Notes library representing one saved study session, showing title, type badge, date, and a hover-reveal "View Session" action.
- **Quick_Action_Tile**: One of four dashboard tiles that link directly to Summarizer, Explainer, Quiz, and Slides.
- **Split_View**: A two-column layout where the left panel contains controls/output and the right panel contains the original source text.
- **Presentation_View**: The three-column Slides page layout: slide thumbnail list (left), active slide canvas (center), settings panel (right).

---

## Requirements

### Requirement 1: Unified Aurelius Dark Visual Foundation

**User Story:** As a user navigating any part of StudyMate AI, I want every page to look and feel like the same product, so that I do not experience jarring visual inconsistencies between public and authenticated pages.

#### Acceptance Criteria

1. THE UI_System SHALL apply `background: #121414` as the page background color on every HTML template in the project.
2. THE UI_System SHALL apply `color: #FFFFFF` as the primary text color and `color: #9ca3af` as the secondary/muted text color on every page.
3. THE UI_System SHALL use `font-family: 'Inter', sans-serif` as the sole body typeface on every page, loaded from Google Fonts.
4. THE UI_System SHALL use `border-radius: 8px` (or the `--radius-md` CSS variable) as the default component border radius across all cards, inputs, and buttons.
5. WHEN any legacy font import (`Plus+Jakarta+Sans`) exists in a template, THE Migration SHALL remove that import and replace it with the Inter import.
6. WHEN any legacy color value outside the Aurelius Dark palette appears in an HTML `style` attribute or inline CSS, THE Migration SHALL replace it with the corresponding Aurelius Dark CSS custom property.
7. THE UI_System SHALL apply `max-width: 1440px` and `margin: 0 auto` to all full-width page containers on desktop viewports.

---

### Requirement 2: Aurelius Dark Side Navigation Bar

**User Story:** As an authenticated user, I want a consistent sidebar navigation on every app page, so that I can move between tools without losing my place.

#### Acceptance Criteria

1. THE Sidebar SHALL be 260px wide when it exists in the DOM, sticky to the top-left of the viewport, and visible at all times on desktop viewports (width ≥ 1200px); on smaller viewports the sidebar SHALL be hidden by default and accessible via a toggle.
2. THE Sidebar SHALL display the "StudyMate AI" brand name in Amber Gold (`#f59e0b`) with "Premium Learner" subtext beneath it.
3. THE Sidebar SHALL render a "New Summary" CTA button with background color `#f59e0b` and black foreground text spanning the full sidebar width (minus padding).
4. THE Sidebar SHALL contain navigation links for Dashboard, Summarizer, Explainer, Audio, Quiz, Slides, Saved Notes, and Profile, in that order.
5. WHEN a navigation link corresponds to the currently active page, THE Sidebar SHALL apply a 4px left border in `#f59e0b`, a `rgba(245,158,11,0.12)` background tint, and amber text color to that link.
6. WHEN a navigation link does not correspond to the active page, THE Sidebar SHALL display it with `color: #9ca3af` and no left border accent.
7. THE Sidebar SHALL render the authenticated user's initial letter avatar, display name, and "Premium Learner" role label in a footer strip at the bottom.
8. WHEN the viewport width is less than 1200px, THE Sidebar SHALL be hidden by default and THE Topbar SHALL render a hamburger toggle button that opens the sidebar as an overlay.
9. WHEN the sidebar is open as an overlay on mobile, THE Sidebar SHALL display a close button (`×`) and a semi-transparent backdrop behind it.

---

### Requirement 3: Public Landing Page (SCREEN_20)

**User Story:** As a visitor landing on StudyMate AI for the first time, I want a polished dark-themed marketing page, so that I immediately understand the product's value and am motivated to sign up.

#### Acceptance Criteria

1. THE Landing_Page SHALL render a navigation bar using `background: rgba(18,20,20,0.92)` with `backdrop-filter: blur(14px)`, containing the brand lockup on the left and Login / Get Started buttons on the right.
2. THE Landing_Page SHALL render a hero section containing a headline, a short description paragraph, a "Create Free Account" primary CTA button, and an "Open Dashboard" secondary button.
3. THE Landing_Page SHALL render a statistics strip below the hero CTAs showing at minimum three stat chips (e.g., "6+ AI tools", "3 explanation depths", "4 persona presets"); WHEN no stat data is available, THE Landing_Page SHALL still render the strip section, displaying it as an empty container.
4. THE Landing_Page SHALL render a feature grid section with at least six feature cards, each displaying a title and description.
5. THE Landing_Page SHALL render a "How It Works" section with numbered step cards (01–04) explaining the workflow.
6. THE Landing_Page SHALL render a persona selection section with four clickable cards: Student, Teacher, Tutor, Self-Learner.
7. WHEN a persona card is clicked, THE Landing_Page SHALL highlight the selected card with an amber border and display a preview description block below the grid.
8. THE Landing_Page SHALL render an authentication modal (login + register tabs) triggered by the nav Login and Get Started buttons.
9. WHEN the authentication modal register form is submitted with valid data, THE Landing_Page SHALL send a POST request to `/api/auth/register` and redirect the user to `/app/dashboard` on success.
10. WHEN the authentication modal login form is submitted with valid credentials, THE Landing_Page SHALL send a POST request to `/api/auth/login`, store the JWT token in `localStorage`, and redirect the user to `/app/dashboard`.

---

### Requirement 4: Onboarding Flow Pages

**User Story:** As a new user completing registration, I want a structured onboarding sequence, so that the app is personalized to my learning role before I reach the dashboard.

#### Acceptance Criteria

1. THE Personalize_Page (at `/personalize`) SHALL render a full-page Aurelius Dark layout with a 4-card grid for selecting Academic Level / persona: Student, Teacher, Tutor, Self-Learner.
2. WHEN a persona card on the Personalize_Page is selected, THE Personalize_Page SHALL visually highlight the selected card with an amber border and update the preview description.
3. THE Personalize_Page SHALL NOT use the Plus Jakarta Sans font or any legacy color values from the old design.
4. THE Personalize_Page SHALL share the same navigation bar structure as the Landing_Page (top nav with brand lockup and auth buttons).
5. THE Courses_Page (at `/courses`) and THE Teachers_Page (at `/teachers`) SHALL be migrated to use the Aurelius Dark foundation (Inter font, `#121414` background, amber accents) and SHALL NOT retain any legacy color palette, typography, or spacing patterns.
6. IF the `courses.html` or `teachers.html` template contains any Bootstrap light-theme override classes inconsistent with Aurelius Dark, THE Migration SHALL remove those classes.

---

### Requirement 5: Dashboard Page — Chat Interface (SCREEN_8)

**User Story:** As an authenticated user arriving at the dashboard, I want a centered search/chat area with quick-action tools, so that I can immediately start a new study session.

#### Acceptance Criteria

1. THE App_Dashboard SHALL render the "What would you like to study today?" heading centered in the main content area when no conversation has started, and SHALL hide the heading once the user submits their first message.
2. THE App_Dashboard SHALL render four quick-action tool pills (Summarize, Explain, Quiz, Slides) below the welcome heading.
3. THE App_Dashboard SHALL render the chat composer bar (textarea + attach button + send button) fixed to the bottom of the main content area.
4. WHEN a tool pill is selected, THE App_Dashboard SHALL highlight it with amber background tint and border, and update the active tool state.
5. THE App_Dashboard SHALL render a "Recent Sessions" section below the chat messages area, displaying the last three saved study sessions as cards.
6. WHEN no sessions exist, THE App_Dashboard SHALL display an empty-state message: "No saved sessions yet."
7. THE App_Dashboard SHALL render the full Sidebar with the Dashboard link in active state.

---

### Requirement 6: Summarizer Page — Split View (SCREEN_5)

**User Story:** As a user summarizing a document, I want a split-panel view showing my summary controls on the left and the original text on the right, so that I can reference the source while reviewing the output.

#### Acceptance Criteria

1. THE Summarizer_Page SHALL render a two-column split layout at desktop widths: a left panel for summary controls and output, and a right panel for the original text input.
2. THE Summarizer_Page left panel SHALL contain: a "Summarize" action button, a Key Themes chip list, and the generated summary bullet list.
3. THE Summarizer_Page right panel SHALL be labeled "Original Text" and SHALL contain a scrollable textarea for pasting source content.
4. WHEN the Summarizer_Page viewport is narrower than 768px, THE Summarizer_Page SHALL stack the two panels vertically with the input panel on top.
5. THE Summarizer_Page SHALL render the full Sidebar with the Summarizer link in active state.
6. WHEN a summary is generated, THE Summarizer_Page SHALL render the bullet points into the left panel result area with a fade-in animation.

---

### Requirement 7: Explainer Page (SCREEN_16)

**User Story:** As a user explaining a concept, I want a clear layout with the explanation output, key principles, and a study toolbox, so that I can understand and act on the generated content efficiently.

#### Acceptance Criteria

1. THE Explainer_Page SHALL render an "AI Generated Visualization" placeholder card at the top of the main content area.
2. THE Explainer_Page SHALL render a "Key Principles" section displaying the generated explanation as a numbered or bulleted list.
3. THE Explainer_Page SHALL render a "Study Toolbox" sidebar panel containing quick-action buttons: Copy, Save Session, and Listen (TTS).
4. THE Explainer_Page SHALL render level-selection buttons (Basic, Intermediate, Advanced) and SHALL highlight the active level with amber styling.
5. WHEN the user calls `/api/study/explain` via the "Explain Concepts" action, THE Explainer_Page SHALL wait for the API response to complete before rendering the results into the Key Principles section.
6. THE Explainer_Page SHALL render the full Sidebar with the Explainer link in active state.

---

### Requirement 8: Quiz Page — Question Card with Stats Sidebar (SCREEN_4)

**User Story:** As a user taking a quiz, I want a centered question card with multiple-choice options and a session stats sidebar, so that I can focus on the question and track my performance.

#### Acceptance Criteria

1. THE Quiz_Page SHALL render the current question in a centered card occupying the main content area.
2. THE Quiz_Page question card SHALL display four answer options (A, B, C, D) as selectable buttons.
3. WHEN an answer option is selected, THE Quiz_Page SHALL highlight the selected option and reveal whether it is correct or incorrect.
4. THE Quiz_Page SHALL render a right-side stats panel showing: Correct count, Incorrect count, and Current Streak.
5. WHEN all questions have been answered, THE Quiz_Page SHALL display a completion summary with the final score, reflecting at minimum the number of correctly answered questions so that partial credit is always shown accurately.
6. THE Quiz_Page SHALL render the full Sidebar with the Quiz link in active state.

---

### Requirement 9: Slides Page — Three-Column Presenter View (SCREEN_17)

**User Story:** As a user reviewing generated slides, I want a three-column layout with a slide thumbnail list, an active slide canvas, and a settings panel, so that I can navigate and configure the presentation efficiently.

#### Acceptance Criteria

1. THE Slides_Page SHALL render a three-column layout (slide thumbnail list left, active slide canvas center, Presentation Settings right) WHEN slides have been generated; WHEN no slides exist yet, THE Slides_Page SHALL render a single-column input state prompting the user to generate slides.
2. THE Slides_Page left panel SHALL list all generated slides as numbered thumbnail cards.
3. WHEN a slide thumbnail is clicked, THE Slides_Page SHALL display that slide's content in the center canvas.
4. THE Slides_Page right panel SHALL contain presentation setting controls including slide style and export options.
5. THE Slides_Page SHALL render the full Sidebar with the Slides link in active state.
6. WHEN the viewport is narrower than 1024px, THE Slides_Page SHALL collapse the right settings panel and provide a toggle to show/hide it.

---

### Requirement 10: Audio Page (SCREEN_7)

**User Story:** As a user listening to my notes, I want a dedicated audio playback page with voice and speed controls, so that I can customize my listening experience.

#### Acceptance Criteria

1. THE Audio_Page SHALL render a text input area for pasting notes or uploading a file as the audio source.
2. THE Audio_Page SHALL render playback controls: Play, Pause, and Stop buttons.
3. THE Audio_Page SHALL render a speed slider ranging from 0.5× to 2.0× with a labeled readout.
4. THE Audio_Page SHALL render a voice selection dropdown populated with the available browser SpeechSynthesis voices.
5. WHEN audio is playing, THE Audio_Page SHALL display an animated audio bars indicator and a "Playing..." status label; WHEN playback stops or has not started, THE Audio_Page SHALL hide both the audio bars and the status label.
6. WHEN the Stop button is pressed, THE Audio_Page SHALL cancel the active SpeechSynthesis utterance and, only after the cancellation completes, SHALL hide the playing indicator and status label.
7. THE Audio_Page SHALL render the full Sidebar with the Audio link in active state.

---

### Requirement 11: Saved Notes Library — Tabbed Filtering (SCREEN_6)

**User Story:** As a user browsing my saved sessions, I want to filter by content type and see hover-reveal actions on each card, so that I can quickly find and reopen what I need.

#### Acceptance Criteria

1. THE Saved_Page SHALL render a tab bar with filter tabs: All, Summaries, Quizzes, Slides, Explanations.
2. WHEN a filter tab is selected, THE Saved_Page SHALL display only session cards matching that content type.
3. THE Saved_Page SHALL render saved sessions as a responsive grid of Session_Card components.
4. EACH Session_Card SHALL display: session title, content type badge, creation date, and a short preview of the content.
5. WHEN the pointer hovers over a Session_Card, THE Saved_Page SHALL reveal a "View Session" button overlaid on the card.
6. WHEN the "View Session" button is clicked, THE Saved_Page SHALL navigate the user to the relevant tool page with the session content preloaded.
7. THE Saved_Page SHALL render the full Sidebar with the Saved Notes link in active state.

---

### Requirement 12: Profile & Settings Page (SCREEN_18)

**User Story:** As an authenticated user managing my account, I want a polished profile page with a large avatar header, personal info section, subscription card, and learning preferences, so that I can manage my identity and customize how the app behaves.

#### Acceptance Criteria

1. THE Profile_Page SHALL render a large avatar header section (avatar diameter ≥ 72px) showing the user's initial letter, full name, and email address.
2. THE Profile_Page SHALL render a Personal Information form section with editable fields for Full Name and Email.
3. THE Profile_Page SHALL render a Subscription card labeled "Premium" with amber styling that distinguishes it from standard content cards.
4. THE Profile_Page SHALL render a Learning Preferences section containing: persona/usage mode selector, summary length selector, and explanation style selector.
5. THE Profile_Page SHALL render a Voice Selection control (dropdown) for choosing the TTS voice used across the app.
6. WHEN the user changes preferences and clicks "Save Preferences", THE Profile_Page SHALL call `POST /api/study/preferences` with the updated values and display a confirmation feedback message.
6. WHEN the user clicks "Save Preferences" and "Reset to defaults" simultaneously, THE Profile_Page SHALL prioritize the reset action and ignore the save action, restoring defaults without calling `/api/study/preferences`.
7. WHEN the "Reset to defaults" button is clicked without a simultaneous save, THE Profile_Page SHALL restore the persona to "student", accent to "amber", and summary length to "balanced" without making an API call.
8. THE Profile_Page SHALL render the full Sidebar with the Profile link in active state.

---

### Requirement 13: Static Asset Consolidation and Dead Code Removal

**User Story:** As a developer maintaining the codebase, I want all legacy styles and scripts removed and replaced with clean Aurelius Dark equivalents, so that the project has no conflicting or unused CSS/JS.

#### Acceptance Criteria

1. THE product.css SHALL be the single stylesheet imported by every HTML template; no template SHALL import an additional custom CSS file.
2. WHEN `product.css` is audited, THE Migration SHALL remove any CSS rule blocks that reference colors outside the Aurelius Dark palette (e.g., `#fff`, `#f8f9fa`, Bootstrap light-theme overrides) and are not intentional overrides.
3. THE dashboard.js SHALL be the single JavaScript file imported by every authenticated app page.
4. THE landing.js SHALL be the single JavaScript file imported by every public page.
5. THE Migration SHALL remove any `<script>` or `<style>` tags with inline content from all templates.
6. THE Migration SHALL remove the `dashboard.html` and `index.html` legacy templates if they are no longer referenced by any route in `pages.py`.
7. WHEN `product.css` contains unused CSS class definitions (classes not referenced in any template), THE Migration SHALL remove those definitions.

---

### Requirement 14: Responsive and Accessibility Standards

**User Story:** As a user on any device, I want every page to be usable on mobile and accessible with assistive technologies, so that the app is inclusive and professional.

#### Acceptance Criteria

1. THE UI_System SHALL apply a responsive meta viewport tag (`width=device-width, initial-scale=1.0`) in the `<head>` of every template.
2. WHEN the viewport width is less than 768px, THE Dashboard_Shell SHALL switch from the two-column grid to a single-column stacked layout.
3. THE Sidebar SHALL include `aria-label` attributes on the toggle button, close button, and nav links.
4. ALL interactive controls (buttons, links, inputs) SHALL have a visible focus ring using the amber accent color (`#f59e0b` at 40% opacity) when focused via keyboard.
5. THE UI_System SHALL maintain a minimum color contrast ratio of 4.5:1 between text elements and their backgrounds, using the Aurelius Dark palette values.
6. ALL images and icon-only buttons SHALL include descriptive `alt` text or `aria-label` attributes.
7. WHEN a form is submitted with invalid or missing required fields, THE Form SHALL display an inline error message adjacent to the relevant field without clearing the other field values.
