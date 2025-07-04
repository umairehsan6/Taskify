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

// --- WebSocket Chat Improvements ---
let chatSocket = null;
let chatSocketTaskId = null;
let chatSocketReconnectTimeout = null;
let chatSocketIntentionalClose = false; // NEW FLAG

function showChatError(message) {
    const commentsList = document.getElementById('commentsList');
    if (commentsList) {
        commentsList.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    }
}

function addReconnectButton(taskId) {
    const commentsList = document.getElementById('commentsList');
    if (commentsList) {
        const btn = document.createElement('button');
        btn.className = 'btn btn-warning mt-2';
        btn.textContent = 'Reconnect';
        btn.onclick = () => {
            showChatError('Reconnecting...');
            connectWebSocket(taskId, true);
        };
        commentsList.appendChild(btn);
    }
}

// Move scrollCommentsToBottom here so it is defined before use
function scrollCommentsToBottom() {
    const commentsList = document.getElementById('commentsList');
    if (commentsList) {
        requestAnimationFrame(() => {
            console.log('Scrolling to bottom. scrollHeight:', commentsList.scrollHeight, 'clientHeight:', commentsList.clientHeight);
            commentsList.scrollTop = 999999; // Set to a very large number to ensure it goes to the very bottom
        });
    }
}

function connectWebSocket(taskId, forceReconnect = false) {
    // Only reconnect if not already connected to this task
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN && chatSocketTaskId === taskId && !forceReconnect) {
        console.log('[WebSocket] Already connected to this task.');
        return chatSocket;
    }
    // Close previous socket if open
    if (chatSocket) {
        chatSocket.close();
        chatSocket = null;
        chatSocketTaskId = null;
    }
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const ws_path = `/ws/comments/${taskId}/`;
    const ws_url = `${ws_scheme}://${window.location.host}${ws_path}`;
    console.log(`[WebSocket] Connecting to: ${ws_url}`);
    chatSocket = new WebSocket(ws_url);
    chatSocketTaskId = taskId;

    chatSocket.onopen = function(e) {
        console.log('[WebSocket] Connection established');
        const commentsList = document.getElementById('commentsList');
        if (commentsList) commentsList.innerHTML = '';
        const anchor = document.createElement('div');
        anchor.id = 'comments-bottom-anchor';
        commentsList.appendChild(anchor);
    };

    chatSocket.onmessage = function(e) {
        console.log('[WebSocket] Received message:', e.data);
        const data = JSON.parse(e.data);
        if (data.error) {
            showChatError('WebSocket error: ' + data.error);
            addReconnectButton(taskId);
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
        setTimeout(() => {
            scrollCommentsToBottom();
        }, 100);
    };

    chatSocket.onclose = function(e) {
        if (chatSocketIntentionalClose) {
            chatSocketIntentionalClose = false; // reset for next time
            return; // Don't show reconnect UI
        }
        console.error('[WebSocket] Connection closed:', e);
        showChatError('Chat connection lost.');
        addReconnectButton(taskId);
        // Optionally, auto-reconnect after a delay
        if (!forceReconnect) {
            if (chatSocketReconnectTimeout) clearTimeout(chatSocketReconnectTimeout);
            chatSocketReconnectTimeout = setTimeout(() => connectWebSocket(taskId, true), 5000);
        }
    };

    chatSocket.onerror = function(e) {
        console.error('[WebSocket] Error:', e);
        showChatError('WebSocket error.');
        addReconnectButton(taskId);
    };
    return chatSocket;
}
window.connectWebSocket = connectWebSocket;

const csrftoken = getCookie('csrftoken');
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        new bootstrap.Modal(modal);
    });

    // Global flag to track if comments modal is open
    window.isCommentsModalOpen = false;

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
            console.log("Fetched data:", data); // <--- Add this line
            window.allProjectTasks = data.tasks || [];
            container.innerHTML = ''; // Clear loading state

            if (data.tasks && data.tasks.length > 0) {
                data.tasks.forEach(task => {
                    const priorityClass = task.priority === 'high' ? 'bg-danger' : 
                                        task.priority === 'medium' ? 'bg-warning' : 
                                        'bg-success';
                    
                    // Check if task has unread messages
                    const hasUnread = task.has_unread_messages || false;
                    
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
                                            ${hasUnread ? '<span class="message-indicator" style="display: block !important;"></span>' : ''}
                                        </div>
                                        ${['employee', 'teamlead', 'project_manager', 'admin'].includes(window.USER_ROLE) ? `
                                            <button class="btn btn-outline-danger task-action-btn"
                                                    type="button"
                                                    onclick="deleteTask(${task.id})">
                                                <i class="fa fa-trash"></i>
                                                <span>Delete</span>
                                            </button>
                                        ` : ''}
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
                        commentsList.innerHTML = '';
                        window.connectWebSocket(taskId);

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

// Function to delete task (for admin/employee)
// function deleteTask(taskId) {
//     console.log('[ADMIN/EMPLOYEE] Attempting to delete task:', taskId);
//     let url = `/delete-task/${taskId}/`;
//     fetch(url, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': getCookie('csrftoken'),
//             'X-Requested-With': 'XMLHttpRequest'
//         },
//         credentials: 'same-origin'
//     })
//     .then(response => response.json())
//     .then(data => {
//         console.log('Delete response:', data);
//         if (data.success) {
//             let taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
//             if (taskCard) {
//                 let cardToRemove = taskCard.closest('.task-card.card') || taskCard.closest('.task-card') || taskCard.closest('.col-12') || taskCard;
//                 cardToRemove.remove();
//             }
//         } else {
//             alert('Error deleting task: ' + (data.error || 'Unknown error'));
//         }
//     })
//     .catch(error => {
//         console.error('Error:', error);
//         alert('Error deleting task');
//     });
// }
// window.deleteTask = deleteTask;


// Function to delete/reject task as teamlead/project_manager/admin


// function deleteTaskTeamlead(taskId) {
//     console.log('[TEAMLEAD] Attempting to delete/reject task:', taskId);
//     let url = `/dashboard/teamlead/delete-task/${taskId}/`;
//     fetch(url, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': getCookie('csrftoken'),
//             'X-Requested-With': 'XMLHttpRequest'
//         },
//         credentials: 'same-origin'
//     })
//     .then(response => response.json())
//     .then(data => {
//         console.log('Teamlead delete response:', data);
//         if (data.success) {
//             let taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
//             if (taskCard) {
//                 let cardToRemove = taskCard.closest('.task-card.card') || taskCard.closest('.task-card') || taskCard.closest('.col-12') || taskCard;
//                 cardToRemove.remove();
//             }
//         } else {
//             alert('Error deleting task: ' + (data.error || 'Unknown error'));
//         }
//     })
//     .catch(error => {
//         console.error('Error:', error);
//         alert('Error deleting task');
//     });
// }
// window.deleteTaskTeamlead = deleteTaskTeamlead;

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

        if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) {
            alert('Chat connection is not open. Please try reconnecting.');
            return;
        }

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
        window.connectWebSocket(taskId);

        // Historical messages will be sent by the consumer upon connection.
    });
});

