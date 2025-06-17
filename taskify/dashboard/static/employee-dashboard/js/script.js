document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        new bootstrap.Modal(modal);
    });

    // Task Details Modal Logic
    const taskDetailsModal = document.getElementById('taskDetailsModal');
    if (taskDetailsModal) {
        taskDetailsModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button) return;

            // Add blur to the main content
            const mainContent = document.querySelector('.main-dashboard-content');
            if (mainContent) mainContent.classList.add('blurred');

            // Get task data from the button's data attributes
            const taskName = button.getAttribute('data-task-name');
            const taskProject = button.getAttribute('data-task-project');
            const taskPriority = button.getAttribute('data-task-priority');
            const taskStatus = button.getAttribute('data-task-status');
            const taskDueDate = button.getAttribute('data-task-due-date');
            const taskTimeSpent = button.getAttribute('data-task-time-spent');
            const taskDescription = button.getAttribute('data-task-description');

            // Get modal elements
            const modalTitle = taskDetailsModal.querySelector('#taskDetailsModalLabel');
            const modalTaskName = taskDetailsModal.querySelector('#modalTaskName');
            const modalProject = taskDetailsModal.querySelector('#modalProject');
            const modalPriority = taskDetailsModal.querySelector('#modalPriority');
            const modalTaskStatus = taskDetailsModal.querySelector('#modalTaskStatus');
            const modalTaskDueDate = taskDetailsModal.querySelector('#modalTaskDueDate');
            const modalTimeSpent = taskDetailsModal.querySelector('#modalTimeSpent');
            const modalTaskDescription = taskDetailsModal.querySelector('#modalTaskDescription');

            // Populate modal with task data
            if (modalTitle) modalTitle.textContent = `Task Details: ${taskName}`;
            if (modalTaskName) modalTaskName.textContent = taskName;
            if (modalProject) modalProject.textContent = taskProject;
            if (modalPriority) modalPriority.textContent = taskPriority;
            if (modalTaskStatus) modalTaskStatus.textContent = taskStatus;
            if (modalTaskDueDate) modalTaskDueDate.textContent = taskDueDate;
            if (modalTimeSpent) modalTimeSpent.textContent = taskTimeSpent;
            if (modalTaskDescription) modalTaskDescription.textContent = taskDescription;
        });

        taskDetailsModal.addEventListener('hidden.bs.modal', function () {
            const mainContent = document.querySelector('.main-dashboard-content');
            if (mainContent) mainContent.classList.remove('blurred');
        });
    }

    // Project Details Modal Logic
    const projectDetailsModal = document.getElementById('projectDetailsModal');
    if (projectDetailsModal) {
        projectDetailsModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button) return;

            // Add blur to the main content
            const mainContent = document.querySelector('.main-dashboard-content');
            if (mainContent) mainContent.classList.add('blurred');

            // Get project data from the button's data attributes
            const projectId = button.getAttribute('data-project-id');
            const projectName = button.getAttribute('data-project-name');
            const projectDepartment = button.getAttribute('data-project-department');
            const projectDueDate = button.getAttribute('data-project-due-date');
            const projectDescription = button.getAttribute('data-project-description');

            // Find the project card that contains this button
            const projectCard = button.closest('.project-summary-card');
            const projectStatus = projectCard ? projectCard.querySelector('.badge').textContent : '';

            // Get modal elements
            const modalTitle = projectDetailsModal.querySelector('#projectDetailsModalLabel');
            const modalProjectName = projectDetailsModal.querySelector('#modalProjectName');
            const modalDepartment = projectDetailsModal.querySelector('#modalDepartment');
            const modalDueDate = projectDetailsModal.querySelector('#modalDueDate');
            const modalStatus = projectDetailsModal.querySelector('#modalStatus');
            const modalDescription = projectDetailsModal.querySelector('#modalDescription');

            // Populate modal with project data
            if (modalTitle) modalTitle.textContent = `Project Details: ${projectName}`;
            if (modalProjectName) modalProjectName.textContent = projectName;
            if (modalDepartment) modalDepartment.textContent = projectDepartment;
            if (modalDueDate) modalDueDate.textContent = projectDueDate;
            if (modalStatus) modalStatus.textContent = projectStatus;
            if (modalDescription) modalDescription.textContent = projectDescription;
        });

        projectDetailsModal.addEventListener('hidden.bs.modal', function () {
            const mainContent = document.querySelector('.main-dashboard-content');
            if (mainContent) mainContent.classList.remove('blurred');
        });
    }

    // Initialize task time tracking
    const taskTimeElements = document.querySelectorAll('.task-time');
    taskTimeElements.forEach(element => {
        const startTime = element.dataset.startTime;
        if (startTime) {
            updateTaskTime(element, startTime);
            setInterval(() => updateTaskTime(element, startTime), 1000);
        }
    });

    // Initialize task status updates
    const taskStatusButtons = document.querySelectorAll('[data-task-status]');
    taskStatusButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default button behavior
            const taskId = this.dataset.taskId;
            const newStatus = this.dataset.taskStatus;
            if (taskId && newStatus) {  // Only update if both values exist
                updateTaskStatus(taskId, newStatus);
            }
        });
    });

    // Initialize file upload functionality
    const fileUploadButtons = document.querySelectorAll('[data-bs-target="#viewFilesModal"]');
    fileUploadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default button behavior
            const taskId = this.dataset.taskId;
            const fileUrl = this.dataset.fileUrl;
            const fileName = this.dataset.fileName;
            const reportText = this.dataset.reportText;
            const taskStatus = this.dataset.taskStatus;
            
            // Update modal content
            document.getElementById('taskId').value = taskId;
            document.getElementById('currentFileName').textContent = fileName || 'No file uploaded';
            document.getElementById('taskReport').value = reportText || '';
            
            // Show/hide appropriate buttons based on task status
            const submitButton = document.getElementById('submitFilesBtn');
            const viewButton = document.getElementById('viewFilesBtn');
            if (taskStatus === 'completed') {
                submitButton.style.display = 'none';
                viewButton.style.display = 'block';
            } else {
                submitButton.style.display = 'block';
                viewButton.style.display = 'none';
            }
        });
    });

