// landing.js — Public page interactions
// Covers: home.html, landing.html, personalize.html, courses.html, teachers.html

// ── Element references ──────────────────────────────────────────────────────
const registerForm     = document.getElementById("registerForm");
const loginForm        = document.getElementById("loginForm");
const registerFeedback = document.getElementById("registerFeedback");
const loginFeedback    = document.getElementById("loginFeedback");
const authModal        = document.getElementById("authModal");
const loginTabBtn      = document.getElementById("loginTabBtn");
const registerTabBtn   = document.getElementById("registerTabBtn");
const loginPanel       = document.getElementById("loginPanel");
const registerPanel    = document.getElementById("registerPanel");
const personaCards     = document.querySelectorAll(".persona-card");
const personaPreview   = document.getElementById("personaPreview");
const modalCloseBtn    = document.getElementById("modalCloseBtn");
const loginNavBtn      = document.getElementById("loginNavBtn");
const registerNavBtn   = document.getElementById("registerNavBtn");
const heroRegisterBtn  = document.getElementById("heroRegisterBtn");
const coursesRegisterBtn  = document.getElementById("coursesRegisterBtn");
const teachersRegisterBtn = document.getElementById("teachersRegisterBtn");
const continueBtn      = document.getElementById("continueBtn");

// ── Persona content map ──────────────────────────────────────────────────────
const personaContent = {
  student: {
    title: "Student mode",
    description:
      "Focuses on faster note compression, simpler explanations, and efficient revision materials.",
  },
  teacher: {
    title: "Teacher mode",
    description:
      "Leans into clearer lesson-ready structure, presentation support, and simplified teaching explanations.",
  },
  tutor: {
    title: "Tutor mode",
    description:
      "Balances explanations, quizzes, and flexible concept breakdowns for one-on-one teaching sessions.",
  },
  "self-learner": {
    title: "Self-learner mode",
    description:
      "Keeps the workflow balanced between understanding, review, and independent exploration.",
  },
};

// ── Auth view tab switching ──────────────────────────────────────────────────
function setAuthView(view) {
  if (!loginTabBtn || !registerTabBtn || !loginPanel || !registerPanel) return;
  const loginActive = view === "login";
  loginTabBtn.classList.toggle("active", loginActive);
  registerTabBtn.classList.toggle("active", !loginActive);
  loginPanel.classList.toggle("active", loginActive);
  registerPanel.classList.toggle("active", !loginActive);
}

// ── Auth modal open / close (custom overlay — not Bootstrap modal) ───────────
function openAuthModal(view) {
  if (!authModal) return;
  setAuthView(view || "login");
  authModal.style.display = "flex";
  document.body.style.overflow = "hidden";
}

function closeAuthModal() {
  if (!authModal) return;
  authModal.style.display = "none";
  document.body.style.overflow = "";
}

// ── Inline field validation (req 14.7) ───────────────────────────────────────
// Shows the .field-error span adjacent to each invalid field.
// Returns true when all fields are valid, false otherwise.
function validateForm(form) {
  const inputs = form.querySelectorAll("input[required], select[required]");
  let valid = true;

  inputs.forEach((input) => {
    const errorSpan = input.parentElement.querySelector(".field-error");
    let message = "";

    if (!input.value.trim()) {
      message = "This field is required.";
    } else if (input.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim())) {
      message = "Please enter a valid email address.";
    } else if (input.minLength > 0 && input.value.length < input.minLength) {
      message = `Must be at least ${input.minLength} characters.`;
    }

    if (message) {
      valid = false;
      input.setAttribute("aria-invalid", "true");
      if (errorSpan) {
        errorSpan.textContent = message;
        errorSpan.style.display = "block";
      }
    } else {
      input.removeAttribute("aria-invalid");
      if (errorSpan) {
        errorSpan.textContent = "";
        errorSpan.style.display = "none";
      }
    }
  });

  return valid;
}

// Clear all .field-error spans inside a form
function clearFieldErrors(form) {
  form.querySelectorAll(".field-error").forEach((span) => {
    span.textContent = "";
    span.style.display = "none";
  });
  form.querySelectorAll("[aria-invalid]").forEach((el) => el.removeAttribute("aria-invalid"));
}

// ── Persona selection ────────────────────────────────────────────────────────
let currentPersona = localStorage.getItem("studymate-persona") || "student";

