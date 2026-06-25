# Requirements Document

## Introduction

StudyMate AI is a FastAPI + Jinja2 learning assistant application. Over time the project accumulated multiple UI generations: an initial single-page prototype (`index.html`), an early multi-panel dashboard (`dashboard.html`), a standalone landing variant (`landing.html`), and a deprecated customise page (`app_customize.html`). These legacy files coexist with the current "Aurelius Dark" design system implemented across the `app_*` template family and `product.css`. The result is:

- Four templates that are never rendered by any live route (dead code).
- Three public marketing pages (`courses.html`, `teachers.html`, `personalize.html`) still using the old `Plus Jakarta Sans` font instead of `Inter`, missing the canonical `accent-amber` body class, missing the favicon link, and missing mobile-responsive navbar collapsing.
- `app_customize.html` using a deprecated sidebar structure without the modern mobile toggle, close button, or `sidebar-header` wrapper, and routing to `/app/customize` which already redirects to `/app/profile`.
- The sidebar HTML block is copy-pasted identically into every `app_*` template, creating a maintenance burden and a source of divergence.
- `dashboard.js` references element IDs that only exist on some pages, producing silent null-reference failures on pages that share the script but do not include every element.

This migration removes all legacy UI, standardises every page on the Aurelius Dark design system, eliminates dead templates and their associated route entries, and extracts the repeated sidebar into a single reusable Jinja2 partial.

## Glossary

- **Aurelius Dark Design System**: The current design language defined in `product.css`. Characteristics: dark surface palette (`--surface: #121414`), Inter font, amber primary accent (`--primary: #f59e0b`), CSS custom-property tokens for surfaces, radii, shadows, and typography.
- **Legacy UI**: Any template, stylesheet, or script that does not conform to the Aurelius Dark design system. Specifically: `index.html`, `dashboard.html`, `landing.html`, `app_customize.html`, and the `Plus Jakarta Sans` font references remaining in `courses.html`, `teachers.html`, and `personalize.html`.
- **Sidebar Partial**: A reusable Jinja2 include block (`app/templates/partials/sidebar.html`) that contains the full sidebar HTML with a `current_page` variable controlling which nav item receives the `active` class.
- **App Pages**: The authenticated tool pages: `app_dashboard.html`, `app_summarizer.html`, `app_explainer.html`, `app_audio.html`, `app_quiz.html`, `app_slides.html`, `app_saved.html`, `app_profile.html`.
- **Marketing Pages**: The public pages: `home.html` (served at `/`), `courses.html`, `teachers.html`, `personalize.html`.
- **Dead Template**: A template file that is not referenced by any route handler in `pages.py` and is never included by another template.
- **Route Handler**: A FastAPI endpoint in `app/api/routes/pages.py` that returns a `FileResponse` for a template.
- **Product.css**: The single CSS file at `app/static/product.css` that contains all design tokens, component styles, and layout rules for the Aurelius Dark system. No other project-specific stylesheet exists.
- **Dashboard.js**: The single script at `app/static/dashboard.js` that handles all authenticated-page interactivity: API calls, sidebar toggle, attach menu, preferences, profile population, and audio playback.

---

## Requirements

### Requirement 1: Remove Dead Templates and Their Route Entries

**User Story:** As a developer maintaining the codebase, I want all unreachable HTML templates and their associated route handlers deleted, so that there is no orphaned code that could mislead future contributors or cause confusion about the canonical page set.

#### Acceptance Criteria

1. THE Migration SHALL delete `app/templates/index.html` from the filesystem.
2. THE Migration SHALL delete `app/templates/dashboard.html` from the filesystem.
3. THE Migration SHALL delete `app/templates/landing.html` from the filesystem.
4. THE Migration SHALL delete `app/templates/app_customize.html` from the filesystem.
5. WHEN `app/api/routes/pages.py` is inspected after migration, THE Route_Handler SHALL contain no import or function reference for any deleted template path.
6. THE Migration SHALL ensure the `/app/customize` route redirect in `pages.py` is removed alongside the `app_customize.html` deletion, since the route served no content of its own.
7. IF any other Python file imports or references a deleted template path, THEN THE Migration SHALL update that reference to remove or replace it.

---

### Requirement 2: Standardise Marketing Pages on Aurelius Dark

**User Story:** As a user visiting the public site, I want every page to look and feel consistent, so that the brand and design quality feel unified from the first page I land on through to the app itself.

