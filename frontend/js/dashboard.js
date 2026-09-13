(async function init() {
  const user = await requireAuth();
  if (!user) return;

  try {
    const stats = await api.dashboardStats();
    const grid = document.getElementById("stat-grid");
    grid.innerHTML = `
      <div class="stat-card"><div class="value">${stats.total_books}</div><div class="label">Total copies in catalog</div></div>
      <div class="stat-card"><div class="value">${stats.available_books}</div><div class="label">Copies available now</div></div>
      <div class="stat-card"><div class="value">${stats.total_members}</div><div class="label">Registered members</div></div>
      <div class="stat-card"><div class="value">${stats.books_issued}</div><div class="label">Books currently issued</div></div>
      <div class="stat-card warn"><div class="value">${stats.overdue}</div><div class="label">Overdue returns</div></div>
    `;

    const issued = await api.listTransactions("issued");
    const tbody = document.getElementById("issued-body");
    if (issued.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="empty-state">Nothing is out on loan right now.</td></tr>`;
      return;
    }

    const today = new Date().toISOString().split("T")[0];
    tbody.innerHTML = issued
      .map((t) => {
        const overdue = t.due_date < today;
        return `
          <tr>
            <td data-label="Book">${escapeHtml(t.book_title)}</td>
            <td data-label="Member">${escapeHtml(t.member_name)}</td>
            <td data-label="Issued">${t.issue_date}</td>
            <td data-label="Due">${t.due_date}</td>
            <td data-label="Status"><span class="badge ${overdue ? "badge-danger" : "badge-ok"}">${overdue ? "Overdue" : "On time"}</span></td>
          </tr>
        `;
      })
      .join("");
  } catch (err) {
    showToast(err.message, true);
  }
})();
