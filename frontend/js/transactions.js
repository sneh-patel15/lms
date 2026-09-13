async function loadTransactions(status = "") {
  const tbody = document.getElementById("txn-body");
  tbody.innerHTML = `<tr><td colspan="9" class="empty-state">Loading…</td></tr>`;
  try {
    const txns = await api.listTransactions(status);
    renderTransactions(txns);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="9" class="empty-state">${escapeHtml(err.message)}</td></tr>`;
  }
}

function renderTransactions(txns) {
  const tbody = document.getElementById("txn-body");
  if (txns.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="empty-state">No loan records yet.</td></tr>`;
    return;
  }
  const today = new Date().toISOString().split("T")[0];
  tbody.innerHTML = txns
    .map((t) => {
      const overdue = t.status === "issued" && t.due_date < today;
      const statusBadge =
        t.status === "returned"
          ? `<span class="badge badge-ok">Returned</span>`
          : overdue
          ? `<span class="badge badge-danger">Overdue</span>`
          : `<span class="badge badge-warn">Issued</span>`;

      const reminderBadge =
        t.status === "returned"
          ? `<span class="badge badge-ok">Returned</span>`
          : t.is_ready
          ? `<span class="badge badge-ok">Ready (emails stopped)</span>`
          : t.reminder_sent
          ? `<span class="badge badge-warn" title="Sent: ${t.reminder_sent_at || ''}">5d Reminder Sent</span>`
          : `<span style="color:var(--text-muted);font-size:12px;">Scheduled (5d before)</span>`;

      const actions =
        t.status === "issued"
          ? `
            <div class="row-actions">
              <button onclick="returnBook(${t.id})">Mark returned</button>
              <button class="btn-secondary" onclick="toggleReady(${t.id}, ${!t.is_ready})" style="font-size:12px;padding:4px 8px;" title="Stops deadline reminder emails">
                ${t.is_ready ? "Unmark ready" : "Mark ready"}
              </button>
            </div>
          `
          : "—";

      return `
        <tr>
          <td data-label="Book">${escapeHtml(t.book_title)}</td>
          <td data-label="Member">${escapeHtml(t.member_name)}</td>
          <td data-label="Issued">${t.issue_date}</td>
          <td data-label="Due">${t.due_date}</td>
          <td data-label="Returned">${t.return_date || "—"}</td>
          <td data-label="Fine">${t.fine_amount ? "$" + t.fine_amount.toFixed(2) : "—"}</td>
          <td data-label="Status">${statusBadge}</td>
          <td data-label="Reminder">${reminderBadge}</td>
          <td>${actions}</td>
        </tr>
      `;
    })
    .join("");
}

async function returnBook(id) {
  if (!confirm("Mark this book as returned?")) return;
  try {
    const result = await api.returnBook(id);
    const msg = result.fine_amount > 0
      ? `Returned. A fine of $${result.fine_amount.toFixed(2)} applies for late return.`
      : "Returned on time. No fine due.";
    showToast(msg);
    loadTransactions(document.getElementById("status-filter").value);
  } catch (err) {
    showToast(err.message, true);
  }
}

async function toggleReady(id, ready) {
  try {
    await api.toggleReady(id, ready);
    showToast(ready ? "Loan marked ready. Deadline reminder emails stopped." : "Loan unmarked ready.");
    loadTransactions(document.getElementById("status-filter").value);
  } catch (err) {
    showToast(err.message, true);
  }
}

async function handleCheckReminders() {
  const btn = document.getElementById("check-reminders-btn");
  if (btn) btn.disabled = true;
  showToast("Scanning for due loans and sending 5-day reminders...");
  try {
    const res = await api.checkReminders();
    const msg = `Checked ${res.total_active_checked} loans: ${res.reminders_sent} reminder(s) sent, ${res.failed} failed.`;
    showToast(msg, res.failed > 0);
    loadTransactions(document.getElementById("status-filter").value);
  } catch (err) {
    showToast(err.message, true);
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function openIssueModal() {
  try {
    const [books, members] = await Promise.all([api.listBooks(), api.listMembers()]);
    const bookSelect = document.getElementById("issue-book");
    const memberSelect = document.getElementById("issue-member");

    const availableBooks = books.filter((b) => b.available_copies > 0);
    bookSelect.innerHTML = availableBooks.length
      ? availableBooks.map((b) => `<option value="${b.id}">${escapeHtml(b.title)} (${b.available_copies} available)</option>`).join("")
      : `<option value="">No copies available</option>`;

    const activeMembers = members.filter((m) => m.status === "active");
    memberSelect.innerHTML = activeMembers.length
      ? activeMembers.map((m) => `<option value="${m.id}">${escapeHtml(m.name)} (${escapeHtml(m.email)})</option>`).join("")
      : `<option value="">No active members</option>`;

    document.getElementById("issue-modal").classList.add("open");
  } catch (err) {
    showToast(err.message, true);
  }
}

function closeIssueModal() {
  document.getElementById("issue-modal").classList.remove("open");
}

document.getElementById("issue-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const bookId = document.getElementById("issue-book").value;
  const memberId = document.getElementById("issue-member").value;
  if (!bookId || !memberId) {
    showToast("Choose a book and a member first.", true);
    return;
  }
  try {
    await api.issueBook(bookId, memberId);
    showToast("Book issued.");
    closeIssueModal();
    loadTransactions(document.getElementById("status-filter").value);
  } catch (err) {
    showToast(err.message, true);
  }
});

document.getElementById("status-filter").addEventListener("change", (e) => {
  loadTransactions(e.target.value);
});

(async function init() {
  const user = await requireAuth();
  if (!user) return;
  loadTransactions();
})();
