document.querySelectorAll("form[data-kind]").forEach(function (form) {
  form.addEventListener("submit", function (event) {
    let errors = [];
    const kind = form.dataset.kind;
    const value = name => form.elements[name].value;
    if (kind === "register") {
      if (!value("name").trim()) errors.push("Name is required");
      if (!value("email").trim()) errors.push("Email is required");
      if (!value("password")) errors.push("Password is required");
      if (!value("confirm_password")) errors.push("Confirm password is required");
      if (value("password") && value("confirm_password") && value("password") !== value("confirm_password")) errors.push("Passwords do not match");
      if (Array.from(value("name").trim()).length > 100) errors.push("Name is too long (100 characters at most)");
      if (Array.from(value("email").trim()).length > 255) errors.push("Email is too long (255 characters at most)");
      if (new TextEncoder().encode(value("password")).length > 72) errors.push("Password is too long (72 bytes at most)");
    }
    if (kind === "login") {
      if (!value("email").trim()) errors.push("Email is required");
      if (!value("password")) errors.push("Password is required");
    }
    if (kind === "todo") {
      if (!value("title").trim()) errors.push("Title is required");
      else if (Array.from(value("title").trim()).length > 200) errors.push("Title is too long");
    }
    const box = form.querySelector(".errors");
    box.replaceChildren();
    errors.forEach(function (error) { const p = document.createElement("p"); p.textContent = error; box.appendChild(p); });
    if (errors.length) event.preventDefault();
  });
});
document.querySelectorAll("form[data-delete]").forEach(function (form) {
  form.addEventListener("submit", function (event) {
    if (!confirm("Are you sure?")) event.preventDefault();
  });
});