function setPersona(persona) {
  const content = personaContent[persona] || personaContent.student;
  currentPersona = persona;

  personaCards.forEach((card) => {
    const isActive = card.dataset.persona === persona;
    card.classList.toggle("active", isActive);

    // Sync aria-checked for radiogroup pages (personalize.html uses role="radio")
    if (card.hasAttribute("aria-checked")) {
      card.setAttribute("aria-checked", isActive ? "true" : "false");
    }
    // Sync aria-pressed for button pages (home.html uses role="button")
    if (card.hasAttribute("aria-pressed")) {
      card.setAttribute("aria-pressed", isActive ? "true" : "false");
    }
  });

  if (personaPreview) {
    personaPreview.innerHTML = `
      <h3 style="color:var(--primary)!important;margin-bottom:8px;">${content.title}</h3>
      <p>${content.description}</p>`;
  }

  localStorage.setItem("studymate-persona", persona);
}

// ── Auth API helpers ─────────────────────────────────────────────────────────
async function submitAuth(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Request failed.");
  }
  return data;
}

function saveSession(data) {
  localStorage.setItem("studymate-token", data.access_token);
  localStorage.setItem("studymate-user", JSON.stringify(data.user));
  window.location.href = "/app/dashboard";
}

// ── Register form submit → POST /api/auth/register ──────────────────────────
registerForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (registerFeedback) registerFeedback.textContent = "";
  clearFieldErrors(registerForm);

  if (!validateForm(registerForm)) return;

  try {
    const payload = Object.fromEntries(new FormData(registerForm).entries());
    localStorage.setItem("studymate-persona", payload.persona || "student");
    const data = await submitAuth("/api/auth/register", payload);
    saveSession(data);
  } catch (error) {
    if (registerFeedback) registerFeedback.textContent = error.message;
  }
});

// ── Login form submit → POST /api/auth/login ────────────────────────────────
loginForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (loginFeedback) loginFeedback.textContent = "";
  clearFieldErrors(loginForm);

  if (!validateForm(loginForm)) return;

  try {
    const data = await submitAuth("/api/auth/login", Object.fromEntries(new FormData(loginForm).entries()));
    saveSession(data);
  } catch (error) {
    if (loginFeedback) loginFeedback.textContent = error.message;
  }
});

// ── Auth tab button clicks ───────────────────────────────────────────────────
loginTabBtn?.addEventListener("click", () => setAuthView("login"));
registerTabBtn?.addEventListener("click", () => setAuthView("register"));

// ── Nav / CTA buttons: open custom overlay modal ─────────────────────────────
// Uses event.preventDefault() to suppress any data-bs-toggle Bootstrap handler
// that may be present on the button in some templates (e.g. personalize.html).
loginNavBtn?.addEventListener("click", (event) => {
  event.preventDefault();
  openAuthModal("login");
});

registerNavBtn?.addEventListener("click", (event) => {
  event.preventDefault();
  openAuthModal("register");
});

heroRegisterBtn?.addEventListener("click", (event) => {
  event.preventDefault();
  openAuthModal("register");
});

coursesRegisterBtn?.addEventListener("click", (event) => {
  event.preventDefault();
  openAuthModal("register");
});

teachersRegisterBtn?.addEventListener("click", (event) => {
  event.preventDefault();
  openAuthModal("register");
});

// ── Modal close button ───────────────────────────────────────────────────────
modalCloseBtn?.addEventListener("click", closeAuthModal);

// ── Backdrop click: click on overlay but NOT on .auth-shell closes modal ─────
authModal?.addEventListener("click", (event) => {
  if (event.target === authModal) {
    closeAuthModal();
  }
});

// ── Keyboard: Escape closes the modal ────────────────────────────────────────
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && authModal && authModal.style.display === "flex") {
    closeAuthModal();
  }
});

// ── Persona card clicks ───────────────────────────────────────────────────────
personaCards.forEach((card) => {
  card.addEventListener("click", () => setPersona(card.dataset.persona));

  // Keyboard support: Enter / Space activate the card
  card.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      setPersona(card.dataset.persona);
    }
  });
});

// ── Continue button (personalize.html): persist persona before navigation ────
// continueBtn is an <a> tag; allow the default href navigation to proceed
// after writing the selected persona to localStorage.
continueBtn?.addEventListener("click", () => {
  localStorage.setItem("studymate-persona", currentPersona);
});

// ── DOMContentLoaded: scroll reveal stagger + initial state ──────────────────
window.addEventListener("DOMContentLoaded", () => {
  // Stagger .reveal-up elements into view
  document.querySelectorAll(".reveal-up").forEach((item, index) => {
    window.setTimeout(() => item.classList.add("is-visible"), index * 100);
  });

  // Set default auth tab view
  setAuthView("login");

  // Restore persona from localStorage (or default to student)
  setPersona(localStorage.getItem("studymate-persona") || "student");
});