// Handle modal close to disconnect WebSocket
const commentsModal = document.getElementById('commentsModal');
if (commentsModal) {
    commentsModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const taskId = button.getAttribute('data-task-id');
        console.log('Opening comments modal for task:', taskId);
        
        // Set flag to prevent indicators from showing
        window.isCommentsModalOpen = true;
        console.log('Set isCommentsModalOpen to true');
        
        // Hide all message indicators when modal opens
        const allIndicators = document.querySelectorAll('.message-indicator');
        allIndicators.forEach(indicator => {
            indicator.style.display = 'none';
        });
        
        // Store task ID in hidden input
        document.getElementById('taskId').value = taskId;
        
        // Send modal open event to WebSocket
        if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify({
                'type': 'modal_open',
                'task_id': taskId
            }));
            console.log('Sent modal_open event to WebSocket');
        }
    });

    commentsModal.addEventListener('hide.bs.modal', function() {
        // Reset flag when modal closes
        window.isCommentsModalOpen = false;
        console.log('Set isCommentsModalOpen to false');
        
        // Send modal close event to WebSocket before closing
        if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            const taskId = document.getElementById('taskId').value;
            chatSocket.send(JSON.stringify({
                'type': 'modal_close',
                'task_id': taskId
            }));
            console.log('Sent modal_close event to WebSocket');
        }
        
        // Force hide all indicators when modal closes to prevent CSS conflicts
        const allIndicators = document.querySelectorAll('.message-indicator');
        allIndicators.forEach(indicator => {
            indicator.style.setProperty('display', 'none', 'important');
            indicator.style.setProperty('visibility', 'hidden', 'important');
            indicator.style.setProperty('opacity', '0', 'important');
            indicator.classList.remove('show', 'active');
            indicator.classList.add('hide');
        });
        console.log('Forced hide all indicators on modal close');
        
        // Close WebSocket after sending close event
        setTimeout(() => {
            if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
                chatSocket.close();
            }
        }, 100);
    });
}

// --- WebSocket Chat Improvements ---
let chatSocket = null;
let chatSocketTaskId = null;
let chatSocketReconnectTimeout = null;

function showChatError(message) {
    const commentsList = document.getElementById('commentsList');
    if (commentsList) {
        commentsList.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    }
}

function addReconnectButton(taskId) {
    const commentsList = document.getElementById('commentsList');
    if (commentsList) {
        const btn = document.createElement('button');
        btn.className = 'btn btn-warning mt-2';
        btn.textContent = 'Reconnect';
        btn.onclick = () => {
            showChatError('Reconnecting...');
            connectWebSocket(taskId, true);
        };
        commentsList.appendChild(btn);
    }
}

function connectWebSocket(taskId, forceReconnect = false) {
    // Only reconnect if not already connected to this task
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN && chatSocketTaskId === taskId && !forceReconnect) {
        console.log('[WebSocket] Already connected to this task.');
        return chatSocket;
    }
    // Close previous socket if open
    if (chatSocket) {
        chatSocket.close();
        chatSocket = null;
        chatSocketTaskId = null;
    }
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const ws_path = `/ws/comments/${taskId}/`;
    const ws_url = `${ws_scheme}://${window.location.host}${ws_path}`;
    console.log(`[WebSocket] Connecting to: ${ws_url}`);
    chatSocket = new WebSocket(ws_url);
    chatSocketTaskId = taskId;

    chatSocket.onopen = function(e) {
        console.log('[WebSocket] Connection established');
        const commentsList = document.getElementById('commentsList');
        if (commentsList) commentsList.innerHTML = '';
        const anchor = document.createElement('div');
        anchor.id = 'comments-bottom-anchor';
        commentsList.appendChild(anchor);
    };

    chatSocket.onmessage = function(e) {
        console.log('[WebSocket] Received message:', e.data);
        const data = JSON.parse(e.data);
        if (data.error) {
            showChatError('WebSocket error: ' + data.error);
            addReconnectButton(taskId);
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
        setTimeout(() => {
            scrollCommentsToBottom();
        }, 100);
    };

    chatSocket.onclose = function(e) {
        if (chatSocketIntentionalClose) {
            chatSocketIntentionalClose = false; // reset for next time
            return; // Don't show reconnect UI
        }
        console.error('[WebSocket] Connection closed:', e);
        showChatError('Chat connection lost.');
        addReconnectButton(taskId);
        // Optionally, auto-reconnect after a delay
        if (!forceReconnect) {
            if (chatSocketReconnectTimeout) clearTimeout(chatSocketReconnectTimeout);
            chatSocketReconnectTimeout = setTimeout(() => connectWebSocket(taskId, true), 5000);
        }
    };

    chatSocket.onerror = function(e) {
        console.error('[WebSocket] Error:', e);
        showChatError('WebSocket error.');
        addReconnectButton(taskId);
    };
    return chatSocket;
}
window.connectWebSocket = connectWebSocket;

// Prevent duplicate event listeners for comments modal
(function() {
    let lastTaskId = null;
    const commentsModal = document.getElementById('commentsModal');
    if (commentsModal) {
        commentsModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const taskId = button ? button.getAttribute('data-task-id') : null;
            if (!taskId) return;
            if (lastTaskId !== taskId) {
                lastTaskId = taskId;
                connectWebSocket(taskId, true);
            }
        });
        commentsModal.addEventListener('hide.bs.modal', function() {
            chatSocketIntentionalClose = true; // SET FLAG
            if (chatSocket) {
                chatSocket.close();
                chatSocket = null;
                chatSocketTaskId = null;
            }
        });
    }
})();

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

// Function to update project indicator
function updateProjectIndicator(projectId, hasUnread) {
    console.log(`=== UPDATING PROJECT INDICATOR ===`);
    console.log(`Project ID: ${projectId}, Has Unread: ${hasUnread}`);

    // Find ALL Show Tasks buttons for this project
    const showTasksButtons = document.querySelectorAll(`[data-project-id="${projectId}"][data-bs-target="#projectTasksModal"]`);
    console.log('Show Tasks buttons found:', showTasksButtons.length);

    showTasksButtons.forEach(showTasksButton => {
        let indicator = showTasksButton.querySelector('.message-indicator');
        if (hasUnread) {
            if (!indicator) {
                indicator = document.createElement('span');
                indicator.className = 'message-indicator';
                indicator.style.cssText = 'position: absolute; top: -8px; right: -8px; width: 12px; height: 12px; background-color: #ff3b30; border: 2px solid #fff; border-radius: 50%; display: block; z-index: 10; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); pointer-events: none;';
                showTasksButton.appendChild(indicator);
            }
            indicator.style.display = 'block';
            indicator.style.visibility = 'visible';
            indicator.style.opacity = '1';
            console.log(`✅ SHOWING project indicator for project ${projectId}`);
        } else {
            if (indicator) {
                indicator.style.display = 'none';
                indicator.style.visibility = 'hidden';
                indicator.style.opacity = '0';
                console.log(`✅ HIDING project indicator for project ${projectId}`);
            }
        }
    });

    if (showTasksButtons.length === 0) {
        console.log(`❌ Show Tasks button not found for project ${projectId}`);
    }
    console.log(`=== END PROJECT INDICATOR UPDATE ===`);
}
window.updateProjectIndicator = updateProjectIndicator;

// Make function globally accessible
window.updateProjectIndicator = updateProjectIndicator;

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

