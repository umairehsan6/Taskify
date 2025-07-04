function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("createTaskModal");
  if (modal) {
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
  }
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
          const actionButtons = getAdminActionButtons(task, projectId);
          const row = `
              <tr>
                <td>${index + 1}</td>
                <td>${task.task_name}</td>
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
                  ${actionButtons}
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
            const actionButtons = getAdminActionButtons(task, projectId);
            const row = `
              <tr>
                <td>${index + 1}</td>
                <td>${task.task_name}</td>
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
                  ${actionButtons}
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

// document.querySelectorAll('.update-status-btn').forEach(function(button) {
//   button.addEventListener('click', function(e) {
//     e.preventDefault();
//     const projectId = this.getAttribute('data-project-id');
//     const newStatus = this.getAttribute('data-new-status');
//     const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

//     fetch(`/dashboard/update_project_status/${projectId}/${newStatus}/`, {
//       method: 'POST',
//       headers: {
//         'X-Requested-With': 'XMLHttpRequest',
//         'X-CSRFToken': csrfToken
//       }
//     })
//     .then(response => response.json())
//     .then(data => {
//       if (data.success) {
//         alert(data.message);
//         // Optionally update the status in the UI
//         // document.getElementById(`status-${projectId}`).textContent = data.new_status;
//       } else {
//         alert(data.error || 'Failed to update status.');
//       }
//     })
//     .catch(error => {
//       alert('An error occurred: ' + error);
//     });
//   });
// });
document.querySelectorAll('.update-status-btn').forEach(function(button) {
  button.addEventListener('click', function(e) {
      e.preventDefault();
      const projectId = this.getAttribute('data-project-id');
      const newStatus = this.getAttribute('data-new-status');
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
      fetch(`/dashboard/update-project-status/${projectId}/${newStatus}/`, {
          method: 'POST',
          headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'X-CSRFToken': csrfToken
          }
      })
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              // Update the badge text and color
              const badge = document.getElementById(`status-badge-${projectId}`);
              if (badge) {
                  badge.textContent = data.new_status;
                  badge.classList.remove('bg-warning', 'bg-primary', 'bg-success', 'bg-danger');
                  switch (newStatus) {
                      case 'pending':
                          badge.classList.add('bg-warning');
                          break;
                      case 'ongoing':
                          badge.classList.add('bg-primary');
                          break;
                      case 'completed':
                          badge.classList.add('bg-success');
                          break;
                      case 'on_hold':
                          badge.classList.add('bg-warning');
                          break;
                      case 'cancelled':
                          badge.classList.add('bg-danger');
                          break;
                  }
              }
          } else {
              alert(data.error || 'Failed to update status.');
          }
      })
      .catch(error => {
          alert('An error occurred: ' + error);
      });
  });
});

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.assign-task-link').forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const projectId = this.getAttribute('data-project-id');
            let projectName = '';
            const row = this.closest('tr');
            if (row) {
                const nameCell = row.querySelector('td:nth-child(2)');
                if (nameCell) {
                    projectName = nameCell.textContent.trim();
                }
            }
            const modal = document.getElementById('createTaskModal');
            const projectIdInput = modal.querySelector('input[name="project_id"]');
            const projectNameInput = modal.querySelector('input[name="project_name"]');
            if (projectIdInput) projectIdInput.value = projectId;
            if (projectNameInput && projectName) projectNameInput.value = projectName;

            // Fetch employees for the selected project and populate the dropdown
            const employeeSelect = modal.querySelector('select[name="assigned_to"]');
            if (employeeSelect) {
                employeeSelect.innerHTML = '<option value="">Select User</option>';
                console.log('Fetching employees for project:', projectId);
                fetch(`/dashboard/get-project-employees/${projectId}/`)
                    .then(response => response.json())
                    .then(data => {
                        console.log('Received employees:', data.employees);
                        data.employees.forEach(emp => {
                            const option = document.createElement('option');
                            option.value = emp.id;
                            option.textContent = emp.name;
                            employeeSelect.appendChild(option);
                        });
                    });
            }
            var bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        });
    });
});

