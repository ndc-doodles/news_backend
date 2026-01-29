document.addEventListener("DOMContentLoaded", () => {

// ================= NAVBAR & DRAWER =================
const toggle = document.getElementById('navToggle');
const drawer = document.getElementById('navDrawer');
const closeBtn = document.getElementById('closeDrawer');
const backdrop = document.getElementById('backdrop');
const navbar = document.querySelector('nav'); // navbar element
const applyFiltersBtn = document.getElementById('applyFiltersBtn'); // apply filters button

// ---------------- OPEN DRAWER ----------------
toggle?.addEventListener('click', () => {
  drawer.classList.remove('translate-x-full');
  drawer.classList.add('translate-x-0');
  backdrop.classList.remove('hidden');
  document.body.classList.add('overflow-hidden'); // prevent scrolling
});


// ---------------- CLOSE DRAWER ----------------
window.closeDrawer = function () {
  drawer.classList.add('translate-x-full');
  drawer.classList.remove('translate-x-0');
  backdrop.classList.add('hidden');
  document.body.classList.remove('overflow-hidden');
};

// ---------------- CLOSE EVENTS ----------------
closeBtn?.addEventListener('click', closeDrawer);
backdrop?.addEventListener('click', closeDrawer);
document.addEventListener('keydown', e => {
  if(e.key === 'Escape') closeDrawer();
});

// ---------------- CLOSE DRAWER ON APPLY ----------------
applyFiltersBtn?.addEventListener('click', () => {
  // You can also handle filter logic here
  closeDrawer();
});

// NAVBAR BLUR ON SCROLL
function updateNavbar() {
  const isDark = document.body.classList.contains("dark");

  if (window.scrollY > 20 && isDark) {
    // Dark theme → glass blur
    navbar.classList.add("backdrop-blur", "bg-white/10"); // increase opacity
  } else if (window.scrollY > 20 && !isDark) {
    // Light theme → solid white background, no blur
    navbar.classList.remove("backdrop-blur");
    navbar.classList.add("bg-white");
  } else {
    // At top → transparent for both
    navbar.classList.remove("backdrop-blur", "bg-white", "bg-white/10");
  }
}

window.addEventListener("scroll", updateNavbar);
updateNavbar(); // initial check




  /* ================= THEME ================= */
const themes = {
  light: { body:"#fff", text:"#000", drawer:"#f5f5f5", modal:"#0006", modalContent:"#fff" },
  dark: { body:"#000", text:"#fff", drawer:"#18181b", modal:"#0008", modalContent:"#111" }
};

const desktopToggle = document.getElementById("themeToggle");
const mobileToggle = document.getElementById("themeToggleMobile");

function applyTheme(theme){
  const s = themes[theme];

  // 1️⃣ Toggle body class for CSS-based styling
  document.body.classList.remove("light", "dark");
  document.body.classList.add(theme);

  // 2️⃣ Set inline styles for body & drawer/modal (optional)
  document.body.style.background = s.body;
  document.body.style.color = s.text;
  drawer?.style.setProperty("background", s.drawer);
  document.getElementById("modal")?.style.setProperty("background", s.modal);
  document.getElementById("modalContent")?.style.setProperty("background", s.modalContent);

  // 3️⃣ Save preference
  localStorage.setItem("theme", theme);
}

// 4️⃣ Load saved theme
const savedTheme = localStorage.getItem("theme") || "light";
applyTheme(savedTheme);

// 5️⃣ Set toggle checkboxes
if(desktopToggle) desktopToggle.checked = savedTheme === "dark";
if(mobileToggle) mobileToggle.checked = savedTheme === "dark";

// 6️⃣ Listen to desktop toggle
desktopToggle?.addEventListener("change", () => {
  const t = desktopToggle.checked ? "dark" : "light";
  applyTheme(t);

  // Sync mobile toggle
  if(mobileToggle) mobileToggle.checked = desktopToggle.checked;
});

// 7️⃣ Listen to mobile toggle
mobileToggle?.addEventListener("change", () => {
  const t = mobileToggle.checked ? "dark" : "light";
  applyTheme(t);

  // Sync desktop toggle
  if(desktopToggle){
    desktopToggle.checked = mobileToggle.checked;
  }
});





});



/* ======================================================
   GLOBAL VARIABLES
===================================================== */
let loginModal, signupModal, forgotModal;
let loginBtn, signupBtn, forgotBtn;
let signupError, forgotError;

let layer, spinner, check, cross, pulse;
let textSuccess, textFail;

/* ======================================================
   INITIALIZE
===================================================== */
window.addEventListener("load", () => {
  // Modals
  loginModal  = document.getElementById("loginModal");
  signupModal = document.getElementById("signupModal");
  forgotModal = document.getElementById("forgotModal");

  // Buttons
  loginBtn  = document.getElementById("loginBtn");
  signupBtn = document.getElementById("signupBtn");
  forgotBtn = document.getElementById("forgotBtn");

  // Errors
  signupError = document.getElementById("signupError");
  forgotError = document.getElementById("forgotError");

  // Success / Fail layer
  layer = document.getElementById("successLayer");
  spinner = document.getElementById("spinner");
  check = document.getElementById("checkmark");
  cross = document.getElementById("cross");
  pulse = document.getElementById("pulseBg");
  textSuccess = document.getElementById("successText");
  textFail = document.getElementById("failText");

  // Prevent # jump
  document.querySelectorAll("[data-open]").forEach(el => {
    el.addEventListener("click", e => e.preventDefault());
  });

  attachModalEvents();
});