// inbuild
document.addEventListener('DOMContentLoaded', function() {
    const viewFilesModal = document.getElementById('viewFilesModal');
    if (viewFilesModal) {
        viewFilesModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            if (!button) return;
            const taskId = button.getAttribute('data-task-id');
            console.log('Opening modal for taskId:', taskId);
            
            // Update the uploadFileForm action in the modal
            const baseUrl = '/dashboard/upload_task_file/0/';
            const fileForm = viewFilesModal.querySelector('.uploadFileForm');
            if (fileForm) {
                fileForm.action = baseUrl.replace('0', taskId);
                console.log('Set fileForm.action to:', fileForm.action);
            } else {
                console.log('No .uploadFileForm found in modal!');
            }
            
            // Update the hidden input if needed
            const fileTaskIdInput = viewFilesModal.querySelector('#fileTaskId');
            if (fileTaskIdInput) {
                fileTaskIdInput.value = taskId;
                console.log('Set fileTaskIdInput.value to:', fileTaskIdInput.value);
            }
            
            // Update report form
            const reportForm = viewFilesModal.querySelector('.uploadReportForm');
            if (reportForm) {
                reportForm.action = `/dashboard/upload_task_report/${taskId}/`;
                console.log('Set reportForm.action to:', reportForm.action);
            } else {
                console.log('No .uploadReportForm found in modal!');
            }
            
            const reportTaskIdInput = viewFilesModal.querySelector('#reportTaskId');
            if (reportTaskIdInput) {
                reportTaskIdInput.value = taskId;
                console.log('Set reportTaskIdInput.value to:', reportTaskIdInput.value);
            }

            const reportDisplay = viewFilesModal.querySelector('#reportDisplay');
            if (reportDisplay) {
                console.log('About to fetch report for taskId:', taskId);
                reportDisplay.innerHTML = '<div class="border p-3 mb-3">Loading...</div>';
                fetch(`/dashboard/get-task-report/${taskId}/`)
                    .then(response => response.json())
                    .then(data => {
                        console.log('Fetched report for taskId:', taskId, 'Report:', data.report);
                        if (data.success) {
                            reportDisplay.innerHTML = `
                                <div class="border p-3 mb-3">
                                    ${data.report ? data.report : 'No report submitted'}
                                </div>`;
                        } else {
                            reportDisplay.innerHTML = `<div class="border p-3 mb-3 text-danger">Error loading report</div>`;
                        }
                    })
                    .catch(() => {
                        reportDisplay.innerHTML = `<div class="border p-3 mb-3 text-danger">Error loading report</div>`;
                    });
            }

            const fileDisplay = viewFilesModal.querySelector('#fileDisplay');
            if (fileDisplay) {
                fileDisplay.innerHTML = '<div class="mb-2">Loading file...</div>';
                fetch(`/dashboard/get-task-file/${taskId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && data.file_url) {
                            fileDisplay.innerHTML = `
                                <div class="mb-2">
                                    <a href="${data.file_url}" class="btn btn-outline-primary btn-sm file-link" download>
                                        <i class="fas fa-file"></i> <span class="file-name">${data.file_name}</span>
                                    </a>
                                </div>`;
                        } else {
                            fileDisplay.innerHTML = '<div class="mb-2">No file uploaded</div>';
                        }
                    })
                    .catch(() => {
                        fileDisplay.innerHTML = '<div class="mb-2 text-danger">Error loading file</div>';
                    });
            }
        });
    }
});

    // Global notification socket for real-time updates
    let notificationSocket = null;
let notificationQueue = [];
let isProcessingQueue = false;
let lastIndicatorUpdate = {}; // Track last update time for each indicator

// Debounce function to prevent rapid indicator updates
function debounceIndicatorUpdate(key, callback, delay = 1000) {
    const now = Date.now();
    const lastUpdate = lastIndicatorUpdate[key] || 0;
    
    if (now - lastUpdate < delay) {
        console.log(`Debouncing ${key} indicator update (last update was ${now - lastUpdate}ms ago)`);
        return;
    }
    
    lastIndicatorUpdate[key] = now;
    callback();
}

// Process notification queue to prevent race conditions
async function processNotificationQueue() {
    if (isProcessingQueue || notificationQueue.length === 0) {
        return;
    }
    
    isProcessingQueue = true;
    
    while (notificationQueue.length > 0) {
        const notification = notificationQueue.shift();
        console.log('Processing queued notification:', notification);
        
        try {
            if (notification.type === 'unread_notification') {
                // Normalize task_id to string for consistent comparison
                const taskId = String(notification.task_id);
                await updateTaskIndicator(taskId, notification.has_unread);
            } else if (notification.type === 'project_unread_notification') {
                // Normalize project_id to string for consistent comparison
                const projectId = String(notification.project_id);
                // --- PATCH: Always update project indicator for this user ---
                console.log(`[WS] Project ${projectId} unread state for current user: ${notification.has_unread}`);
                updateProjectIndicator(projectId, notification.has_unread);
            }
        } catch (error) {
            console.error('Error processing notification:', error);
        }
        
        // Small delay to prevent overwhelming the DOM
        await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    isProcessingQueue = false;
}
    
    // Initialize notification socket
    function initializeNotificationSocket() {
    // Prevent multiple socket connections
    if (notificationSocket && notificationSocket.readyState === WebSocket.OPEN) {
        console.log('Notification socket already connected, skipping initialization');
        return;
    }
    
        const socketProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const socketUrl = `${socketProtocol}//${window.location.host}/ws/notifications/`;
        
        if (notificationSocket) {
        console.log('Closing existing notification socket...');
            notificationSocket.close();
        }
        
    console.log('Creating new notification socket connection...');
        notificationSocket = new WebSocket(socketUrl);

        notificationSocket.onopen = function(e) {
        console.log('✅ Notification WebSocket connection opened successfully');
        // Clear any pending notifications when reconnecting
        notificationQueue = [];
        isProcessingQueue = false;
        };

        notificationSocket.onmessage = function(e) {
            try {
                const data = JSON.parse(e.data);
                console.log('=== RECEIVED NOTIFICATION ===');
                console.log('Raw data:', e.data);
                console.log('Parsed data:', data);

            // Add to queue instead of processing immediately
            notificationQueue.push(data);
            processNotificationQueue();
            
                console.log('=== END NOTIFICATION PROCESSING ===');
            } catch (error) {
                console.error('Error parsing notification message:', error);
            }
        };

        notificationSocket.onclose = function(e) {
        console.log('Notification WebSocket connection closed, code:', e.code);
            // Only attempt to reconnect if the close was not initiated by us
            if (e.code !== 1000) {
            console.log('Attempting to reconnect in 5 seconds...');
                setTimeout(initializeNotificationSocket, 5000);
            }
        };

        notificationSocket.onerror = function(e) {
            console.error('Notification WebSocket error:', e);
        };
    }

// Function to update task indicator
async function updateTaskIndicator(taskId, hasUnread) {
    // Don't show indicators if comments modal is open
    if (window.isCommentsModalOpen && hasUnread) {
        console.log('Comments modal is open, skipping indicator update for task:', taskId);
        return;
    }
    // Use debounce to prevent rapid updates
    const key = `task_${taskId}`;
    debounceIndicatorUpdate(key, async () => {
        // Find all Comments buttons for this task
        const commentButtons = document.querySelectorAll(`[data-task-id="${taskId}"][data-bs-target="#commentsModal"]`);
        console.log(`Found ${commentButtons.length} comment buttons for task ${taskId}`);
        let projectId = null;
        for (const button of commentButtons) {
            // Look for indicator in the button's parent div (position-relative wrapper)
            const parentDiv = button.closest('.position-relative');
            let indicator = parentDiv ? parentDiv.querySelector('.message-indicator') : null;
            // Find project ID from the closest task card
            if (!projectId) {
                const taskCard = button.closest('[data-project-id]');
                if (taskCard) {
                    projectId = taskCard.getAttribute('data-project-id');
                }
            }
            if (hasUnread) {
                if (!indicator) {
                    // Create new indicator if it doesn't exist
                    console.log(`Creating new task indicator for task ${taskId}`);
                    indicator = document.createElement('span');
                    indicator.className = 'message-indicator';
                    indicator.setAttribute('data-task-id', taskId); // Add data attribute for tracking
                    indicator.style.cssText = 'position: absolute !important; top: -5px !important; right: -5px !important; width: 12px !important; height: 12px !important; background-color: #ff3b30 !important; border: 2px solid #121212 !important; border-radius: 50% !important; display: block !important; z-index: 9999 !important; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important; pointer-events: none !important;';
                    if (parentDiv) {
                        parentDiv.appendChild(indicator);
                    } else {
                        button.appendChild(indicator);
                    }
                    console.log(`New task indicator created and added for task ${taskId}`);
                }
                // Force indicator to be visible with multiple methods
                indicator.style.setProperty('display', 'block', 'important');
                indicator.style.setProperty('visibility', 'visible', 'important');
                indicator.style.setProperty('opacity', '1', 'important');
                indicator.style.setProperty('background-color', '#ff3b30', 'important');
                indicator.style.setProperty('border-color', '#121212', 'important');
                // Remove any classes that might interfere
                indicator.classList.remove('show', 'hide');
                indicator.classList.add('active');
                console.log(`✅ SHOWING task indicator for task ${taskId}`);
            } else {
                if (indicator) {
                    // Force indicator to be hidden
                    indicator.style.setProperty('display', 'none', 'important');
                    indicator.style.setProperty('visibility', 'hidden', 'important');
                    indicator.style.setProperty('opacity', '0', 'important');
                    // Remove any classes that might interfere
                    indicator.classList.remove('show', 'active');
                    indicator.classList.add('hide');
                    console.log(`✅ HIDING task indicator for task ${taskId}`);
                }
            }
        }
        // --- Project indicator logic ---
        if (projectId) {
            // Check if any task in this project has an unread indicator
            const anyUnread = !!document.querySelector(
                `[data-project-id="${projectId}"] .message-indicator[style*='display: block']`
            );
            console.log(
                `[LOG] updateTaskIndicator: Project ${projectId} anyUnread=${anyUnread} (triggered by task ${taskId})`
            );
            updateProjectIndicator(projectId, anyUnread);
        }
    }, 500); // 500ms debounce delay
}

    // Handle project tasks modal
    if (projectTasksModal) {
        projectTasksModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const projectId = button.getAttribute('data-project-id');
            console.log('Opening project tasks modal for project:', projectId);
            
            // Don't hide project indicator when modal opens
            // It should only disappear when all tasks are actually read
        });
    }

// Reinitialize notification socket after successful login
const loginForm = document.querySelector('form[action="/login/"]');
if (loginForm) {
    loginForm.addEventListener('submit', function() {
        // Wait for login to complete and page to reload
        setTimeout(initializeNotificationSocket, 1000);
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

    // Debug function to test project indicator - remove this after testing
    window.testProjectIndicator = function(projectId) {
        console.log('Testing project indicator for project:', projectId);
        updateProjectIndicator(projectId, true);
    };

    // Debug function to hide project indicator - remove this after testing
    window.hideProjectIndicator = function(projectId) {
        console.log('Hiding project indicator for project:', projectId);
        updateProjectIndicator(projectId, false);
    };

    // Debug function to test project notification via API - remove this after testing
    window.testProjectNotification = function(projectId) {
        console.log('Testing project notification via API for project:', projectId);
        fetch(`/dashboard/test-project-notification/${projectId}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Test notification response:', data);
        })
        .catch(error => {
            console.error('Error testing project notification:', error);
        });
    };

// Debug function to check WebSocket connection status
window.checkWebSocketStatus = function() {
    console.log('=== WEB SOCKET STATUS CHECK ===');
    console.log('Notification socket:', notificationSocket);
    if (notificationSocket) {
        console.log('Ready state:', notificationSocket.readyState);
        console.log('URL:', notificationSocket.url);
        console.log('Protocol:', notificationSocket.protocol);
    }
    console.log('Queue length:', notificationQueue.length);
    console.log('Is processing queue:', isProcessingQueue);
    console.log('Modal open state:', window.isCommentsModalOpen);
};

// Debug function to test indicator with specific data
window.testIndicatorWithData = function(type, id, hasUnread) {
    console.log(`Testing ${type} indicator with ID: ${id}, hasUnread: ${hasUnread}`);
    if (type === 'task') {
        updateTaskIndicator(String(id), hasUnread);
    } else if (type === 'project') {
        updateProjectIndicator(String(id), hasUnread);
    }
};

// Debug function to clear all indicators
window.clearAllIndicators = function() {
    console.log('Clearing all indicators...');
    const allIndicators = document.querySelectorAll('.message-indicator');
    allIndicators.forEach(indicator => {
        indicator.style.display = 'none';
    });
    console.log(`Cleared ${allIndicators.length} indicators`);
};

// Debug function to show queue status
window.showQueueStatus = function() {
    console.log('=== QUEUE STATUS ===');
    console.log('Queue length:', notificationQueue.length);
    console.log('Is processing:', isProcessingQueue);
    console.log('Queue contents:', notificationQueue);
};

// Debug function to test modal state tracking
window.testModalState = function() {
    console.log('=== MODAL STATE TEST ===');
    console.log('Modal open state:', window.isCommentsModalOpen);
    console.log('Chat socket state:', chatSocket ? chatSocket.readyState : 'null');
    console.log('Notification socket state:', notificationSocket ? notificationSocket.readyState : 'null');
    
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        const taskId = document.getElementById('taskId').value;
        console.log('Current task ID:', taskId);
        console.log('Sending test modal_open event...');
        chatSocket.send(JSON.stringify({
            'type': 'modal_open',
            'task_id': taskId
        }));
    }
};

// Debug function to simulate modal close
window.simulateModalClose = function() {
    console.log('=== SIMULATING MODAL CLOSE ===');
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        const taskId = document.getElementById('taskId').value;
        console.log('Sending test modal_close event for task:', taskId);
        chatSocket.send(JSON.stringify({
            'type': 'modal_close',
            'task_id': taskId
        }));
    }
};

// Initialize notification socket
initializeNotificationSocket();

// Reinitialize notification socket after successful login
});

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('createTaskForm');
    const messageDiv = document.getElementById('createTaskMessage');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

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
            // Show success message
            messageDiv.classList.remove('d-none');
            // Reset form fields
            form.reset();
            // Hide success message after 3 seconds
            setTimeout(() => {
                messageDiv.classList.add('d-none');
            }, 3000);
        })
        .catch(error => {
            // More detailed error handling
            const errorMessage = error.error || error.message || 'Could not create task.';
            alert('Error: ' + errorMessage);
            console.error('Form submission error:', error);  // Add this for debugging
        });
    });
});

function renderPendingTasks(tasks) {
    const container = document.getElementById('pendingTasksContainer');
    container.innerHTML = '';
    if (tasks.length === 0) {
        container.innerHTML = '<div class="card p-3"><p class="text-center mb-0">No Other Pending Task</p></div>';
        return;
    }
    tasks.forEach(task => {
        container.innerHTML += `
            <div class="task-card card p-3 mb-3" data-priority="${task.priority.toLowerCase()}">
                <div class="priority-light"></div>
                <h6 class="fw-semibold">Name: ${task.task_name}</h6>
                <p class="text-secondary">Description: ${task.description}</p>
                <p>Due Date: ${task.due_date}</p>
                <p>Status: ${task.status}</p>
                <div class="task-card-buttons2 d-flex gap-2 mt-2">
                    <form method="POST" action="/dashboard/start-task/${task.id}/" class="start-task-form">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                        <button class="task-action-btn" type="submit">
                            <i class="fa fa-play-circle"></i>
                            <span>Start Task</span>
                        </button>
                    </form>
                    <button class="task-action-btn" 
                        data-bs-toggle="modal" 
                        data-bs-target="#taskDetailsModal"
                        data-task-name="${task.task_name}"
                        data-task-project="${task.project}"
                        data-task-priority="${task.priority}"
                        data-task-status="${task.status}"
                        data-task-due-date="${task.due_date}"
                        data-task-time-spent="${task.time_spent}"
                        data-task-description="${task.description}">
                        <i class="fa fa-info-circle"></i>
                        <span>Read More</span>
                    </button>
                    ${['employee', 'teamlead', 'project_manager', 'admin'].includes(window.USER_ROLE) ? `
                    ` : ''}
                </div>
            </div>
        `;
    });

    // Attach event listeners for modal buttons
    container.querySelectorAll('[data-bs-target="#taskDetailsModal"]').forEach(btn => {
        btn.addEventListener('click', function() {
            document.getElementById('modalTaskName').textContent = this.getAttribute('data-task-name');
            document.getElementById('modalProject').textContent = this.getAttribute('data-task-project');
            document.getElementById('modalPriority').textContent = this.getAttribute('data-task-priority');
            document.getElementById('modalTaskStatus').textContent = this.getAttribute('data-task-status');
            document.getElementById('modalTaskDueDate').textContent = this.getAttribute('data-task-due-date');
            document.getElementById('modalTimeSpent').textContent = this.getAttribute('data-task-time-spent');
            document.getElementById('modalTaskDescription').textContent = this.getAttribute('data-task-description');
        });
    });

    // Attach AJAX submit for start task forms
    container.querySelectorAll('.start-task-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("Complete task form submitted!");
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log("Complete task AJAX response:", data);
                pollPendingTasks();
                updateOngoingTasks();
                updateTodayStats();
                // Trigger stat update after completing a task
                if (typeof updateTaskStats === 'function') {
                    updateTaskStats();
                } else {
                    // Fallback: dispatch a custom event for stats update
                    document.dispatchEvent(new Event('taskDoneStatUpdate'));
                }
            })
            .catch(error => {
                alert('Error: Could not complete task.');
                console.error('Complete task AJAX error:', error);
            });
        });
    });

    // Attach delete button event listeners
    container.querySelectorAll('.delete-task-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const taskId = this.getAttribute('data-task-id');
            const projectId = this.getAttribute('data-project-id');
            if (!confirm('Are you sure you want to delete this task?')) return;
            deleteTask(taskId, projectId, this.closest('.task-card'));
        });
    });
}

function pollPendingTasks() {
    fetch('/dashboard/pending-tasks/')
        .then(response => response.json())
        .then(data => {
            renderPendingTasks(data.tasks);
        })
        .catch(error => {
            console.error('Error fetching pending tasks:', error);
        });
}

// Poll every 5 seconds
setInterval(pollPendingTasks, 10000);
// Initial load
pollPendingTasks();

// AJAX for ongoing tasks action buttons
function setupOngoingTaskAjax() {
    // Complete Task
    document.querySelectorAll('.complete-task-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("Complete task form submitted!");
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log("Complete task AJAX response:", data);
                pollPendingTasks();
                updateOngoingTasks();
                updateTodayStats();
                // Trigger stat update after completing a task
                if (typeof updateTaskStats === 'function') {
                    updateTaskStats();
                } else {
                    // Fallback: dispatch a custom event for stats update
                    document.dispatchEvent(new Event('taskDoneStatUpdate'));
                }
            })
            .catch(error => {
                alert('Error: Could not complete task.');
                console.error('Complete task AJAX error:', error);
            });
        });
    });
    // Start Working
    document.querySelectorAll('.start-working-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                pollPendingTasks();
                updateOngoingTasks();
            })
            .catch(error => {
                alert('Error: Could not start working on task.');
            });
        });
    });
    // Stop Working
    document.querySelectorAll('.stop-working-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                pollPendingTasks();
                updateOngoingTasks();
            })
            .catch(error => {
                alert('Error: Could not stop working on task.');
            });
        });
    });
}

// Call setupOngoingTaskAjax after rendering ongoing tasks
function updateOngoingTasks() {
    fetch('/dashboard/ongoing-tasks/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('ongoingTasksContainer');
            container.innerHTML = '';
            if (data.tasks.length === 0) {
                container.innerHTML = '<div class="col-12"><div class="ongoing-task-item card p-3 align-items-center" role="alert"><p class="text-center mb-0">No ongoing tasks available.</p></div></div>';
                return;
            }
            data.tasks.forEach(task => {
                let priorityClass = 'bg-success';
                if (task.priority === 'High') priorityClass = 'bg-danger';
                else if (task.priority === 'Medium') priorityClass = 'bg-warning';
                // console.log('Opening modal for taskId:', taskId);
                let actionButtons = `
                    <form method="POST" action="/dashboard/complete-task/${task.id}/" class="complete-task-form">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                        <button class="task-action-btn bg-primary text-white">
                            <i class="fa fa-check-circle"></i>
                            <span>Complete</span>
                        </button>
                    </form>
                `;
                if (task.status === 'On Hold') {
                    actionButtons += `
                        <form method="POST" action="/dashboard/start-working/${task.id}/" class="start-working-form">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                            <button class="task-action-btn bg-success text-white">
                                <i class="fa fa-play-circle"></i>
                                <span>Start Working</span>
                            </button>
                        </form>
                    `;
                } else if (task.status === 'In Progress') {
                    actionButtons += `
                        <form method="POST" action="/dashboard/stop-working/${task.id}/" class="stop-working-form">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                            <button class="task-action-btn bg-danger text-white">
                                <i class="fa fa-stop-circle"></i>
                                <span>Stop Working</span>
                            </button>
                        </form>
                    `;
                }
                // Files & Report, Comments, Read More buttons
                actionButtons += `
                    <button class="task-action-btn bg-info text-white"
                        data-bs-toggle="modal"
                        data-bs-target="#viewFilesModal"
                        data-task-id="${task.id}"
                        data-file-url="${task.file_url || '#'}"
                        data-file-name="${task.file_name || 'No file uploaded'}"
                        data-report-text="${task.report || 'No report submitted'}">
                        <i class="fa fa-upload"></i>
                        <span>Files & Report</span>
                    </button>
                    <div class="position-relative">
                        <button class="task-action-btn bg-dark text-white"
                            data-bs-toggle="modal"
                            data-bs-target="#commentsModal"
                            data-task-id="${task.id}"
                            data-has-unread="${task.has_unread_messages ? 'true' : 'false'}">
                            <i class="fas fa-comment-dots"></i>
                            <span>Comments</span>
                        </button>
                        ${task.has_unread_messages ? '<span class="message-indicator" style="display: block;"></span>' : ''}
                    </div>
                    <button class="task-action-btn bg-dark text-white"
                        data-bs-toggle="modal"
                        data-bs-target="#taskDetailsModal"
                        data-task-name="${task.task_name}"
                        data-task-project="${task.project}"
                        data-task-priority="${task.priority}"
                        data-task-status="${task.status}"
                        data-task-due-date="${task.due_date}"
                        data-task-time-spent="${task.time_spent}"
                        data-task-description="${task.description}">
                        <i class="fa fa-info-circle"></i>
                        <span>Read More</span>
                    </button>
                `;
                // console.log('Rendering Files & Report button for task id:', task.id);
                container.innerHTML += `
                    <div class="ongoing-task-item card p-3 mb-3" data-priority="${task.priority.toLowerCase()}">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="fw-semibold mb-0">Task: ${task.task_name}</h6>
                            <span class="badge ${priorityClass}">${task.priority}</span>
                        </div>
                        <p class="mb-1">Project: <strong>${task.project}</strong></p>
                        <p class="text-secondary mb-1">Description: <strong>${task.description}</strong></p>
                        <p class="mb-1">Time Spent: <strong>${task.time_spent}</strong></p>
                        <p class="mb-3">Due Date: <strong>${task.due_date}</strong></p>
                        <p class="task-meta">Status: <strong>${task.status}</strong></p>
                        <div class="task-card-buttons d-flex gap-2 mt-2">
                            ${actionButtons}
                        </div>
                    </div>
                `;
            });
            setupOngoingTaskAjax();
            setupFileUploadAjax();
            // Re-attach event listeners for Comments buttons after AJAX update
            container.querySelectorAll('[data-bs-target="#commentsModal"]').forEach(button => {
                button.addEventListener('click', function() {
                    const taskId = this.dataset.taskId;
                    const commentsList = document.getElementById('commentsList');
                    const modalTaskIdInput = document.getElementById('taskId');
                    modalTaskIdInput.value = taskId;
                    commentsList.innerHTML = '';
                    window.connectWebSocket(taskId);
                });
            });
        })
        .catch(error => {
            console.error('Error fetching ongoing tasks:', error);
        });
}

function setupFileUploadAjax() {
    document.querySelectorAll('.uploadFileForm').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log('File upload AJAX response:', data);
                if (data.success) {
                    alert('File uploaded successfully!');
                    // Fetch and display the uploaded file
                    const modal = form.closest('.modal');
                    if (modal) {
                        const fileDisplay = modal.querySelector('#fileDisplay');
                        if (fileDisplay) {
                            fileDisplay.innerHTML = '<div class="mb-2">Loading file...</div>';
                            fetch(`/dashboard/get-task-file/${formData.get('task_id')}/`)
                                .then(response => response.json())
                                .then(data => {
                                    if (data.success && data.file_url) {
                                        fileDisplay.innerHTML = `
                                            <div class="mb-2">
                                                <a href="${data.file_url}" class="btn btn-outline-primary btn-sm file-link" download>
                                                    <i class="fas fa-file"></i> <span class="file-name">${data.file_name}</span>
                                                </a>
                                            </div>`;
                                    } else {
                                        fileDisplay.innerHTML = '<div class="mb-2">No file uploaded</div>';
                                    }
                                })
                                .catch(() => {
                                    fileDisplay.innerHTML = '<div class="mb-2 text-danger">Error loading file</div>';
                                });
                        }
                    }
                    // Clear the file input after upload
                    form.reset();
                } else if (data.error) {
                    alert('Error uploading file: ' + data.error);
                } else {
                    alert('Unknown error uploading file.');
                }
            })
            .catch(error => {
                alert('Error uploading file.');
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    updateOngoingTasks();
});

document.addEventListener('submit', function(e) {
    if (e.target.classList.contains('uploadReportForm')) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        console.log('Submitting report for taskId:', form.action, 'Hidden input:', formData.get('task_id'));
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Report submitted successfully!');
                // After successful submission, fetch the latest report from the server
                const modal = form.closest('.modal');
                if (modal) {
                    const reportDisplay = modal.querySelector('#reportDisplay');
                    if (reportDisplay) {
                        reportDisplay.innerHTML = '<div class="border p-3 mb-3">Loading...</div>';
                        const match = form.action.match(/upload_task_report\/(\d+)\//);
                        const taskId = match ? match[1] : null;
                        if (taskId) {
                            fetch(`/dashboard/get-task-report/${taskId}/`)
                                .then(response => response.json())
                                .then(data => {
                                    console.log('Fetched report after submit for taskId:', taskId, 'Report:', data.report);
                                    if (data.success) {
                                        reportDisplay.innerHTML = `
                                            <div class="border p-3 mb-3">
                                                ${data.report ? data.report : 'No report submitted'}
                                            </div>`;
                                    } else {
                                        reportDisplay.innerHTML = `<div class="border p-3 mb-3 text-danger">Error loading report</div>`;
                                    }
                                })
                                .catch(() => {
                                    reportDisplay.innerHTML = `<div class="border p-3 mb-3 text-danger">Error loading report</div>`;
                                });
                        }
                    }
                }
                form.reset();
            } else {
                alert('Error submitting report: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            alert('AJAX error: ' + error);
        });
    }
});

document.addEventListener('click', function(e) {
    const btn = e.target.closest('[data-bs-target="#viewFilesModal"]');
    if (btn) {
        const taskId = btn.getAttribute('data-task-id');
        const viewFilesModal = document.getElementById('viewFilesModal');
        if (viewFilesModal) {
            // Set file upload form action and hidden input
            const fileForm = viewFilesModal.querySelector('.uploadFileForm');
            if (fileForm) {
                fileForm.action = `/dashboard/upload_task_file/${taskId}/`;
                console.log('[CLICK] Set fileForm.action to:', fileForm.action);
            }
            const fileTaskIdInput = viewFilesModal.querySelector('#fileTaskId');
            if (fileTaskIdInput) {
                fileTaskIdInput.value = taskId;
                console.log('[CLICK] Set fileTaskIdInput.value to:', fileTaskIdInput.value);
            }
            // Update report form
            const reportForm = viewFilesModal.querySelector('.uploadReportForm');
            if (reportForm) {
                reportForm.action = `/dashboard/upload_task_report/${taskId}/`;
                console.log('Set reportForm.action to:', reportForm.action);
            } else {
                console.log('No .uploadReportForm found in modal!');
            }
            // Fetch and display the report for this task
            const reportDisplay = viewFilesModal.querySelector('#reportDisplay');
            if (reportDisplay) {
                console.log('[CLICK] About to fetch report for taskId:', taskId);
                reportDisplay.innerHTML = '<div class="border p-3 mb-3">Loading...</div>';
                fetch(`/dashboard/get-task-report/${taskId}/`)
                    .then(response => response.json())
                    .then(data => {
                        console.log('[CLICK] Fetched report for taskId:', taskId, 'Report:', data.report);
                        if (data.success) {
                            reportDisplay.innerHTML = `
                                <div class="border p-3 mb-3">
                                    ${data.report ? data.report : 'No report submitted'}
                                </div>`;
                        } else {
                            reportDisplay.innerHTML = `<div class="border p-3 mb-3 text-danger">Error loading report</div>`;
                        }
                    })
                    .catch(() => {
                        reportDisplay.innerHTML = `<div class="border p-3 mb-3 text-danger">Error loading report</div>`;
                    });
            }

            const fileDisplay = viewFilesModal.querySelector('#fileDisplay');
            if (fileDisplay) {
                fileDisplay.innerHTML = '<div class="mb-2">Loading file...</div>';
                fetch(`/dashboard/get-task-file/${taskId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && data.file_url) {
                            fileDisplay.innerHTML = `
                                <div class="mb-2">
                                    <a href="${data.file_url}" class="btn btn-outline-primary btn-sm file-link" download>
                                        <i class="fas fa-file"></i> <span class="file-name">${data.file_name}</span>
                                    </a>
                                </div>`;
                        } else {
                            fileDisplay.innerHTML = '<div class="mb-2">No file uploaded</div>';
                        }
                    })
                    .catch(() => {
                        fileDisplay.innerHTML = '<div class="mb-2 text-danger">Error loading file</div>';
                    });
            }
        }
    }
});