// AJAX for admin create task form (similar to teamlead panel)
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('createTaskForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]')?.value;
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => { throw data; });
            }
            return response.json();
        })
        .then(data => {
            // Show success message (use Bootstrap alert or custom)
            let msg = document.getElementById('createTaskMessage');
            if (!msg) {
                msg = document.createElement('div');
                msg.id = 'createTaskMessage';
                msg.className = 'alert alert-success';
                msg.textContent = 'Task created successfully!';
                form.prepend(msg);
            } else {
                msg.className = 'alert alert-success';
                msg.textContent = 'Task created successfully!';
                msg.classList.remove('d-none');
            }
            // Reset form fields
            form.reset();
            // Hide message after 3 seconds
            setTimeout(() => {
                msg.classList.add('d-none');
            }, 3000);
            // Optionally close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createTaskModal'));
            if (modal) {
                setTimeout(() => modal.hide(), 1000);
            }
            // Optionally refresh the project/task list here
        })
        .catch(error => {
            const errorMessage = error.error || error.message || 'Could not create task.';
            alert('Error: ' + errorMessage);
            console.error('Form submission error:', error);
        });
    });
});

// Helper function for action buttons
function getAdminActionButtons(task, projectId) {
    let buttons = '';
    if (task.status === 'not_assigned') {
        buttons += `
            <button type="button" class="btn btn-success btn-sm approve-task-btn" data-task-id="${task.id}">Approve</button>`;
    }
    buttons += `
        <button type="button" class="btn btn-danger btn-sm delete-task-btn" data-task-id="${task.id}" data-project-id="${projectId}">Delete</button>`;
    if (task.status === 'completed') {
        buttons += `
            <button type="button"
                    class="btn btn-outline-info btn-sm"
                    data-bs-toggle="modal"
                    data-bs-target="#viewFilesModal"
                    data-task-id="${task.id}"
                    data-file-url="${task.file_url}"
                    data-file-name="${task.file_name}"
                    data-report-text="${task.report}">
                View Files
            </button>`;
    }
    return buttons;
}

