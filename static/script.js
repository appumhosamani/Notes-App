$("#signup-btn").on("click", function () {
  const name = $("#signup-name").val().trim();
  const email = $("#signup-email").val().trim();
  const password = $("#signup-password").val();
  const confirm = $("#signup-confirm-password").val();

  if (!name || !email || !password || !confirm) {
    $("#signup-message").html(`<p class='error'>please enter all the fields.</p>`);
    return;
  }

  if (password !== confirm) {
    $("#signup-message").html(`<p class='error'>Passwords not matching...</p>`);
    return;
  }

  $.ajax({
    url: "/api/signup",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ name, email, password, confirm_password: confirm }),
    success: function (res) {
      $("#signup-message").html(`<p class='success'>${res.message}</p>`);
      setTimeout(() => (window.location.href = "/login"), 1200);
    },
    error: function (xhr) {
      const msg = (xhr.responseJSON && xhr.responseJSON.message) || "Signup failed.";
      $("#signup-message").html(`<p class='error'>${msg}</p>`);
    },
  });
});


$("#login-btn").on("click", function () {
  const email = $("#login-email").val().trim();
  const password = $("#login-password").val();

  if (!email || !password) {
    $("#login-message").html(`<p class='error'>Enter email and password.</p>`);
    return;
  }

  $.ajax({
    url: "/api/login",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ email, password }),
    success: function (res) {
      window.location.href = res.redirect;
    },
    error: function (xhr) {
      const msg = (xhr.responseJSON && xhr.responseJSON.message) || "Login failed.";
      $("#login-message").html(`<p class='error'>${msg}</p>`);
    },
  });
});

// --- notes 




let editingId = null;

function openPopup() {
  editingId = null;
  $("#popup-title").text("Add Notes");
  $("#save-btn").text("Add");
  $("#note-title").val("");
  $("#note-content").val("");
  $("#popup").removeClass("hidden");
}

function openEdit(id, title, content) {
  editingId = id;
  $("#popup-title").text("Edit Note");
  $("#save-btn").text("Update");
  $("#note-title").val(title);
  $("#note-content").val(content);
  $("#popup").removeClass("hidden");
}

function closePopup() {
  $("#popup").addClass("hidden");
}


function saveNote() {
  const title = $("#note-title").val().trim();
  const content = $("#note-content").val().trim();

  if (!title || !content) {
    alert("Both Title and Content are required!");
    return;
  }

  if (editingId) {
    $.ajax({
      url: `/edit_note/${editingId}`,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ title, content }),
      success: () => location.reload(),
      error: () => alert("Failed to update note."),
    });
  } else {
    $.ajax({
      url: "/add_note",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ title, content }),
      success: () => location.reload(),
      error: () => alert("Failed to add note."),
    });
  }
}

function deleteNote(id) {
  if (!confirm("Delete this note?")) return;
  $.ajax({
    url: `/delete_note/${id}`,
    method: "DELETE",
    success: () => location.reload(),
    error: () => alert("Failed to delete note."),
  });
}