#### Acceptance Criteria

1. THE Migration SHALL update `courses.html`, `teachers.html`, and `personalize.html` to load the `Inter` Google Font instead of `Plus Jakarta Sans`.
2. THE Migration SHALL add `class="landing-body accent-amber"` to the `<body>` tag of `courses.html`, `teachers.html`, and `personalize.html` to match the body class used in `home.html`.
3. THE Migration SHALL add `<link rel="icon" href="/favicon.ico" type="image/x-icon">` to the `<head>` of `courses.html`, `teachers.html`, and `personalize.html`.
4. THE Marketing_Pages SHALL use the `product-nav-education` navbar pattern already established in `home.html` with the collapsible mobile hamburger (`navbar-toggler`, `data-bs-toggle="collapse"`).
5. WHEN any marketing page is rendered, THE Page SHALL contain no reference to `Plus Jakarta Sans` in any `<link>` tag or inline style.
6. THE Marketing_Pages SHALL include the Bootstrap JS bundle (`bootstrap.bundle.min.js`) and `landing.js` in the same order and at the same version (`5.3.7`) used by `home.html`.

---

### Requirement 3: Extract Sidebar into a Reusable Partial

**User Story:** As a developer, I want the sidebar HTML defined in exactly one place, so that any future change to the sidebar only requires editing one file and every app page reflects the update automatically.

#### Acceptance Criteria

1. THE Migration SHALL create `app/templates/partials/sidebar.html` containing the complete sidebar HTML block currently duplicated across all eight app pages.
2. THE Sidebar_Partial SHALL accept a `current_page` Jinja2 variable and use it to conditionally apply the `active` CSS class to the matching nav link (`{% if current_page == 'dashboard' %}active{% endif %}`).
3. THE Migration SHALL replace the inline sidebar HTML in each app page with `{% include "partials/sidebar.html" %}`, passing the appropriate `current_page` value.
4. WHEN any app page is rendered, THE Sidebar SHALL render identically to the sidebar that was previously inlined on that page, with the correct nav item marked active.
5. THE Sidebar_Partial SHALL include the sidebar backdrop button, sidebar header with brand lockup, "New Summary" button, navigation section, and user info block — all elements present in the current inlined version.
6. BECAUSE the route handlers use `FileResponse` and Jinja2 templating is not currently enabled, THE Migration SHALL enable Jinja2 template rendering for app pages via `Jinja2Templates` so that `{% include %}` directives resolve correctly.

---

### Requirement 4: Fix App Page Route Handlers for Jinja2 Rendering

**User Story:** As a developer, I want the page route handlers to use Jinja2 template rendering instead of raw file responses, so that template includes and variables work correctly.

#### Acceptance Criteria

1. THE Migration SHALL replace `FileResponse` returns with `templates.TemplateResponse` calls in `app/api/routes/pages.py` for all app pages that use Jinja2 includes or template variables.
2. THE Route_Handler SHALL pass a `current_page` context variable to each `TemplateResponse` call, set to the page identifier string matching the sidebar nav (e.g., `"dashboard"`, `"summarizer"`, `"explainer"`, `"audio"`, `"quiz"`, `"slides"`, `"saved"`, `"profile"`).
3. THE Route_Handler for marketing pages (`/`, `/courses`, `/teachers`, `/personalize`) SHALL continue using `FileResponse` if those templates require no Jinja2 processing, OR be updated to `TemplateResponse` if they require variable injection.
4. THE Migration SHALL instantiate `Jinja2Templates(directory="app/templates")` in `pages.py` or in a shared location accessible to the router.
5. WHEN a protected page route is accessed without a valid session cookie, THE Route_Handler SHALL still redirect to `/` as before (the authentication check logic remains unchanged).

---

### Requirement 5: Eliminate Deprecated Sidebar Structure in app_customize.html

**User Story:** As a developer, I want every app-internal page to use the same sidebar structure, so that mobile navigation works consistently and there are no structural divergences between pages.

**Note:** This requirement is fully satisfied by Requirement 1 (deleting `app_customize.html`) and Requirement 3 (replacing all sidebars with the single partial). It is stated explicitly to document that `app_customize.html`'s deprecated sidebar — which lacked the `sidebar-header` wrapper, `sidebar-close-btn`, `sidebar-backdrop`, and mobile toggle — must not survive in any form.

