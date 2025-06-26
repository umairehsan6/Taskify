
      document.addEventListener("DOMContentLoaded", function () {
        const modal = document.getElementById("createTaskModal");

        modal.addEventListener("show.bs.modal", function (event) {
          const button = event.relatedTarget;
          const projectId = button.getAttribute("data-project-id");
          const projectName = button
            .closest("tr")
            .querySelector("td:nth-child(2)").textContent;

          // Update hidden project ID field
          const projectIdInput = modal.querySelector(
            'input[name="project_id"]'
          );
          projectIdInput.value = projectId;

          // Update project name display
          const projectNameInput = modal.querySelector(
            'input[name="project_name"]'
          );
          projectNameInput.value = projectName;

          // Update form action
          const form = modal.querySelector("#createTaskForm");
          form.action = `{% url 'create_task' %}?project_id=${projectId}`;

          // Fetch employees for the project's department
          fetch(`/admin-dashboard/?project_id=${projectId}`)
            .then((response) => response.text())
            .then((html) => {
              // Extract the filtered employees from the response
              const parser = new DOMParser();
              const doc = parser.parseFromString(html, "text/html");
              const employeeSelect = modal.querySelector(
                'select[name="assigned_to"]'
              );
              const newEmployeeSelect = doc.querySelector(
                'select[name="assigned_to"]'
              );

              if (newEmployeeSelect) {
                employeeSelect.innerHTML = newEmployeeSelect.innerHTML;
              }
            })
            .catch((error) => console.error("Error:", error));
        });
      });

      document.addEventListener("DOMContentLoaded", function () {
        const modals = document.querySelectorAll(".modal");
        modals.forEach((modal) => {
          modal.addEventListener("show.bs.modal", function (event) {
            const button = event.relatedTarget;
            const projectId = button.getAttribute("data-project-id");
            const modalTitle = modal.querySelector(".modal-title");
            modalTitle.textContent = `Tasks for Project ID: ${projectId}`;
          });
        });
      });

      function filterTasksByProject() {
        const projectId = document.getElementById("projectDropdown").value;
        const tasksTableContainer = document.getElementById(
          "tasksTableContainer"
        );
        const tasksTableBody = document.getElementById("tasksTableBody");

        if (!projectId) {
          tasksTableContainer.classList.add("d-none");
          return;
        }
        tasksTableBody.innerHTML = "";
        fetch("{% url 'get-tasks' %}?project_id=" + projectId)
          .then((response) => response.json())
          .then((data) => {
            if (data.tasks.length > 0) {
              tasksTableContainer.classList.remove("d-none");
              data.tasks.forEach((task, index) => {
                const viewFilesButton =
                  task.status === "completed"
                    ? `
                    <button type="button"
                            class="btn btn-outline-info btn-sm"
                            data-bs-toggle="modal"
                            data-bs-target="#viewFilesModal"
                            data-task-id="${task.id}"
                            data-file-url="${task.file_url}"
                            data-file-name="${task.file_name}"
                            data-report-text="${task.report}"
                            data-feedback="#">
                      View Files
                    </button>`
                    : "";

                const approveButton =
                  task.status === "not_assigned"
                    ? `
                    <form action="/dashboard/tasks/approve-task/${task.id}/" method="POST" style="display: inline; margin: 0; padding: 0;">
                      {% csrf_token %}
                      <button type="submit" class="btn btn-success task-action-btn">Approve</button>
                    </form>`
                    : "";

                const row = `
                    <tr>
                      <td>${index + 1}</td>
                      <td>${task.name}</td>
                      <td>${task.assigned_to}</td>
                      <td>${task.assigned_from}</td>
                      <td>${task.time_spent || "0h 0m"}</td>
                      <td>
                        <span class="badge ${
                          task.status === "completed"
                            ? "bg-success"
                            : "bg-primary"
                        } rounded-pill">${task.status_display}</span>
                      </td>
                      <td>
                        ${approveButton}
                        <a href="/dashboard/tasks/delete-task/${projectId}/?task_id=${
                  task.id
                }" class="btn btn-danger task-action-btn" onclick="return confirm('Are you sure you want to delete this task?');">Delete</a>
                        ${viewFilesButton}
                      </td>
                    </tr>
                  `;
                tasksTableBody.innerHTML += row;
              });
            } else {
              tasksTableContainer.classList.remove("d-none");
              tasksTableBody.innerHTML = `
                  <tr>
                    <td colspan="7" class="text-center">No tasks found for this project.</td>
                  </tr>
                `;
            }
          })
          .catch((error) => {
            console.error("Error fetching tasks:", error);
          });
      }

      document.addEventListener("DOMContentLoaded", function () {
        var viewFilesModal = document.getElementById("viewFilesModal");
        if (viewFilesModal) {
          viewFilesModal.addEventListener("show.bs.modal", function (event) {
            var button = event.relatedTarget;
            var taskId = button.getAttribute("data-task-id");
            var fileUrl = button.getAttribute("data-file-url");
            var fileName = button.getAttribute("data-file-name");
            var reportText = button.getAttribute("data-report-text");
            var feedback = button.getAttribute("data-feedback") || "";
            var taskStatus = button
              .closest("tr")
              .querySelector("td:nth-child(7)")
              .textContent.trim();

            // Update file upload form
            var uploadFileForm =
              viewFilesModal.querySelector("#uploadFileForm");
            if (uploadFileForm) {
              uploadFileForm.action = `/dashboard/upload_task_file/${taskId}/`;
              uploadFileForm.querySelector("#fileTaskId").value = taskId;
              uploadFileForm.style.display =
                taskStatus === "completed" ? "none" : "block";
            }

            // Update report form
            var reportForm = viewFilesModal.querySelector(
              'form[action*="upload_task_report"]'
            );
            if (reportForm) {
              reportForm.action = `/dashboard/upload_task_report/${taskId}/`;
              reportForm.querySelector("#reportTaskId").value = taskId;
              reportForm.style.display =
                taskStatus === "completed" ? "none" : "block";
            }

            var fileDisplay = viewFilesModal.querySelector("#fileDisplay");
            var reportDisplay = viewFilesModal.querySelector("#reportDisplay");

            // Display file
            if (fileUrl && fileUrl !== "#") {
              fileDisplay.innerHTML = `
                <div class="mb-2">
                  <a href="/dashboard/download_task_file/${taskId}/" class="btn btn-outline-primary btn-sm">
                    <i class="fas fa-file"></i> ${fileName || "Download File"}
                  </a>
                </div>`;
            } else {
              fileDisplay.innerHTML =
                '<p class="text-muted">No file uploaded yet</p>';
            }

            // Display report
            if (reportText && reportText.trim() !== "") {
              reportDisplay.innerHTML = `
                <div class="border p-3 mb-3">
                  ${reportText}
                </div>`;
            } else {
              reportDisplay.innerHTML =
                '<p class="text-muted">No report submitted yet</p>';
            }
          });
        }

        // Dashboard tasks filter function
        window.filterTasksByProject = function () {
          const projectId = document.getElementById("projectDropdown")?.value;
          const tasksTableContainer = document.getElementById(
            "tasksTableContainer"
          );
          const tasksTableBody = document.getElementById("tasksTableBody");

          if (!projectId || !tasksTableContainer || !tasksTableBody) {
            return;
          }

          if (!projectId) {
            tasksTableContainer.classList.add("d-none");
            return;
          }

          tasksTableBody.innerHTML = "";
          fetch("/dashboard/tasks/get-tasks/?project_id=" + projectId)
            .then((response) => response.json())
            .then((data) => {
              if (data.tasks.length > 0) {
                tasksTableContainer.classList.remove("d-none");
                data.tasks.forEach((task, index) => {
                  const viewFilesButton =
                    task.status === "completed"
                      ? `
                    <button type="button"
                            class="btn btn-outline-info btn-sm"
                            data-bs-toggle="modal"
                            data-bs-target="#viewFilesModal"
                            data-task-id="${task.id}"
                            data-file-url="${task.file_url}"
                            data-file-name="${task.file_name}"
                            data-report-text="${task.report}"
                            data-feedback="#">
                      View Files
                    </button>`
                      : "";

                  const approveButton =
                    task.status === "not_assigned"
                      ? `
                    <form action="/dashboard/tasks/approve-task/${task.id}/" method="POST" style="display: inline; margin: 0; padding: 0;">
                      {% csrf_token %}
                      <button type="submit" class="btn btn-success task-action-btn">Approve</button>
                    </form>`
                      : "";

                  const row = `
                    <tr>
                      <td>${index + 1}</td>
                      <td>${task.name}</td>
                      <td>${task.assigned_to}</td>
                      <td>${task.assigned_from}</td>
                      <td>${task.time_spent || "0h 0m"}</td>
                      <td>
                        <span class="badge ${
                          task.status === "completed"
                            ? "bg-success"
                            : "bg-primary"
                        } rounded-pill">${task.status_display}</span>
                      </td>
                      <td>
                        ${approveButton}
                        <a href="/dashboard/tasks/delete-task/${projectId}/?task_id=${
                    task.id
                  }" class="btn btn-danger task-action-btn" onclick="return confirm('Are you sure you want to delete this task?');">Delete</a>
                        ${viewFilesButton}
                      </td>
                    </tr>
                  `;
                  tasksTableBody.innerHTML += row;
                });
              } else {
                tasksTableContainer.classList.remove("d-none");
                tasksTableBody.innerHTML = `
                  <tr>
                    <td colspan="7" class="text-center">No tasks found for this project.</td>
                  </tr>
                `;
              }
            })
            .catch((error) => {
              console.error("Error fetching tasks:", error);
            });
        };
      });

      document.addEventListener("DOMContentLoaded", function () {
        var uploadFileForm = document.getElementById("uploadFileForm");
        if (uploadFileForm) {
          uploadFileForm.addEventListener("submit", function (event) {
            // Let the form submit normally - Django will handle the redirect and messages
            return true;
          });
        }
      });
