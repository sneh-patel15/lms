let allBooks = [];

async function loadBooks(q = "") {
  const tbody = document.getElementById("books-body");
  tbody.innerHTML = `<tr><td colspan="7" class="empty-state">Loading…</td></tr>`;
  try {
    allBooks = await api.listBooks(q);
    renderBooks(allBooks);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state">${escapeHtml(err.message)}</td></tr>`;
  }
}

function renderBooks(books) {
  const tbody = document.getElementById("books-body");
  if (books.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No books match yet. Try adding one.</td></tr>`;
    return;
  }
  tbody.innerHTML = books
    .map((b) => {
      const availBadge = b.available_copies === 0 ? "badge-danger" : "badge-ok";
      return `
        <tr>
          <td data-label="Title">${escapeHtml(b.title)}</td>
          <td data-label="Author">${escapeHtml(b.author)}</td>
          <td data-label="Category">${escapeHtml(b.category || "—")}</td>
          <td data-label="Copies">${b.total_copies}</td>
          <td data-label="Available"><span class="badge ${availBadge}">${b.available_copies}</span></td>
          <td data-label="Shelf">${escapeHtml(b.shelf_location || "—")}</td>
          <td>
            <div class="row-actions">
              <button onclick="openBookModal(${b.id})">Edit</button>
              <button class="danger" onclick="deleteBook(${b.id})">Delete</button>
            </div>
          </td>
        </tr>
      `;
    })
    .join("");
}

function openBookModal(id = null) {
  const modal = document.getElementById("book-modal");
  const form = document.getElementById("book-form");
  form.reset();
  document.getElementById("book-id").value = "";
  document.getElementById("book-modal-title").textContent = id ? "Edit book" : "Add a book";

  if (id) {
    const book = allBooks.find((b) => b.id === id);
    if (book) {
      document.getElementById("book-id").value = book.id;
      document.getElementById("book-title").value = book.title;
      document.getElementById("book-author").value = book.author;
      document.getElementById("book-isbn").value = book.isbn || "";
      document.getElementById("book-category").value = book.category || "";
      document.getElementById("book-publisher").value = book.publisher || "";
      document.getElementById("book-shelf").value = book.shelf_location || "";
      document.getElementById("book-copies").value = book.total_copies;
    }
  }
  modal.classList.add("open");
}

function closeBookModal() {
  document.getElementById("book-modal").classList.remove("open");
}

async function deleteBook(id) {
  if (!confirm("Remove this book from the catalog? This cannot be undone.")) return;
  try {
    await api.deleteBook(id);
    showToast("Book removed.");
    loadBooks(document.getElementById("search-input").value.trim());
  } catch (err) {
    showToast(err.message, true);
  }
}

document.getElementById("book-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("book-id").value;
  const payload = {
    title: document.getElementById("book-title").value.trim(),
    author: document.getElementById("book-author").value.trim(),
    isbn: document.getElementById("book-isbn").value.trim() || null,
    category: document.getElementById("book-category").value.trim() || null,
    publisher: document.getElementById("book-publisher").value.trim() || null,
    shelf_location: document.getElementById("book-shelf").value.trim() || null,
    total_copies: parseInt(document.getElementById("book-copies").value, 10),
  };

  try {
    if (id) {
      await api.updateBook(id, payload);
      showToast("Book updated.");
    } else {
      await api.createBook(payload);
      showToast("Book added to the catalog.");
    }
    closeBookModal();
    loadBooks(document.getElementById("search-input").value.trim());
  } catch (err) {
    showToast(err.message, true);
  }
});

let searchTimer = null;
document.getElementById("search-input").addEventListener("input", (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadBooks(e.target.value.trim()), 300);
});

(async function init() {
  const user = await requireAuth();
  if (!user) return;
  loadBooks();
})();
