let allMembers = [];

async function loadMembers(q = "") {
  const tbody = document.getElementById("members-body");
  tbody.innerHTML = `<tr><td colspan="6" class="empty-state">Loading…</td></tr>`;
  try {
    allMembers = await api.listMembers(q);
    renderMembers(allMembers);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state">${escapeHtml(err.message)}</td></tr>`;
  }
}

function renderMembers(members) {
  const tbody = document.getElementById("members-body");
  if (members.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state">No members yet. Add the first one.</td></tr>`;
    return;
  }
  tbody.innerHTML = members
    .map((m) => `
      <tr>
        <td data-label="Name">${escapeHtml(m.name)}</td>
        <td data-label="Email">${escapeHtml(m.email)}</td>
        <td data-label="Phone">${escapeHtml(m.phone || "—")}</td>
        <td data-label="Joined">${m.membership_date || "—"}</td>
        <td data-label="Status"><span class="badge ${m.status === "active" ? "badge-ok" : "badge-danger"}">${m.status}</span></td>
        <td>
          <div class="row-actions">
            <button onclick="openMemberModal(${m.id})">Edit</button>
            <button class="danger" onclick="deleteMember(${m.id})">Delete</button>
          </div>
        </td>
      </tr>
    `)
    .join("");
}

function openMemberModal(id = null) {
  const modal = document.getElementById("member-modal");
  const form = document.getElementById("member-form");
  form.reset();
  document.getElementById("member-id").value = "";
  document.getElementById("member-modal-title").textContent = id ? "Edit member" : "Add a member";

  if (id) {
    const member = allMembers.find((m) => m.id === id);
    if (member) {
      document.getElementById("member-id").value = member.id;
      document.getElementById("member-name").value = member.name;
      document.getElementById("member-email").value = member.email;
      document.getElementById("member-phone").value = member.phone || "";
      document.getElementById("member-address").value = member.address || "";
      document.getElementById("member-status").value = member.status;
    }
  }
  modal.classList.add("open");
}

function closeMemberModal() {
  document.getElementById("member-modal").classList.remove("open");
}

async function deleteMember(id) {
  if (!confirm("Remove this member? This cannot be undone.")) return;
  try {
    await api.deleteMember(id);
    showToast("Member removed.");
    loadMembers(document.getElementById("search-input").value.trim());
  } catch (err) {
    showToast(err.message, true);
  }
}

document.getElementById("member-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("member-id").value;
  const payload = {
    name: document.getElementById("member-name").value.trim(),
    email: document.getElementById("member-email").value.trim(),
    phone: document.getElementById("member-phone").value.trim() || null,
    address: document.getElementById("member-address").value.trim() || null,
    status: document.getElementById("member-status").value,
  };

  try {
    if (id) {
      await api.updateMember(id, payload);
      showToast("Member updated.");
    } else {
      await api.createMember(payload);
      showToast("Member added.");
    }
    closeMemberModal();
    loadMembers(document.getElementById("search-input").value.trim());
  } catch (err) {
    showToast(err.message, true);
  }
});

let searchTimer = null;
document.getElementById("search-input").addEventListener("input", (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadMembers(e.target.value.trim()), 300);
});

(async function init() {
  const user = await requireAuth();
  if (!user) return;
  loadMembers();
})();