console.log('Script loaded');
function adminFilterTasksByProject() {
    const projectDropdown = document.getElementById('projectDropdown');
    const getTasksUrl = projectDropdown.getAttribute('data-get-tasks-url');
    const projectId = projectDropdown.value;
    const tasksTableContainer = document.getElementById('tasksTableContainer');
    const tasksTableBody = document.getElementById('tasksTableBody');

    if (!projectId) {
        tasksTableContainer.classList.add('d-none');
        return;
    }

    tasksTableBody.innerHTML = '';
    fetch(getTasksUrl + '?project_id=' + projectId)
        .then(response => response.json())
        .then(data => {
            if (data.tasks.length > 0) {
                tasksTableContainer.classList.remove('d-none');
                data.tasks.forEach((task, index) => {
                    const statusClass = task.status === 'completed' ? 'bg-success' :
                                      task.status === 'in_progress' ? 'bg-primary' :
                                      task.status === 'on_hold' ? 'bg-warning' : 'bg-secondary';

                    const actionButtons = getAdminActionButtons(task, projectId);

                    const row = `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${task.task_name}</td>
                            <td>${task.assigned_to}</td>
                            <td>${task.assigned_from}</td>
                            <td>${task.time_spent || '0h 0m'}</td>
                            <td><span class="badge ${statusClass} rounded-pill">${task.status_display}</span></td>
                            <td>${actionButtons}</td>
                        </tr>
                    `;
                    tasksTableBody.innerHTML += row;
                });
            } else {
                tasksTableContainer.classList.remove('d-none');
                tasksTableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center">No tasks found for this project.</td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching tasks:', error);
            tasksTableContainer.classList.remove('d-none');
            tasksTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-danger">Error loading tasks. Please try again.</td>
                </tr>
            `;
        });
}

function getAdminActionButtons(task, projectId) {
    let buttons = '';
    if (task.status === 'not_assigned') {
        buttons += `
            <button type="button" class="btn btn-success btn-sm approve-task-btn" data-task-id="${task.id}">Approve</button>`;
    }
    buttons += `
        <button type="button" class="btn btn-danger btn-sm delete-task-btn" data-task-id="${task.id}" data-project-id="${projectId}">Delete</button>`;
    if (task.status === 'completed') {
        buttons += `
            <button type="button"
                    class="btn btn-outline-info btn-sm"
                    data-bs-toggle="modal"
                    data-bs-target="#viewFilesModal"
                    data-task-id="${task.id}"
                    data-file-url="${task.file_url}"
                    data-file-name="${task.file_name}"
                    data-report-text="${task.report}">
                View Files
            </button>`;
    }
    return buttons;
}

// Initialize modal functionality
document.addEventListener('DOMContentLoaded', function() {
    const viewFilesModal = document.getElementById('viewFilesModal');
    if (viewFilesModal) {
        viewFilesModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const taskId = button.getAttribute('data-task-id');
            const fileUrl = button.getAttribute('data-file-url');
            const fileName = button.getAttribute('data-file-name');
            const reportText = button.getAttribute('data-report-text');

            const fileDisplay = viewFilesModal.querySelector('#fileDisplay');
            const reportDisplay = viewFilesModal.querySelector('#reportDisplay');

            if (fileUrl && fileUrl !== '#') {
                fileDisplay.innerHTML = `
                    <div class="mb-2">
                        <a href="${fileUrl}" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-file"></i> ${fileName}
                        </a>
                    </div>`;
            } else {
                fileDisplay.innerHTML = '<p class="text-muted">No file uploaded</p>';
            }

            if (reportText) {
                reportDisplay.innerHTML = `
                    <div class="border p-3 mb-3">
                        ${reportText}
                    </div>`;
            } else {
                reportDisplay.innerHTML = '<p class="text-muted">No report submitted</p>';
            }
        });
    }

    document.getElementById('tasksTableBody').addEventListener('click', function(e) {
        // Approve button
        const approveBtn = e.target.closest('.approve-task-btn');
        if (approveBtn) {
            e.preventDefault();
            const taskId = approveBtn.getAttribute('data-task-id');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            fetch(`/dashboard/approve-task/${taskId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update status badge and remove Approve button
                    const row = approveBtn.closest('tr');
                    if (row) {
                        const statusCell = row.querySelector('td:nth-child(6) .badge');
                        if (statusCell) {
                            statusCell.textContent = data.status_display || 'Approved';
                            statusCell.classList.remove('bg-primary', 'bg-warning', 'bg-secondary');
                            statusCell.classList.add('bg-success');
                        }
                        approveBtn.remove();
                    }
                } else {
                    alert(data.error || 'Could not approve task.');
                }
            })
            .catch(() => {
                alert('Error approving task.');
            });
            return;
        }
        // ... existing delete handler ...
        const btn = e.target.closest('.delete-task-btn');
        if (btn) {
            console.log('Delete button clicked');
            e.preventDefault();
            const taskId = btn.getAttribute('data-task-id');
            const projectId = btn.getAttribute('data-project-id');
            if (confirm('Are you sure you want to delete this task?')) {
                fetch(`/dashboard/delete-task/${projectId}/?task_id=${taskId}`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': (document.querySelector('[name=csrfmiddlewaretoken]') || {}).value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        btn.closest('tr').remove();
                    } else {
                        alert('Error: ' + (data.error || 'Could not delete task.'));
                    }
                })
                .catch(() => {
                    alert('Error deleting task.');
                });
            }
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const userTable = document.querySelector('table');
    if (!userTable) return;
    userTable.addEventListener('click', function(e) {
        // Promote User
        const promoteBtn = e.target.closest('.promote-user-btn');
        if (promoteBtn) {
            e.preventDefault();
            const userId = promoteBtn.getAttribute('data-user-id');
            const roleValue = promoteBtn.getAttribute('data-role-value');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            fetch(`/promote-user/${userId}/${roleValue}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update role cell in the row
                    const row = promoteBtn.closest('tr');
                    if (row) {
                        const roleCell = row.querySelector('td:nth-child(6)');
                        if (roleCell) roleCell.textContent = data.new_role || roleValue;
                    }
                } else {
                    alert(data.error || 'Could not promote user.');
                }
            })
            .catch(() => {
                alert('Error promoting user.');
            });
            return;
        }
        // Assign Department
        const assignBtn = e.target.closest('.assign-department-btn');
        if (assignBtn) {
            e.preventDefault();
            const userId = assignBtn.getAttribute('data-user-id');
            const deptId = assignBtn.getAttribute('data-dept-id');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            fetch(`/dashboard/assign-department/${userId}/${deptId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update department cell in the row
                    const row = assignBtn.closest('tr');
                    if (row) {
                        const deptCell = row.querySelector('td:nth-child(7)');
                        if (deptCell) deptCell.textContent = data.new_department || 'Assigned';
                    }
                } else {
                    alert(data.error || 'Could not assign department.');
                }
            })
            .catch(() => {
                alert('Error assigning department.');
            });
            return;
        }
        // Toggle Status
        const toggleBtn = e.target.closest('.toggle-status-btn');
        if (toggleBtn) {
            e.preventDefault();
            const userId = toggleBtn.getAttribute('data-user-id');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            fetch(`/toggle-status/${userId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update status badge and button
                    const row = toggleBtn.closest('tr');
                    if (row) {
                        const statusCell = row.querySelector('td:nth-child(8) .badge');
                        if (statusCell) {
                            statusCell.textContent = data.new_status_display || (data.is_active ? 'Active' : 'Disabled');
                            statusCell.classList.toggle('bg-success', data.is_active);
                            statusCell.classList.toggle('bg-danger', !data.is_active);
                        }
                        // Update button text and color
                        toggleBtn.textContent = data.is_active ? 'Disable' : 'Activate';
                        toggleBtn.classList.toggle('btn-success', !data.is_active);
                        toggleBtn.classList.toggle('btn-danger', data.is_active);
                    }
                } else {
                    alert(data.error || 'Could not toggle status.');
                }
            })
            .catch(() => {
                alert('Error toggling status.');
            });
            return;
        }
    });
});

// Admin Notification Dropdown Logic
function fetchAdminNotifications() {
    fetch('/dashboard/admin-notifications-json/', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        adminNotificationsCache = data.notifications || [];
        renderAdminNotifications(adminNotificationsCache);
    })
    .catch(error => {
        console.error('Error fetching admin notifications:', error);
    });
}

function renderAdminNotifications(notifications) {
    const badge = document.getElementById('adminNotificationBadge');
    const list = document.getElementById('adminNotificationList');
    let unreadCount = 0;
    list.innerHTML = '';
    if (!notifications.length) {
        list.innerHTML = '<li class="p-4 text-center text-muted" style="min-height: 60px;">No notifications</li>';
        badge.style.display = 'none';
        return;
    }
    // Only show the 3 most recent notifications
    const notificationsToShow = notifications.slice(0, 3);
    notificationsToShow.forEach(n => {
        if (!n.is_read) unreadCount++;
        list.innerHTML += `<li class="dropdown-item py-2 px-3" style="white-space: normal; word-break: break-word;">
            <p style="margin-bottom: 2px; white-space: normal; word-break: break-word;">${n.message} ${!n.is_read ? '<span class=\"badge bg-danger ms-2\">New</span>' : ''}</p>
            <p style="margin-bottom: 0; font-size: 0.95em;">${n.timestamp}</p>
        </li>`;
    });
    // Count ALL unread notifications for the badge
    const totalUnread = notifications.filter(n => !n.is_read).length;
    if (totalUnread > 0) {
        badge.textContent = totalUnread;
        badge.style.display = 'inline-block';
    } else {
        badge.style.display = 'none';
    }
    // Show a badge at 'See All' if there are more unread notifications not shown in the top 3
    const seeAllUnreadBadge = document.getElementById('adminSeeAllUnreadBadge');
    const unreadInDropdown = notificationsToShow.filter(n => !n.is_read).length;
    const remainingUnread = totalUnread - unreadInDropdown;
    if (seeAllUnreadBadge) {
        if (remainingUnread > 0) {
            seeAllUnreadBadge.textContent = '+' + remainingUnread;
            seeAllUnreadBadge.style.display = '';
        } else {
            seeAllUnreadBadge.style.display = 'none';
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('adminNotificationBell')) {
        fetchAdminNotifications();
        setInterval(fetchAdminNotifications, 10000);
        // Fetch notifications on bell click
        document.getElementById('adminNotificationBell').addEventListener('click', function() {
            fetchAdminNotifications();
        });
    }
});

// --- Admin Notification Dropdown Read Functionality ---
let adminNotificationsCache = null;

// Mark as read when admin dropdown closes (only top 3 shown)
async function markAdminNotificationsRead() {
    if (!adminNotificationsCache) await fetchAdminNotifications();
    // Only mark as read the notifications currently shown in the dropdown (top 3)
    const notificationsToShow = (adminNotificationsCache || []).slice(0, 3);
    const unreadToMark = notificationsToShow.filter(n => !n.is_read && n.id);
    if (unreadToMark.length > 0) {
        const ids = unreadToMark.map(n => n.id);
        console.log('[ADMIN] Marking as read notification IDs:', ids);
        const response = await fetch('/dashboard/mark-notifications-read/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
            body: JSON.stringify({ notification_ids: ids })
        });
        const data = await response.json();
        console.log('[ADMIN] Mark as read response:', data);
        // Update cache
        adminNotificationsCache = adminNotificationsCache.map(n => ids.includes(n.id) ? { ...n, is_read: true } : n);
        renderAdminNotifications(adminNotificationsCache);
    } else {
        console.log('[ADMIN] No unread notifications to mark as read.');
    }
}

// Mark as read and update badge when dropdown closes
const adminNotificationBell = document.getElementById('adminNotificationBell');
const adminNotificationDropdownMenu = document.getElementById('adminNotificationDropdown');

document.body.addEventListener('hidden.bs.dropdown', async function(e) {
    if (e.target && e.target.id === 'adminNotificationBell') {
        await markAdminNotificationsRead();
        // Immediately update badge after marking as read
        fetchAdminNotifications();
    }
});