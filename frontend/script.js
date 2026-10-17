document.addEventListener("DOMContentLoaded", () => {
  const taskForm = document.getElementById("task-form");
  const taskInput = document.getElementById("task-input");
  const taskList = document.getElementById("task-list");

  async function api(path = "", method = "GET", body) {
    const response = await fetch(`/api/tasks${path}`, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body && JSON.stringify(body),
    });
    if (!response.ok)
      throw new Error(`${method} ${path} failed (${response.status})`);
    return response.json();
  }

  function render(tasks) {
    taskList.replaceChildren(
      ...tasks.map(({ id, title, completed }) => {
        const li = document.createElement("li");
        li.dataset.id = id;
        li.classList.toggle("completed", completed);
        li.innerHTML = `
                <span class="task-title"></span>
                <div class="task-actions">
                    <button class="toggle-btn">${completed ? "Undo" : "Done"}</button>
                    <button class="delete-btn">Delete</button>
                </div>`;
        li.querySelector(".task-title").textContent = title;
        return li;
      }),
    );
  }

  // Run an optional mutation, then reload the list. One place for error handling.
  async function sync(mutation) {
    try {
      await mutation?.();
      render(await api());
    } catch (error) {
      console.error(error);
    }
  }

  taskForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const title = taskInput.value.trim();
    if (!title) return;
    sync(async () => {
      await api("", "POST", { title });
      taskInput.value = "";
    });
  });

  taskList.addEventListener("click", ({ target }) => {
    const li = target.closest("li");
    if (!li) return;
    const { id } = li.dataset;

    if (target.matches(".toggle-btn")) {
      sync(() =>
        api(`/${id}`, "PATCH", {
          completed: !li.classList.contains("completed"),
        }),
      );
    } else if (
      target.matches(".delete-btn") &&
      confirm("Are you sure you want to delete this task?")
    ) {
      sync(() => api(`/${id}`, "DELETE"));
    }
  });

  sync();
});