// Also clear the file input when the modal is closed
const viewFilesModal = document.getElementById('viewFilesModal');
if (viewFilesModal) {
    viewFilesModal.addEventListener('hidden.bs.modal', function() {
        const fileForm = viewFilesModal.querySelector('.uploadFileForm');
        if (fileForm) {
            fileForm.reset();
        }
    });
}

// Approval Pending Tasks Functions
let approvalPendingInterval;

function renderApprovalPendingTasks(tasks) {
    const container = document.getElementById('approvalPendingContainer');
    if (!container) return;

    if (!tasks || tasks.length === 0) {
        container.innerHTML = `
            <div class="card p-3">
                <p class="text-center mb-0">No Other Pending Approval</p>
            </div>`;
        return;
    }

    let html = '';
    tasks.forEach(task => {
        html += `
            <div class="task-card card p-3 mb-3" data-priority="high" data-task-id="${task.id}" data-project-id="${task.project_id || ''}">
                <div class="priority-light"></div>
                <h6 class="fw-semibold">Name: ${task.task_name}</h6>
                <p class="text-secondary">Description: ${task.task_description}</p>
                <p>Due Date: ${task.due_date}</p>
                <p>Status: ${task.status_display}</p>
                <p>Project: ${task.project_name}</p>
                ${task.project_department ? `<p>Department: ${task.project_department}</p>` : ''}
                <div class="task-card-buttons2 d-flex gap-2 mt-2">
                    ${
                      (window.USER_ROLE === 'teamlead' || window.USER_ROLE === 'project_manager')
                      ? `
                        <form method="POST" action="/dashboard/approve-task/${task.id}/" class="approve-task-form">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                            <button type="submit" class="task-action-btn">
                                <i class="fa fa-check-circle"></i>
                                <span>Approve</span>
                            </button>
                        </form>
                        <button type="button" class="task-action-btn reject-task-btn"
                                data-task-id="${task.id}"
                                data-project-id="${task.project_id || ''}">
                            <i class="fa fa-times-circle"></i>
                            <span>Reject</span>
                        </button>
                      ` : ''
                    }
                    <button class="task-action-btn"
                            data-bs-toggle="modal"
                            data-bs-target="#taskDetailsModal"
                            data-task-name="${task.task_name}"
                            data-task-project="${task.project_name}"
                            data-task-priority="${task.priority}"
                            data-task-status="${task.status_display}"
                            data-task-due-date="${task.due_date}"
                            data-task-time-spent="${task.time_spent}"
                            data-task-description="${task.task_description}">
                        <i class="fa fa-info-circle"></i>
                        <span>Read More</span>
                    </button>
                </div>
            </div>`;
    });
    
    container.innerHTML = html;

    // Add event listeners to the approve forms
    container.querySelectorAll('.approve-task-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    pollApprovalPendingTasks(); // Refresh the list immediately
                } else {
                    alert('Error: ' + (data.error || 'Could not approve task.'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error approving task.');
            });
        });
    });

    // Add event listeners to the reject buttons
    container.querySelectorAll('.reject-task-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const taskId = this.getAttribute('data-task-id');
            const projectId = this.getAttribute('data-project-id');
            if (!confirm('Are you sure you want to reject/delete this task?')) return;
            deleteTask(taskId, projectId, this.closest('.task-card'));
        });
    });
}