/* ======================================================
   MODAL EVENTS
===================================================== */
function attachModalEvents() {
  document.querySelectorAll("[data-open='login']").forEach(el =>
    el.addEventListener("click", () => openModal("login"))
  );

  document.querySelectorAll("[data-open='signup']").forEach(el =>
    el.addEventListener("click", () => openModal("signup"))
  );

  document.querySelectorAll("[data-open='forgot']").forEach(el =>
    el.addEventListener("click", () => openModal("forgot"))
  );

  loginBtn?.addEventListener("click", simulateLogin);
  signupBtn?.addEventListener("click", handleSignup);
  forgotBtn?.addEventListener("click", handleForgot);
}

/* ======================================================
   OPEN / CLOSE MODALS (FIXED)
===================================================== */
function openModal(type = "login") {
  closeAllModals();

  let modal = null;
  if (type === "login") modal = loginModal;
  if (type === "signup") modal = signupModal;
  if (type === "forgot") modal = forgotModal;

  if (modal) {
    modal.classList.remove("hidden");
    modal.classList.remove("pointer-events-none"); // ✅ FIX
  }

  document.body.classList.add("overflow-hidden");
}

function closeModal(id) {
  const modal = document.getElementById(id);
  modal?.classList.add("hidden");
  modal?.classList.add("pointer-events-none");
  document.body.classList.remove("overflow-hidden");
}

function closeAllModals() {
  [loginModal, signupModal, forgotModal].forEach(m => {
    if (!m) return;
    m.classList.add("hidden");
    m.classList.add("pointer-events-none"); // ✅ restore
  });
}

/* ======================================================
   LOGIN / SIGNUP / FORGOT
===================================================== */
function simulateLogin() {
  const u = document.getElementById("username").value.trim();
  const p = document.getElementById("password").value;

  if (!u || !p) {
    showFail("Please enter username and password");
    return;
  }

  // Disable button while processing
  loginBtn.disabled = true;

  // Reset previous errors / animations
  resetAnimations();

  fetch("/login-ajax/", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": getCookie("csrftoken")
    },
    body: new URLSearchParams({
      username: u,
      password: p
    })
  })
  .then(res => {
    if (!res.ok) throw new Error("Network response was not ok");
    return res.json();
  })
  .then(data => {
    if (data.success) {
      showSuccess(data.message);
    } else {
      showFail(data.error);
    }
  })
  .catch(err => {
    console.error("Login error:", err);
    showFail("Something went wrong. Try again.");
  })
  .finally(() => {
    // Re-enable button
    loginBtn.disabled = false;
  });
}

function handleSignup() {
  const u = signupUsername.value.trim();
  const e = signupEmail.value.trim();
  const p = signupPassword.value;
  const c = signupConfirm.value;

  if (!u || !e || !p || !c) {
    signupError.textContent = "All fields are required";
    signupError.classList.remove("hidden");
    return;
  }

  signupError.classList.add("hidden");

  fetch("/signup-ajax/", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": getCookie("csrftoken")
    },
    body: new URLSearchParams({
      username: u,
      email: e,
      password: p,
      confirm: c
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showSuccess("Account created successfully!");

      // ✅ Option 1: reload page to reflect authenticated state
      window.location.reload();

    } else {
      signupError.textContent = data.error;
      signupError.classList.remove("hidden");
    }
  })
  .catch(() => {
    signupError.textContent = "Server error. Try again.";
    signupError.classList.remove("hidden");
  });
}

function handleForgot() {
  const value = document.getElementById("forgotUsername").value.trim();

  if (!value) {
    forgotError.textContent = "Enter username or email";
    forgotError.classList.remove("hidden");
    return;
  }

  forgotError.classList.add("hidden");

  fetch("/forgot-password-ajax/", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": getCookie("csrftoken")
    },
    body: new URLSearchParams({ username: value })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showSuccess(data.message);
    } else {
      forgotError.textContent = data.error;
      forgotError.classList.remove("hidden");
    }
  })
  .catch(() => {
    forgotError.textContent = "Server error. Try again.";
    forgotError.classList.remove("hidden");
  });
}


/* ======================================================
   CSRF HELPER (REQUIRED)
===================================================== */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/* ======================================================
   SUCCESS / FAIL ANIMATION
===================================================== */
function resetAnimations() {
  spinner.classList.remove("hidden");
  check.classList.add("hidden");
  cross.classList.add("hidden");
  pulse.classList.add("hidden");
  textSuccess.classList.add("hidden");
  textFail.classList.add("hidden");
}

function showSuccess(msg) {
  resetAnimations();
  layer.classList.remove("hidden");

  textSuccess.textContent = msg;
  textSuccess.classList.remove("hidden");

  setTimeout(() => {
    spinner.classList.add("hidden");
    check.classList.remove("hidden");
    pulse.classList.remove("hidden");

    setTimeout(() => {
      layer.classList.add("hidden");
      closeAllModals();
    }, 1200);
  }, 600);
}

function showFail(msg) {
  resetAnimations();
  layer.classList.remove("hidden");

  spinner.classList.add("hidden");
  cross.classList.remove("hidden");
  textFail.textContent = msg;
  textFail.classList.remove("hidden");

  setTimeout(() => layer.classList.add("hidden"), 1200);
}



