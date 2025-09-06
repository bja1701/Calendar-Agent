document.addEventListener('DOMContentLoaded', () => {
    const eventInput = document.getElementById('event-input');
    const scheduleButton = document.getElementById('schedule-button');
    const schedulerStatus = document.getElementById('scheduler-status');
    const tasksUl = document.getElementById('tasks-ul');
    const tasksStatus = document.getElementById('tasks-status');
    const refreshTasksButton = document.getElementById('refresh-tasks-button');

    // Function to display status messages
    const showStatus = (element, message, isSuccess) => {
        element.textContent = message;
        element.className = 'status-message'; // Reset classes
        if (isSuccess) {
            element.classList.add('success');
        } else {
            element.classList.add('error');
        }
    };

    // --- Schedule a new event ---
    scheduleButton.addEventListener('click', async () => {
        const text = eventInput.value.trim();
        if (!text) {
            showStatus(schedulerStatus, 'Please enter an event description.', false);
            return;
        }

        scheduleButton.disabled = true;
        scheduleButton.textContent = 'Scheduling...';
        schedulerStatus.style.display = 'none';

        try {
            const response = await fetch('/schedule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text }),
            });

            const result = await response.json();

            if (response.ok) {
                showStatus(schedulerStatus, 'Event scheduled successfully!', true);
                eventInput.value = ''; // Clear input field
                fetchTasks(); // Refresh the task list
            } else {
                showStatus(schedulerStatus, `Error: ${result.error}`, false);
            }
        } catch (error) {
            showStatus(schedulerStatus, `Network error: ${error.message}`, false);
        } finally {
            scheduleButton.disabled = false;
            scheduleButton.textContent = 'Schedule';
        }
    });

    // --- Fetch and display tasks ---
    const fetchTasks = async () => {
        tasksUl.innerHTML = '<li>Loading tasks...</li>';
        tasksStatus.style.display = 'none';

        try {
            const response = await fetch('/tasks');
            const tasks = await response.json();

            tasksUl.innerHTML = ''; // Clear the list

            if (tasks.length === 0) {
                tasksUl.innerHTML = '<li>No tasks scheduled for today.</li>';
            } else {
                tasks.forEach(task => {
                    const li = document.createElement('li');

                    const summarySpan = document.createElement('span');
                    summarySpan.className = 'summary';
                    summarySpan.textContent = task.summary;

                    const timeSpan = document.createElement('span');
                    timeSpan.className = 'time';
                    timeSpan.textContent = task.start_time;

                    li.appendChild(summarySpan);
                    li.appendChild(timeSpan);
                    tasksUl.appendChild(li);
                });
            }
        } catch (error) {
            showStatus(tasksStatus, `Error fetching tasks: ${error.message}`, false);
            tasksUl.innerHTML = ''; // Clear loading message
        }
    };

    // --- Event Listeners ---
    refreshTasksButton.addEventListener('click', fetchTasks);

    // Fetch tasks on initial page load
    fetchTasks();
});
