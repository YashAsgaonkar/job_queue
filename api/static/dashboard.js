// Dashboard.js - Handles task queue dashboard functionality

// Global variables
let allTasks = [];
let currentSort = { field: 'timestamp', direction: 'desc' };
let currentFilter = 'all';
let lastUpdated = null;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners
    fetchTasks();

    document.getElementById('refresh').addEventListener('click', fetchTasks);
    
    // Modal controls
    document.getElementById('closeModal').addEventListener('click', closeModal);
    document.getElementById('closeModalBtn').addEventListener('click', closeModal);
    
    // Filter buttons
    document.getElementById('filter-all').addEventListener('click', () => setFilter('all'));
    document.getElementById('filter-pending').addEventListener('click', () => setFilter('pending'));
    document.getElementById('filter-processing').addEventListener('click', () => setFilter('processing'));
    document.getElementById('filter-success').addEventListener('click', () => setFilter('success'));
    document.getElementById('filter-failed').addEventListener('click', () => setFilter('failed'));
    document.getElementById('filter-permanently_failed').addEventListener('click', () => setFilter('permanently_failed'));
    
    // Set up sorting
    document.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const field = th.getAttribute('data-sort');
            sortTasks(field);
        });
    });
    
    // Initial fetch
    updateLastUpdatedTime();
});

// Fetch tasks from the API
function fetchTasks() {
    fetch('/api/tasks')
        .then(response => response.json())
        .then(data => {
            allTasks = data;
            lastUpdated = new Date();
            updateLastUpdatedTime();
            renderTasks();
        })
        .catch(error => {
            console.error('Error fetching tasks:', error);
        });
}

// Update the last updated timestamp
function updateLastUpdatedTime() {
    const lastUpdatedElement = document.getElementById('last-updated-time');
    if (!lastUpdated) {
        lastUpdated = new Date(); // Set initial time when first loading
    }
    lastUpdatedElement.textContent = lastUpdated.toLocaleTimeString();
}

// Render tasks to the table
function renderTasks() {
    const tableBody = document.getElementById('tasks-table');
    tableBody.innerHTML = '';
    
    // Apply filter and sort
    const filteredTasks = filterTasksByStatus(allTasks);
    const sortedTasks = sortTasksByField(filteredTasks);
    
    if (sortedTasks.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="7" class="px-6 py-4 text-center text-sm text-gray-500">No tasks found</td>';
        tableBody.appendChild(row);
        return;
    }
    
    sortedTasks.forEach(task => {
    const row = document.createElement('tr');
    
    // Apply Tailwind classes directly based on status
    if (task.status.toLowerCase() === 'pending') {
      row.classList.add('bg-yellow-100');
    } else if (task.status.toLowerCase() === 'success') {
      row.classList.add('bg-green-100');
    } else if (task.status.toLowerCase() === 'failed') {
      row.classList.add('bg-red-100');
    } else if (task.status.toLowerCase() === 'processing') {
      row.classList.add('bg-blue-100');
    } else if (task.status.toLowerCase() === 'permanently_failed') {
      row.classList.add('bg-red-300');
    }
    
      // Set the proper status class for background color
    row.setAttribute('data-id', task.id);
        
        // Format timestamp
        const createdDate = new Date(task.created_at * 1000);
        const pickedDate = task.picked_at ? new Date(task.picked_at * 1000) : null;
        const completedDate = task.completed_at ? new Date(task.completed_at * 1000) : null;
        
        // Apply priority class
        const priorityClass = `priority-${task.priority.toLowerCase()}`;
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${task.id}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${task.job_type}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${truncateText(task.payload, 30)}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm ${priorityClass}">${task.priority}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                Created: ${createdDate.toLocaleString()}<br>
                ${pickedDate ? `Picked: ${pickedDate.toLocaleString()}<br>` : ''}
                ${completedDate ? `Completed: ${completedDate.toLocaleString()}` : ''}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm ${getStatusClass(task.status)}">${task.status}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm ${task.retry_count > 0 ? 'text-red-600' : 'text-gray-500'}">
                ${task.retry_count}
                ${task.last_error ? `<br><span class="text-xs text-red-500">${truncateText(task.last_error, 20)}</span>` : ''}
            </td>
        `;
        
        row.addEventListener('click', () => showTaskDetails(task));
        tableBody.appendChild(row);
    });
}
function getStatusClass(status) {
    switch(status.toLowerCase()) {
        case 'pending':
            return 'text-yellow-800';
        case 'processing':
            return 'text-blue-800';
        case 'success':
            return 'text-green-800';
        case 'failed':
            return 'text-red-800';
        case 'permanently_failed':
            return 'text-gray-800';
        default:
            return 'text-gray-600';
    }
}
// Show task details in modal
function showTaskDetails(task) {
    const detailElement = document.getElementById('task-detail-json');
    detailElement.textContent = JSON.stringify(task, null, 2);
    
    // Set modal title
    document.getElementById('taskDetailModalLabel').textContent = `Task Details: ${task.id}`;
    
    // Show modal
    document.getElementById('taskDetailModal').classList.remove('hidden');
}

// Close the modal
function closeModal() {
    document.getElementById('taskDetailModal').classList.add('hidden');
}

// Sort tasks by field
function sortTasks(field) {
    if (currentSort.field === field) {
        // Toggle direction if same field
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.field = field;
        currentSort.direction = 'asc';
    }
    
    // Update UI to show sort direction
    document.querySelectorAll('th.sortable').forEach(th => {
        th.classList.remove('sorted-asc', 'sorted-desc');
        if (th.getAttribute('data-sort') === field) {
            th.classList.add(`sorted-${currentSort.direction}`);
        }
    });
    
    renderTasks();
}

// Sort function implementation
function sortTasksByField(tasks) {
    const { field, direction } = currentSort;
    
    return [...tasks].sort((a, b) => {
        let comparison = 0;
        
        // Handle different field types
        if (field === 'id' || field === 'retry_count') {
            comparison = a[field] - b[field];
        } else if (field === 'timestamp') {
            comparison = a[field] - b[field];
        } else {
            comparison = String(a[field]).localeCompare(String(b[field]));
        }
        
        return direction === 'asc' ? comparison : -comparison;
    });
}

// Filter by status
function setFilter(status) {
    currentFilter = status;
    
    // Update button states
    document.querySelectorAll('[id^="filter-"]').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`filter-${status}`).classList.add('active');
    
    renderTasks();
}

// Filter function implementation
function filterTasksByStatus(tasks) {
    if (currentFilter === 'all') {
        return tasks;
    }
    
    return tasks.filter(task => task.status === currentFilter);
}

// Helper to truncate text
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}