// Shared API helper for the Library Management System frontend.
// All requests go to the same origin (Flask serves both the API and these files).

const API_BASE = "/api";

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method || "GET",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  let data = null;
  try {
    data = await response.json();
  } catch (e) {
    data = null;
  }

  if (!response.ok) {
    const message = (data && data.error) || "Something went wrong. Please try again.";
    throw new Error(message);
  }
  return data;
}

const api = {
  login: (username, password) =>
    apiRequest("/auth/login", { method: "POST", body: { username, password } }),
  register: (payload) =>
    apiRequest("/auth/register", { method: "POST", body: payload }),
  forgotPassword: (login) =>
    apiRequest("/auth/forgot-password", { method: "POST", body: { login } }),
  resetPassword: (token, new_password) =>
    apiRequest("/auth/reset-password", { method: "POST", body: { token, new_password } }),
  logout: () => apiRequest("/auth/logout", { method: "POST" }),
  me: () => apiRequest("/auth/me"),

  listBooks: (q = "") => apiRequest(`/books${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  createBook: (payload) => apiRequest("/books", { method: "POST", body: payload }),
  updateBook: (id, payload) => apiRequest(`/books/${id}`, { method: "PUT", body: payload }),
  deleteBook: (id) => apiRequest(`/books/${id}`, { method: "DELETE" }),

  listMembers: (q = "") => apiRequest(`/members${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  createMember: (payload) => apiRequest("/members", { method: "POST", body: payload }),
  updateMember: (id, payload) => apiRequest(`/members/${id}`, { method: "PUT", body: payload }),
  deleteMember: (id) => apiRequest(`/members/${id}`, { method: "DELETE" }),

  listTransactions: (status = "") =>
    apiRequest(`/transactions${status ? `?status=${status}` : ""}`),
  issueBook: (book_id, member_id, loan_days = undefined) =>
    apiRequest("/transactions/issue", {
      method: "POST",
      body: { book_id, member_id, loan_days },
    }),
  returnBook: (id) => apiRequest(`/transactions/return/${id}`, { method: "POST" }),
  toggleReady: (id, ready = undefined) =>
    apiRequest(`/transactions/ready/${id}`, {
      method: "POST",
      body: ready !== undefined ? { ready } : undefined,
    }),
  checkReminders: () => apiRequest("/transactions/check-reminders", { method: "POST" }),
  dashboardStats: () => apiRequest("/transactions/stats"),
};

// Ensures a user is logged in; redirects to login page otherwise.
// Returns the user object so pages can render name/role in the sidebar.
async function requireAuth() {
  try {
    const { user } = await api.me();
    if (!user) {
      window.location.href = "index.html";
      return null;
    }
    const nameEl = document.getElementById("sidebar-user-name");
    const roleEl = document.getElementById("sidebar-user-role");
    if (nameEl) nameEl.textContent = user.full_name;
    if (roleEl) roleEl.textContent = user.role;
    return user;
  } catch (e) {
    window.location.href = "index.html";
    return null;
  }
}

function showToast(message, isError = false) {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.className = "toast show" + (isError ? " error" : "");
  setTimeout(() => {
    toast.className = "toast" + (isError ? " error" : "");
  }, 3000);
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function handleLogoutClick() {
  try {
    await api.logout();
  } finally {
    window.location.href = "index.html";
  }
}

// ---- Mobile drawer navigation ----
function openSidebar() {
  document.getElementById("sidebar")?.classList.add("open");
  document.getElementById("sidebar-backdrop")?.classList.add("open");
}

function closeSidebar() {
  document.getElementById("sidebar")?.classList.remove("open");
  document.getElementById("sidebar-backdrop")?.classList.remove("open");
}

// Close the drawer automatically when a nav link is tapped on mobile.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".sidebar nav a").forEach((link) => {
    link.addEventListener("click", closeSidebar);
  });
});

// ---- Dark mode ----
const SUN_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
const MOON_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';

function getTheme() {
  return localStorage.getItem("lms-theme") || "light";
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const icon = theme === "dark" ? SUN_ICON : MOON_ICON;
  const label = theme === "dark" ? "Switch to light mode" : "Switch to dark mode";
  document.querySelectorAll(".theme-toggle, .theme-toggle-floating").forEach((btn) => {
    const textSpan = btn.querySelector(".theme-toggle-label");
    btn.setAttribute("aria-label", label);
    btn.innerHTML = textSpan
      ? `${icon}<span class="theme-toggle-label">${theme === "dark" ? "Light mode" : "Dark mode"}</span>`
      : icon;
  });
}

function toggleTheme() {
  const next = getTheme() === "dark" ? "light" : "dark";
  localStorage.setItem("lms-theme", next);
  applyTheme(next);
}

document.addEventListener("DOMContentLoaded", () => applyTheme(getTheme()));