function pollApprovalPendingTasks() {
    fetch('/dashboard/approval-pending-tasks-json/', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        renderApprovalPendingTasks(data.tasks);
    })
    .catch(error => {
        console.error('Error fetching approval pending tasks:', error);
    });
}

function setupApprovalPendingTasksPolling() {
    // Initial load
    pollApprovalPendingTasks();
    
    // Clear existing interval if any
    if (approvalPendingInterval) {
        clearInterval(approvalPendingInterval);
    }
    
    // Set up new polling interval
    approvalPendingInterval = setInterval(pollApprovalPendingTasks, 10000); // 10 seconds
}

// Initialize polling when document is ready
document.addEventListener('DOMContentLoaded', function() {
    setupApprovalPendingTasksPolling();
    
    // Listen for task submission events to trigger immediate refresh
    document.addEventListener('taskSubmitted', function() {
        pollApprovalPendingTasks();
    });
});

function updateTodayStats() {
    console.log("updateTodayStats called!");
    fetch('/dashboard/employee-today-stats-json/', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Stats response:", data);
        if (data.total_time_today !== undefined) {
            const timeElem = document.getElementById('totalTimeToday');
            if (timeElem) timeElem.textContent = data.total_time_today;
        }
        // Robustly update 'Tasks Done'
        let tasksDoneUpdated = false;
        if (data.tasks_done_today !== undefined) {
            document.querySelectorAll('.row.text-center.mb-4 .col-md-3 .card').forEach(card => {
                const p = card.querySelector('p.text-secondary');
                if (p && p.textContent.trim() === 'Tasks Done') {
                    const h3 = card.querySelector('h3');
                    if (h3) {
                        h3.textContent = data.tasks_done_today;
                        tasksDoneUpdated = true;
                    }
                }
            });
            // Fallback: update the second .col-md-3 h3 if not found by label
            if (!tasksDoneUpdated) {
                const fallback = document.querySelector('.row.text-center.mb-4 .col-md-3:nth-of-type(2) h3');
                if (fallback) fallback.textContent = data.tasks_done_today;
            }
        }
        if (data.tasks_expiring_today !== undefined) {
            document.querySelectorAll('.row.text-center.mb-4 .col-md-3 .card').forEach(card => {
                const p = card.querySelector('p.text-secondary');
                if (p && p.textContent.trim() === 'Tasks Expiring Today') {
                    const h3 = card.querySelector('h3');
                    if (h3) h3.textContent = data.tasks_expiring_today;
                }
            });
        }
        if (data.expired_tasks !== undefined) {
            document.querySelectorAll('.row.text-center.mb-4 .col-md-3 .card').forEach(card => {
                const p = card.querySelector('p.text-secondary');
                if (p && p.textContent.trim() === 'Expired Tasks') {
                    const h3 = card.querySelector('h3');
                    if (h3) h3.textContent = data.expired_tasks;
                }
            });
        }
    })
    .catch(error => {
        console.error('Error updating today stats:', error);
    });
}