#### Acceptance Criteria

1. THE Migration SHALL ensure no app page contains a sidebar using the deprecated `dashboard-sidebar-education` CSS class.
2. THE Migration SHALL ensure no app page contains a sidebar without the `sidebar-header`, `sidebar-close-btn`, and `sidebar-backdrop` elements.
3. WHEN any app page is rendered on a mobile viewport (width ≤ 1199px), THE Sidebar SHALL be hidden by default and toggleable via the hamburger button in the top bar.

---

### Requirement 6: Remove Dead CSS and Validate Style Consistency

**User Story:** As a developer, I want no CSS classes in `product.css` that exclusively existed to support deleted legacy templates, so that the stylesheet does not accumulate dead rules over time.

#### Acceptance Criteria

1. THE Migration SHALL audit `product.css` for CSS classes whose sole consumers were `index.html` or `dashboard.html`.
2. IF a CSS class is exclusively used by a deleted template and appears nowhere in the surviving template set, THEN THE Migration SHALL remove that CSS rule from `product.css`.
3. THE Migration SHALL verify that `product.css` retains all classes required by the surviving templates: `app_dashboard.html`, `app_summarizer.html`, `app_explainer.html`, `app_audio.html`, `app_quiz.html`, `app_slides.html`, `app_saved.html`, `app_profile.html`, `home.html`, `courses.html`, `teachers.html`, and `personalize.html`.
4. WHEN any surviving page is rendered after the CSS audit, THE Page SHALL not display broken or unstyled components due to a removed CSS rule.

---

### Requirement 7: Responsive Behaviour Across All Surviving Pages

**User Story:** As a user on a mobile or tablet device, I want every page to be usable and visually consistent, so that I can study on any screen size without encountering broken layouts.

#### Acceptance Criteria

1. THE Migration SHALL verify that `product.css` contains media query rules covering the responsive sidebar toggle (show/hide at ≤ 1199px breakpoint) for all app pages.
2. THE Marketing_Pages SHALL use the Bootstrap navbar collapse pattern so navigation links collapse into a hamburger menu on small screens.
3. WHEN the sidebar toggle button is tapped on a viewport ≤ 1199px wide, THE Sidebar SHALL open as an overlay without breaking the main content layout.
4. THE Migration SHALL ensure no inline `display:none` or fixed-width style in any template overrides the responsive CSS rules defined in `product.css`.

---

### Requirement 8: Consistent Head Block Across All Surviving Templates

**User Story:** As a developer, I want every template to have a standardised `<head>` block structure, so that all pages load the same fonts, CSS, and favicon in a consistent order.

#### Acceptance Criteria

1. THE Migration SHALL ensure every surviving template loads fonts via `<link rel="preconnect">` to `fonts.googleapis.com` and `fonts.gstatic.com` followed by the `Inter` font at weights `400;500;600;700;800`.
2. THE Migration SHALL ensure every surviving template loads Bootstrap CSS at version `5.3.7` (`cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css`) before `product.css`.
3. THE Migration SHALL ensure every surviving template includes `<link rel="icon" href="/favicon.ico" type="image/x-icon">`.
4. THE App_Pages SHALL load `product.css` with the cache-bust query parameter `?v=3` (or a higher version if `product.css` is modified during migration).
5. THE App_Pages SHALL NOT load Bootstrap JS (it is not required for authenticated pages and adds unnecessary weight); only marketing pages that use Bootstrap modals SHALL load `bootstrap.bundle.min.js`.

---

### Requirement 9: Post-Migration Verification Report

**User Story:** As a developer, I want a written summary of every change made during the migration, so that I can confirm nothing was missed and communicate the scope of changes to teammates.

#### Acceptance Criteria

1. WHEN the migration is complete, THE Migration SHALL produce a `MIGRATION_REPORT.md` file at the project root listing: all deleted files, all modified files with a one-line description of each change, the legacy components removed, the new components now in use, and any known remaining inconsistencies.
2. THE Migration_Report SHALL include a section confirming that each of the eight surviving app pages uses the sidebar partial, the correct `current_page` value, and the standardised head block.
3. THE Migration_Report SHALL include a section confirming that each of the four surviving marketing pages uses the `Inter` font, the `accent-amber` body class, the favicon link, and the Bootstrap collapse navbar.
4. THE Migration_Report SHALL list any CSS classes removed from `product.css` as a result of deleting the legacy templates.