function updateTaskTime(element, startTime) {
    const start = new Date(startTime);
    const now = new Date();
    const diff = now - start;
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    element.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function updateTaskStatus(taskId, newStatus) {
    fetch(`/update-task-status/${taskId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error updating task status');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating task status');
    });
}

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

// Function to update the time display
function updateTimeDisplay() {
    const timeElement = document.getElementById('totalTimeToday');
    if (!timeElement) return;

    // Get the current time string
    const currentTime = timeElement.textContent;
    
    // Parse the time string (format: "Xh Ym Zs")
    const match = currentTime.match(/(\d+)h\s+(\d+)m\s+(\d+)s/);
    if (!match) return;

    let [_, hours, minutes, seconds] = match.map(Number);
    
    // Increment seconds
    seconds++;
    if (seconds >= 60) {
        seconds = 0;
        minutes++;
        if (minutes >= 60) {
            minutes = 0;
            hours++;
        }
    }

    // Update the display
    timeElement.textContent = `${hours}h ${minutes}m ${seconds}s`;
}

// Function to check if there are any in-progress tasks
function hasInProgressTasks() {
    const ongoingTasks = document.querySelectorAll('.ongoing-task-item');
    for (const task of ongoingTasks) {
        const statusElement = task.querySelector('.task-meta strong');
        if (statusElement && statusElement.textContent === 'In Progress') {
            return true;
        }
    }
    return false;
}

// Update time every second if there are in-progress tasks
setInterval(function() {
    if (hasInProgressTasks()) {
        updateTimeDisplay();
    }
}, 1000);

// Update time when starting/stopping tasks
document.addEventListener('DOMContentLoaded', function() {
    const startButtons = document.querySelectorAll('[data-action="start"]');
    const stopButtons = document.querySelectorAll('[data-action="stop"]');

    startButtons.forEach(button => {
        button.addEventListener('click', () => {
            setTimeout(updateTimeDisplay, 1000);
        });
    });

    stopButtons.forEach(button => {
        button.addEventListener('click', () => {
            setTimeout(updateTimeDisplay, 1000);
        });
    });
});

// Project Tasks Modal Logic
const projectTasksModal = document.getElementById('projectTasksModal');
if (projectTasksModal) {
    projectTasksModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        if (!button) return;

        const projectId = button.getAttribute('data-project-id');
        const projectName = button.getAttribute('data-project-name');

        // Update modal title
        const modalTitle = projectTasksModal.querySelector('#projectTasksModalLabel');
        if (modalTitle) modalTitle.textContent = `Tasks - ${projectName}`;

        // Show loading state
        const container = document.getElementById('projectTasksContainer');
        container.innerHTML = '<div class="col-12"><p class="text-center">Loading tasks...</p></div>';

        // Get CSRF token from cookie
        const csrftoken = getCookie('csrftoken');

        // Fetch tasks for this project
        fetch(`/dashboard/get-project-tasks/${projectId}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrftoken,
                'Accept': 'application/json'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            container.innerHTML = ''; // Clear loading state

            if (data.tasks && data.tasks.length > 0) {
                data.tasks.forEach(task => {
                    const priorityClass = task.priority === 'high' ? 'bg-danger' : 
                                        task.priority === 'medium' ? 'bg-warning' : 
                                        'bg-success';
                    const taskCard = `
                        <div class="col-12 mb-3">
                            <div class="task-card card p-3" data-priority="${task.priority}" data-task-id="${task.id}">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div class="flex-grow-1">
                                        <h6 class="fw-semibold mb-2">${task.task_name}</h6>
                                        <p class="text-secondary mb-2">${task.task_description}</p>
                                        <div class="d-flex gap-2 mb-2">
                                            <span class="badge 
                                                ${task.status === 'in_progress' ? 'bg-success' : 
                                                  task.status === 'completed' ? 'bg-primary' : 
                                                  task.status === 'on_hold' ? 'bg-warning' : 
                                                  'bg-secondary'}">
                                                ${task.status_display}
                                            </span>
                                            <span class="badge ${priorityClass}">
                                                ${task.priority.charAt(0).toUpperCase() + task.priority.slice(1)} Priority
                                            </span>
                                        </div>
                                        <div class="d-flex gap-3 mb-2">
                                            <p class="text-muted mb-0">
                                                <i class="fa fa-user me-1"></i>
                                                Assigned to: ${task.assigned_to}
                                            </p>
                                            <p class="text-muted mb-0">
                                                <i class="fa fa-clock me-1"></i>
                                                Time spent: ${task.time_spent || '0h 0m 0s'}
                                            </p>
                                        </div>
                                        ${task.report ? `<p class="text-muted mt-2 mb-0">Report: ${task.report}</p>` : ''}
                                        ${task.file_url ? 
                                        `<p class="text-muted mt-2 mb-0">
                                            File Url: 
                                            <a href="${task.file_url}" class="btn btn-outline-primary btn-sm ms-2" download>
                                                <i class="fas fa-file-download"></i> ${task.file_name}
                                            </a>
                                        </p>` 
                                        : ''
                                    }
                                    </div>
                                    <div class="task-card-buttons2 d-flex ms-3">
                                        <div class="position-relative">
                                            <button class="task-action-btn" data-bs-toggle="modal" data-bs-target="#commentsModal" data-task-id="${task.id}">
                                                <i class="fa fa-comments"></i>
                                                <span>Comments</span>
                                            </button>
                                        </div>
                                        <button class="task-action-btn" onclick="deleteTask(${task.id})">
                                            <i class="fa fa-trash"></i>
                                            <span>Delete</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    container.innerHTML += taskCard;
                });

                // Add event listeners to the newly created comment buttons
                container.querySelectorAll('[data-bs-target="#commentsModal"]').forEach(button => {
                    button.addEventListener('click', function() {
                        const taskId = this.dataset.taskId;
                        const commentsList = document.getElementById('commentsList');
                        const modalTaskIdInput = document.getElementById('taskId');
                        modalTaskIdInput.value = taskId;

                        // Clear existing comments
                        commentsList.innerHTML = '';

                        // Connect WebSocket for this task
                        connectWebSocket(taskId);

                        // Hide indicator for this task
                        const parentDiv = this.closest('.position-relative');
                        const indicator = parentDiv ? parentDiv.querySelector('.message-indicator') : null;
                        if (indicator) {
                            indicator.style.display = 'none';
                        }
                    });
                });
            } else {
                container.innerHTML = '<div class="col-12"><p class="text-center">No tasks found for this project.</p></div>';
            }
        })
        .catch(error => {
            console.error('Error fetching tasks:', error);
            container.innerHTML = `<div class="col-12"><p class="text-center text-danger">Error loading tasks: ${error.message}</p></div>`;
        });
    });
}

// Function to change task priority
function changeTaskPriority(taskId) {
    // Implement priority change logic
    console.log('Change priority for task:', taskId);
}

// Function to delete task
function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        fetch(`/delete-task/${taskId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove the task card from the modal
                const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
                if (taskCard) {
                    taskCard.remove();
                }
            } else {
                alert('Error deleting task');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting task');
        });
    }
}

// Handle comment form submission
const commentForm = document.getElementById('commentForm');
if (commentForm) {
    commentForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const taskId = document.getElementById('taskId').value;
        const messageInput = document.getElementById('messageInput');
        const messageText = messageInput.value.trim();

        if (!messageText) {
            console.log('Attempted to send empty message.');
            return;
        }

        if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            try {
                chatSocket.send(JSON.stringify({
                    'message': messageText,
                    'task_id': taskId
                }));
                messageInput.value = ''; // Clear input field immediately
                console.log('Message sent via WebSocket.');
            } catch (error) {
                console.error('Error sending message:', error);
                alert('Error sending message. Please try again.');
            }
        } else {
            console.error('WebSocket is not open. Cannot send message.');
            alert('Cannot send message. WebSocket connection not established.');
        }
    });
}

