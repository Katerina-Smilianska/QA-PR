// ── Auth ──────────────────────────────────────────────────────────
const CREDENTIALS = { username: "admin", password: "@Dm1n" };

function login() {
  const enteredUser = document.getElementById("username").value.trim();
  const enteredPass = document.getElementById("password").value;
  const errorEl     = document.getElementById("loginError");

  if (enteredUser === CREDENTIALS.username && enteredPass === CREDENTIALS.password) {
    document.getElementById("loginPage").style.display = "none";
    document.getElementById("app").classList.remove("hidden");

    const initials = enteredUser.substring(0, 2).toUpperCase();
    document.getElementById("userBadge").textContent = initials;

    switchPage("cameras", document.querySelector('[data-page="cameras"]'));
  } else {
    errorEl.textContent = "Incorrect username or password.";
  }
}

function logout() {
  location.reload();
}

// ── Navigation ────────────────────────────────────────────────────
function switchPage(pageId, clickedBtn) {
  // Hide all sections
  document.querySelectorAll(".page").forEach(function(section) {
    section.classList.add("hidden");
  });

  // Deactivate all nav buttons
  document.querySelectorAll(".nav-btn").forEach(function(btn) {
    btn.classList.remove("active");
  });

  // Show target section
  document.getElementById(pageId).classList.remove("hidden");

  // Mark active button
  if (clickedBtn) {
    clickedBtn.classList.add("active");
  }
}

// ── Form Validation ───────────────────────────────────────────────
var EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
var PHONE_PATTERN = /^\+?[0-9\s]{7,15}$/;

function checkEmail() {
  var value   = document.getElementById("email").value;
  var errorEl = document.getElementById("emailError");

  if (value === "") {
    errorEl.textContent = "Email address is required.";
    return false;
  }
  if (!EMAIL_PATTERN.test(value)) {
    errorEl.textContent = "Please enter a valid email (e.g. name@domain.com).";
    return false;
  }
  errorEl.textContent = "";
  return true;
}

function checkPhone() {
  var value   = document.getElementById("phone").value;
  var errorEl = document.getElementById("phoneError");

  if (value === "") {
    errorEl.textContent = "Phone number is required.";
    return false;
  }
  if (!PHONE_PATTERN.test(value)) {
    errorEl.textContent = "Phone must be 7–15 digits (+ prefix allowed).";
    return false;
  }
  errorEl.textContent = "";
  return true;
}

// ── Form Submit ───────────────────────────────────────────────────
function handleSubmit(e) {
  e.preventDefault();

  var name        = document.getElementById("name").value.trim();
  var nameErrorEl = document.getElementById("nameError");
  var successEl   = document.getElementById("formSuccess");

  // Validate name
  if (name === "") {
    nameErrorEl.textContent = "Name is required.";
  } else {
    nameErrorEl.textContent = "";
  }

  var emailOk = checkEmail();
  var phoneOk = checkPhone();

  if (name !== "" && emailOk && phoneOk) {
    successEl.textContent = "Message sent successfully!";
  } else {
    successEl.textContent = "";
  }
}