document.addEventListener('click', function(e) {
    // If a button inside a complete-task-form is clicked
    const btn = e.target.closest('form.complete-task-form button');
    if (btn) {
        // Call updateTodayStats after a short delay to allow backend to process
        setTimeout(updateTodayStats, 500);
    }
});



// Project Tasks Search ---
function setupProjectTasksSearch() {
    const projectTasksModal = document.getElementById('projectTasksModal');
    if (!projectTasksModal) return;

    let debounceTimeout = null;

    // Helper to render tasks
    function renderProjectTasks(tasks) {
        const container = document.getElementById('projectTasksContainer');
        container.innerHTML = '';
        if (tasks && tasks.length > 0) {
            tasks.forEach(task => {
                const priorityClass = task.priority === 'high' ? 'bg-danger' :
                    task.priority === 'medium' ? 'bg-warning' : 'bg-success';
                const hasUnread = task.has_unread_messages || false;
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
                                        ${hasUnread ? '<span class="message-indicator" style="display: block !important;"></span>' : ''}
                                    </div>
                                    ${['employee', 'teamlead', 'project_manager', 'admin'].includes(window.USER_ROLE) ? `
                                        <button class="btn btn-outline-danger task-action-btn"
                                                type="button"
                                                onclick="deleteTask(${task.id})">
                                            <i class="fa fa-trash"></i>
                                            <span>Delete</span>
                                        </button>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                container.innerHTML += taskCard;
            });
        } else {
            container.innerHTML = '<div class="col-12"><p class="text-center">No tasks found for this project.</p></div>';
        }
    }

    projectTasksModal.addEventListener('show.bs.modal', function (event) {
        const searchInput = projectTasksModal.querySelector('#projectTasksSearchInput');
        if (!searchInput) return;

        // Try to get projectId from the triggering button
        let projectId = null;
        if (event && event.relatedTarget) {
            projectId = event.relatedTarget.getAttribute('data-project-id');
        }
        // Fallback: try to get from modal attribute if needed
        if (!projectId && projectTasksModal.getAttribute('data-project-id')) {
            projectId = projectTasksModal.getAttribute('data-project-id');
        }
        if (!projectId) {
            const container = projectTasksModal.querySelector('#projectTasksContainer');
            container.innerHTML = '<div class="col-12"><p class="text-center text-danger">No project ID found.</p></div>';
            return;
        }

        // If already loaded for this project, use cached data
        if (window.allProjectTasks && Array.isArray(window.allProjectTasks) && window.allProjectTasks.projectId === projectId && window.allProjectTasks.tasks && window.allProjectTasks.tasks.length > 0) {
            searchInput.value = '';
            renderProjectTasks(window.allProjectTasks.tasks);

            // Remove previous event listeners
            searchInput.oninput = null;
            searchInput.addEventListener('input', function() {
                if (debounceTimeout) clearTimeout(debounceTimeout);
                debounceTimeout = setTimeout(() => {
                    const query = searchInput.value.trim().toLowerCase();
                    const words = query.split(/\s+/).filter(Boolean);
                    const filtered = window.allProjectTasks.tasks.filter(task => {
                        const taskName = (task.task_name || '').toLowerCase();
                        const assignedTo = (task.assigned_to || '').toLowerCase();
                        const allInTaskName = words.every(word => taskName.includes(word));
                        const allInAssignedTo = words.every(word => assignedTo.includes(word));
                        return allInTaskName || allInAssignedTo;
                    });
                    renderProjectTasks(filtered);
                }, 2000);
            });
            return;
        }

        // Otherwise, fetch and cache
        const container = projectTasksModal.querySelector('#projectTasksContainer');
        container.innerHTML = '<div class="col-12"><p class="text-center">Loading tasks...</p></div>';

        fetch(`/dashboard/get-project-tasks/${projectId}/`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            window.allProjectTasks = { projectId: projectId, tasks: data.tasks || [] };
            searchInput.value = '';
            renderProjectTasks(window.allProjectTasks.tasks);

            // Remove previous event listeners
            searchInput.oninput = null;
            searchInput.addEventListener('input', function() {
                if (debounceTimeout) clearTimeout(debounceTimeout);
                debounceTimeout = setTimeout(() => {
                    const query = searchInput.value.trim().toLowerCase();
                    const words = query.split(/\s+/).filter(Boolean);
                    const filtered = window.allProjectTasks.tasks.filter(task => {
                        const taskName = (task.task_name || '').toLowerCase();
                        const assignedTo = (task.assigned_to || '').toLowerCase();
                        const allInTaskName = words.every(word => taskName.includes(word));
                        const allInAssignedTo = words.every(word => assignedTo.includes(word));
                        return allInTaskName || allInAssignedTo;
                    });
                    renderProjectTasks(filtered);
                }, 2000);
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    setupProjectTasksSearch();
});

// ... existing code ...

    // Notification Dropdown Logic
    const notificationBell = document.getElementById('notificationBell');
    const notificationList = document.getElementById('notificationList');
    const notificationBadge = document.getElementById('notificationBadge');
    const mobileNotificationBell = document.getElementById('mobileNotificationBell');
    const mobileNotificationList = document.getElementById('mobileNotificationList');
    const mobileNotificationBadge = document.getElementById('mobileNotificationBadge');
    let notificationsCache = null;

    async function fetchNotifications() {
        try {
            const response = await fetch('/dashboard/employee-notifications-json/');
            const data = await response.json();
            notificationsCache = data.notifications || [];
            renderNotifications();
        } catch (e) {
            const errorMessage = '<div class="p-3 text-danger">Failed to load notifications.</div>';
            if (notificationList) notificationList.innerHTML = errorMessage;
            if (mobileNotificationList) mobileNotificationList.innerHTML = errorMessage;
        }
    }

    function renderNotifications() {
        if (!notificationsCache || notificationsCache.length === 0) {
            const emptyMessage = '<div class="p-3 text-muted">No notifications.</div>';
            if (notificationList) {
                notificationList.innerHTML = emptyMessage;
                notificationBadge.style.display = 'none';
            }
            if (mobileNotificationList) {
                mobileNotificationList.innerHTML = emptyMessage;
                if (mobileNotificationBadge) mobileNotificationBadge.style.display = 'none';
            }
            return;
        }

        // Count ALL unread notifications for the badge
        const totalUnread = notificationsCache.filter(n => !n.is_read).length;
        // Only show the 3 most recent notifications in the dropdown
        const notificationsToShow = notificationsCache.slice(0, 3);
        const notificationHtml = notificationsToShow.map(n => {
            return `<div class="notification-item${n.is_read ? '' : ' unread'}">
                <i class='fa fa-bell notification-icon'></i>
                <div class="notification-content">
                  <div class="notification-title">${n.message}</div>
                  <div class="notification-status">${n.timestamp}${!n.is_read ? '<span class=\"notification-new ms-2\">New</span>' : ''}</div>
                </div>
            </div>`;
        }).join('');

        // Update desktop notifications
        if (notificationList) {
            notificationList.innerHTML = notificationHtml;
            notificationBadge.textContent = totalUnread;
            notificationBadge.style.display = totalUnread > 0 ? '' : 'none';
            // Show remaining unread count in 'See All' badge
            const seeAllUnreadBadge = document.getElementById('seeAllUnreadBadge');
            if (seeAllUnreadBadge) {
                // Count unread in the first 3
                const unreadInDropdown = notificationsToShow.filter(n => !n.is_read).length;
                const remainingUnread = totalUnread - unreadInDropdown;
                console.log('See All badge: totalUnread=', totalUnread, 'unreadInDropdown=', unreadInDropdown, 'remainingUnread=', remainingUnread);
                if (remainingUnread > 0) {
                    seeAllUnreadBadge.textContent = '+' + remainingUnread;
                    seeAllUnreadBadge.style.display = '';
                } else {
                    seeAllUnreadBadge.style.display = 'none';
                }
            }
        }

        // Update mobile notifications
        if (mobileNotificationList) {
            mobileNotificationList.innerHTML = notificationHtml;
            if (mobileNotificationBadge) {
                mobileNotificationBadge.textContent = totalUnread;
                mobileNotificationBadge.style.display = totalUnread > 0 ? '' : 'none';
            }
        }
    }

    // Mark all as read when either dropdown is closed (not opened)
    const markAsRead = async () => {
        if (!notificationsCache) await fetchNotifications();
        // Only mark as read the 3 notifications currently shown in the dropdown
        const notificationsToShow = notificationsCache ? notificationsCache.slice(0, 3) : [];
        const unreadToMark = notificationsToShow.filter(n => !n.is_read && n.id);
        if (unreadToMark.length > 0) {
            const ids = unreadToMark.map(n => n.id);
            console.log('Marking as read notification IDs:', ids);
            const response = await fetch('/dashboard/mark-notifications-read/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
                body: JSON.stringify({ notification_ids: ids })
            });
            const data = await response.json();
            console.log('Mark as read response:', data);
            // Update only those as read in the cache
            notificationsCache = notificationsCache.map(n => ids.includes(n.id) ? { ...n, is_read: true } : n);
            renderNotifications();
        }
    };

    const notificationDropdownMenu = document.getElementById('notificationDropdown');
    const mobileNotificationDropdownMenu = document.getElementById('mobileNotificationDropdown');

    // Fetch notifications on page load
    fetchNotifications();

    // Fetch notifications when bell is clicked
    if (notificationBell) {
        notificationBell.addEventListener('click', function() {
            fetchNotifications();
        });
    }
    if (mobileNotificationBell) {
        mobileNotificationBell.addEventListener('click', function() {
            fetchNotifications();
        });
    }

    // GOD MODE: Use event delegation for dropdown close event (works for both desktop and mobile)
    document.body.addEventListener('hidden.bs.dropdown', function(e) {
        // Desktop
        if (e.target && e.target.id === 'notificationBell') {
            console.log('[GOD MODE] Desktop dropdown closed, marking notifications as read');
            markAsRead();
        }
        // Mobile
        if (e.target && e.target.id === 'mobileNotificationBell') {
            console.log('[GOD MODE] Mobile dropdown closed, marking notifications as read');
            markAsRead();
        }
    });

    ['show.bs.dropdown', 'shown.bs.dropdown', 'hide.bs.dropdown', 'hidden.bs.dropdown'].forEach(eventName => {
        document.body.addEventListener(eventName, function(e) {
            console.log(`[DEBUG] ${eventName} fired!`, 'e.target:', e.target, 'id:', e.target.id, 'class:', e.target.className);
        });
    });

    // Poll notifications every 10 seconds
    setInterval(fetchNotifications, 10000);

    // --- Fix reject-task-form to prevent reload and use AJAX ---
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('.reject-task-form').forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                // Get the taskId from the button's onclick or data attribute
                const btn = form.querySelector('button[onclick^="deleteTask("]');
                let taskId = null;
                if (btn) {
                    const match = btn.getAttribute('onclick').match(/deleteTask\((\d+)\)/);
                    if (match) {
                        taskId = match[1];
                    }
                }
                if (taskId) {
                    deleteTask(taskId);
                } else {
                    alert('Could not determine task ID for rejection.');
                }
            });
        });
    });

function deleteTask(taskId, projectId, cardElem) {
    fetch(`/dashboard/delete-task/${projectId}/?task_id=${taskId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (cardElem) cardElem.remove();
            // Optionally show a toast or message
        } else {
            alert(data.error || 'Could not delete task.');
        }
        pollPendingTasks();
        updateOngoingTasks && updateOngoingTasks();
    })
    .catch(error => {
        alert('Error: Could not delete task.');
        console.error('Delete task AJAX error:', error);
    });
}