// Initialize comments functionality for modal trigger buttons
const commentButtons = document.querySelectorAll('[data-bs-target="#commentsModal"]');
commentButtons.forEach(button => {
    button.addEventListener('click', function() {
        const taskId = this.dataset.taskId;
        const commentsList = document.getElementById('commentsList');
        const modalTaskIdInput = document.getElementById('taskId');
        modalTaskIdInput.value = taskId; // Set the task ID in the hidden input

        // Clear existing comments before connecting WebSocket
        commentsList.innerHTML = '';

        // Connect WebSocket for the specific task
        connectWebSocket(taskId);

        // Historical messages will be sent by the consumer upon connection.
    });
});

// Handle modal close to disconnect WebSocket
const commentsModal = document.getElementById('commentsModal');
if (commentsModal) {
    commentsModal.addEventListener('hidden.bs.modal', function() {
        if (chatSocket) {
            chatSocket.close();
            chatSocket = null;
            console.log('WebSocket disconnected due to modal close.');
        }
    });
}

let chatSocket = null;

function connectWebSocket(taskId) {
    // Close existing socket if it exists
    if (chatSocket) {
        chatSocket.close();
        chatSocket = null;
    }

    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const ws_path = `/ws/comments/${taskId}/`;
    
    console.log(`Connecting to WebSocket at ${ws_scheme}://${window.location.host}${ws_path}`);
    
    chatSocket = new WebSocket(
        `${ws_scheme}://${window.location.host}${ws_path}`
    );

    chatSocket.onopen = function(e) {
        console.log('WebSocket connection established');
        const commentsList = document.getElementById('commentsList');
        commentsList.innerHTML = ''; // Clear comments before receiving from socket
        const anchor = document.createElement('div');
        anchor.id = 'comments-bottom-anchor';
        commentsList.appendChild(anchor);
    };

    chatSocket.onmessage = function(e) {
        console.log('Received message:', e.data);
        const data = JSON.parse(e.data);
        if (data.error) {
            console.error('WebSocket error:', data.error);
            return;
        }

        const commentsList = document.getElementById('commentsList');
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-3 ${data.is_current_user ? 'bg-dark text-white message-right' : 'bg-secondary text-black message-left'}`;
        messageDiv.innerHTML = `
            <div class="d-flex align-items-center mb-1">
                <span class="fw-semibold me-2">${data.username}</span>
                <span class="text-muted small">${data.timestamp}</span>
            </div>
            <div class="p-2">
                ${data.message}
            </div>
        `;
        
        const anchor = document.getElementById('comments-bottom-anchor');
        if (anchor) {
            commentsList.insertBefore(messageDiv, anchor);
        } else {
            commentsList.appendChild(messageDiv);
        }

        // Scroll to bottom after new message is appended
        setTimeout(() => {
            scrollCommentsToBottom();
        }, 100);
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly:', e);
    };

    chatSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };

    return chatSocket;
}

function sendMessage(taskId, message) {
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        console.log('Sending message:', message);
        chatSocket.send(JSON.stringify({
            'message': message,
            'task_id': taskId
        }));
    } else {
        console.error('WebSocket is not connected');
    }
}

// Function to update task indicator
function updateTaskIndicator(taskId, hasUnread) {
    // Find all Comments buttons for this task (both in ongoing tasks and modal)
    const commentButtons = document.querySelectorAll(`[data-task-id="${taskId}"][data-bs-target="#commentsModal"]`);
    commentButtons.forEach(button => {
        const parentDiv = button.closest('.position-relative');
        if (!parentDiv) {
            const newParent = document.createElement('div');
            newParent.className = 'position-relative';
            button.parentNode.insertBefore(newParent, button);
            newParent.appendChild(button);
        }
        
        let indicator = parentDiv ? parentDiv.querySelector('.message-indicator') : null;
        if (hasUnread) {
            if (!indicator) {
                indicator = document.createElement('span');
                indicator.className = 'message-indicator';
                if (parentDiv) {
                    parentDiv.appendChild(indicator);
                } else {
                    button.appendChild(indicator);
                }
            }
            indicator.style.display = 'block';
        } else {
            if (indicator) {
                indicator.style.display = 'none';
            }
        }
    });
}
}); // Closing brace for DOMContentLoaded

// inbuild
document.addEventListener('DOMContentLoaded', function() {
    const viewFilesModal = document.getElementById('viewFilesModal');
    if (viewFilesModal) {
        viewFilesModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const taskId = button.getAttribute('data-task-id');
            const fileUrl = button.getAttribute('data-file-url');
            const fileName = button.getAttribute('data-file-name');
            const reportText = button.getAttribute('data-report-text');
            const taskStatus = button.getAttribute('data-task-status');

            // Update file display
            const fileLink = viewFilesModal.querySelector('.file-link');
            const fileNameSpan = viewFilesModal.querySelector('.file-name');
            if (fileUrl && fileUrl !== '#') {
                fileLink.href = `/dashboard/download_task_file/${taskId}/`;
                fileNameSpan.textContent = fileName;
                fileLink.style.display = 'inline-block';
            } else {
                fileLink.style.display = 'none';
            }

            // Update report display
            const reportContent = viewFilesModal.querySelector('.report-content');
            if (reportText) {
                reportContent.textContent = reportText;
                reportContent.style.display = 'block';
            } else {
                reportContent.style.display = 'none';
            }

            // Show/hide upload sections based on task status
            const uploadFileSection = document.getElementById('uploadFileSection');
            const uploadReportSection = document.getElementById('uploadReportSection');
            if (taskStatus === 'completed') {
                uploadFileSection.style.display = 'none';
                uploadReportSection.style.display = 'none';
            } else {
                uploadFileSection.style.display = 'block';
                uploadReportSection.style.display = 'block';
            }

            // Update form action URLs and task IDs
            const fileForm = document.getElementById('uploadFileForm');
            const reportForm = document.getElementById('uploadReportForm');
            
            // Get the base URL pattern from Django
            const baseUrl = "{% url 'upload_task_file' task_id=0 %}";
            const reportBaseUrl = "{% url 'upload_task_report' task_id=0 %}";
            
            // Replace the '0' with the actual task ID
            fileForm.action = baseUrl.replace('0', taskId);
            reportForm.action = reportBaseUrl.replace('0', taskId);
            
            document.getElementById('fileTaskId').value = taskId;
            document.getElementById('reportTaskId').value = taskId;
        });
    }
});
document.addEventListener('DOMContentLoaded', function() {
    // Global notification socket for real-time updates
    let notificationSocket = null;
    
    // Initialize notification socket
    function initializeNotificationSocket() {
        const socketProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const socketUrl = `${socketProtocol}//${window.location.host}/ws/notifications/`;
        
        if (notificationSocket) {
            notificationSocket.close();
        }
        
        notificationSocket = new WebSocket(socketUrl);

        notificationSocket.onopen = function(e) {
            console.log('Notification WebSocket connection opened');
        };

        notificationSocket.onmessage = function(e) {
            try {
                const data = JSON.parse(e.data);
                console.log('Received notification:', data);

                if (data.type === 'unread_notification') {
                    updateTaskIndicator(data.task_id, data.has_unread);
                }
            } catch (error) {
                console.error('Error parsing notification message:', error);
            }
        };

        notificationSocket.onclose = function(e) {
            console.log('Notification WebSocket connection closed');
            // Only attempt to reconnect if the close was not initiated by us
            if (e.code !== 1000) {
                setTimeout(initializeNotificationSocket, 5000);
            }
        };

        notificationSocket.onerror = function(e) {
            console.error('Notification WebSocket error:', e);
        };
    }

    // Function to update task indicator
    function updateTaskIndicator(taskId, hasUnread) {
        // Find all Comments buttons for this task
        const commentButtons = document.querySelectorAll(`[data-task-id="${taskId}"][data-bs-target="#commentsModal"]`);
        commentButtons.forEach(button => {
            // Look for indicator in the button's parent div (position-relative wrapper)
            const parentDiv = button.closest('.position-relative');
            let indicator = parentDiv ? parentDiv.querySelector('.message-indicator') : null;
            
            if (hasUnread) {
                if (!indicator) {
                    // Create new indicator if it doesn't exist
                    indicator = document.createElement('span');
                    indicator.className = 'message-indicator';
                    if (parentDiv) {
                        parentDiv.appendChild(indicator);
                    } else {
                    button.appendChild(indicator);
                }
                }
                indicator.style.display = 'block';
            } else {
                if (indicator) {
                    indicator.style.display = 'none';
                }
            }
        });
    }

    // Function to hide indicator for a specific task
    function hideTaskIndicator(taskId) {
        const commentButtons = document.querySelectorAll(`[data-task-id="${taskId}"][data-bs-target="#commentsModal"]`);
        commentButtons.forEach(button => {
            // Look for indicator in the button's parent div
            const parentDiv = button.closest('.position-relative');
            const indicator = parentDiv ? parentDiv.querySelector('.message-indicator') : button.querySelector('.message-indicator');
            if (indicator) {
                indicator.style.display = 'none';
            }
        });
    }

    // Initialize notification socket
    initializeNotificationSocket();

    // Reinitialize notification socket after successful login
    const loginForm = document.querySelector('form[action="/login/"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            // Wait for login to complete and page to reload
            setTimeout(initializeNotificationSocket, 1000);
        });
    }

    // Handle comments modal
    const commentsModal = document.getElementById('commentsModal');
    let commentSocket = null; // Declare socket variable globally within this scope

    if (commentsModal) {
        commentsModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const taskId = button.getAttribute('data-task-id');
            console.log('Opening comments modal for task:', taskId);
            
            // Hide all message indicators when modal opens
            const allIndicators = document.querySelectorAll('.message-indicator');
            allIndicators.forEach(indicator => {
                indicator.style.display = 'none';
            });
            
            // Store task ID in hidden input
            document.getElementById('taskId').value = taskId;
        });

        commentsModal.addEventListener('hide.bs.modal', function() {
            if (commentSocket && commentSocket.readyState === WebSocket.OPEN) {
                commentSocket.close();
            }
        });
    }

    // Clean up sockets when page unloads
    window.addEventListener('beforeunload', function() {
        if (commentSocket) {
            commentSocket.close();
        }
        if (notificationSocket) {
            notificationSocket.close();
        }
    });

    // Debug function - remove this after testing
    window.testIndicator = function(taskId) {
        console.log('Testing indicator for task:', taskId);
        updateTaskIndicator(taskId, true);
    };

    // Debug function to hide indicator - remove this after testing
    window.hideTestIndicator = function(taskId) {
        console.log('Hiding indicator for task:', taskId);
        hideTaskIndicator(taskId);
    };
});

// New function for reliable auto-scrolling
function scrollCommentsToBottom() {
    const commentsList = document.getElementById('commentsList');
    if (commentsList) {
        requestAnimationFrame(() => {
            console.log('Scrolling to bottom. scrollHeight:', commentsList.scrollHeight, 'clientHeight:', commentsList.clientHeight);
            commentsList.scrollTop = 999999; // Set to a very large number to ensure it goes to the very bottom
        });
    }
}