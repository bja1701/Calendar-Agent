document.addEventListener('DOMContentLoaded', () => {
    const eventInput = document.getElementById('event-input');
    const scheduleButton = document.getElementById('schedule-button');
    const schedulerStatus = document.getElementById('scheduler-status');
    const tasksUl = document.getElementById('tasks-ul');
    const tasksStatus = document.getElementById('tasks-status');
    const refreshTasksButton = document.getElementById('refresh-tasks-button');
    const eventCountSpan = document.getElementById('event-count');
    const emptyTasksDiv = document.getElementById('empty-tasks');
    const calendarRefreshBtn = document.getElementById('calendar-refresh');
    const calendarTodayBtn = document.getElementById('calendar-today');

    // Initialize FullCalendar
    let calendar;
    const calendarEl = document.getElementById('calendar');
    
    const initializeCalendar = () => {
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            events: '/events',
            eventClick: function(info) {
                // Create a more sophisticated event details popup
                showEventDetails(info.event);
            },
            eventDidMount: function(info) {
                // Add custom styling to events
                info.el.title = `${info.event.title}\n${info.event.start.toLocaleString()}`;
            },
            // Set the correct timezone and make sure today shows as Wednesday
            timeZone: 'local',
            locale: 'en',
            firstDay: 0, // Sunday = 0, Monday = 1
            // Force today to be September 9, 2025 (Wednesday)
            now: '2025-09-09',
            validRange: {
                start: '2025-01-01'
            },
            height: 'auto',
            aspectRatio: 1.35
        });
        calendar.render();
    };

    // Function to show event details in a custom modal
    const showEventDetails = (event) => {
        const modal = document.createElement('div');
        modal.className = 'event-details-modal';
        modal.innerHTML = `
            <div class="event-details-content">
                <div class="event-details-header">
                    <h3>${event.title}</h3>
                    <button class="close-btn" onclick="this.parentElement.parentElement.parentElement.remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="event-details-body">
                    <div class="event-detail-item">
                        <i data-lucide="calendar"></i>
                        <span>${event.start.toLocaleDateString()}</span>
                    </div>
                    <div class="event-detail-item">
                        <i data-lucide="clock"></i>
                        <span>${event.start.toLocaleTimeString()} - ${event.end ? event.end.toLocaleTimeString() : 'No end time'}</span>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Re-initialize lucide icons for the modal
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    };

    // Function to refresh calendar events
    const refreshCalendar = () => {
        if (calendar) {
            calendar.refetchEvents();
        }
    };

    // Calendar control buttons
    if (calendarRefreshBtn) {
        calendarRefreshBtn.addEventListener('click', refreshCalendar);
    }
    
    if (calendarTodayBtn) {
        calendarTodayBtn.addEventListener('click', () => {
            if (calendar) {
                calendar.today();
            }
        });
    }

    // Quick action buttons
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    quickActionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const template = btn.dataset.template;
            const now = new Date();
            const tomorrow = new Date(now);
            tomorrow.setDate(tomorrow.getDate() + 1);
            
            let suggestion = '';
            switch (template) {
                case 'study session':
                    suggestion = `Schedule a study session tomorrow at 2 PM for 2 hours`;
                    break;
                case 'meeting':
                    suggestion = `Schedule a meeting tomorrow at 10 AM`;
                    break;
                case 'exam':
                    suggestion = `Schedule an exam next week`;
                    break;
                case 'assignment':
                    suggestion = `Schedule time to work on assignment tomorrow at 3 PM`;
                    break;
            }
            
            eventInput.value = suggestion;
            eventInput.focus();
            
            // Add a subtle animation to the input
            eventInput.style.transform = 'scale(1.02)';
            setTimeout(() => {
                eventInput.style.transform = 'scale(1)';
            }, 200);
        });
    });

    // Update event count
    const updateEventCount = (count) => {
        if (eventCountSpan) {
            eventCountSpan.textContent = count || '0';
        }
    };

    // Handle conflict resolution
    const handleConflicts = async (result) => {
        const conflicts = result.conflicts;
        
        // Get AI suggestions for alternatives
        for (const conflict of conflicts) {
            await showConflictResolutionDialog(conflict);
        }
    };

    // Show enhanced conflict resolution dialog with AI suggestions
    const showConflictResolutionDialog = async (conflict) => {
        const proposed = conflict.proposed_event;
        const conflictDetails = conflict.conflicts.map(c => 
            `• ${c.existing_event.summary} (${c.overlap_minutes} min overlap)`
        ).join('\n');
        
        // Create a custom dialog
        const dialogHtml = `
            <div class="conflict-dialog" id="conflict-dialog">
                <h3>⚠️ Scheduling Conflict Detected</h3>
                <div class="conflict-details">
                    <p><strong>Proposed Event:</strong> "${proposed.summary}"</p>
                    <p><strong>Requested Time:</strong> ${formatDateTime(proposed.start_time)} - ${formatDateTime(proposed.end_time)}</p>
                    <p><strong>Conflicts with:</strong></p>
                    <div class="conflict-list">
                        ${conflict.conflicts.map(c => `
                            <div class="conflict-item">
                                ${c.existing_event.summary} (${c.overlap_minutes} min overlap)
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="loading-alternatives">
                    <p>🤖 AI is finding alternative times...</p>
                </div>
                <div class="resolution-options" id="resolution-options" style="display: none;">
                    <p><strong>Suggested alternatives:</strong></p>
                    <div id="alternatives-container"></div>
                    <div class="action-buttons">
                        <button id="force-original" class="force-btn">Force Original Time</button>
                        <button id="cancel-event" class="cancel-btn">Cancel</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add dialog to page
        const existingDialog = document.getElementById('conflict-dialog');
        if (existingDialog) {
            existingDialog.remove();
        }
        
        document.body.insertAdjacentHTML('beforeend', dialogHtml);
        
        // Get AI alternatives
        try {
            const response = await fetch('/get_alternatives', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    proposed_event: proposed,
                    conflicts: conflict.conflicts
                }),
            });
            
            const result = await response.json();
            
            // Hide loading, show options
            document.querySelector('.loading-alternatives').style.display = 'none';
            document.getElementById('resolution-options').style.display = 'block';
            
            if (result.alternatives && result.alternatives.length > 0) {
                displayAlternatives(result.alternatives, proposed);
            } else if (result.new_event_alternatives || result.existing_event_alternatives) {
                displayEnhancedAlternatives(result, proposed);
            } else {
                document.getElementById('alternatives-container').innerHTML = 
                    '<p>No suitable alternatives found. You can force the original time or cancel.</p>';
            }
            
        } catch (error) {
            document.querySelector('.loading-alternatives').innerHTML = 
                '<p>❌ Error getting alternatives. You can force the original time or cancel.</p>';
            document.getElementById('resolution-options').style.display = 'block';
        }
        
        // Set up event listeners
        document.getElementById('force-original').onclick = () => {
            forceScheduleEvent(proposed);
            removeConflictDialog();
        };
        
        document.getElementById('cancel-event').onclick = () => {
            showStatus(schedulerStatus, 'Event cancelled due to conflicts.', false);
            removeConflictDialog();
        };
    };

    // Display alternative time options (legacy format for backward compatibility)
    const displayAlternatives = (alternatives, proposedEvent) => {
        const container = document.getElementById('alternatives-container');
        
        const alternativeButtons = alternatives.map((alt, index) => `
            <button class="alternative-btn" data-alternative='${JSON.stringify(alt)}' data-summary='${proposedEvent.summary}'>
                <div class="alt-option">${alt.option}</div>
                <div class="alt-time">${formatDateTime(alt.start_time)} - ${formatDateTime(alt.end_time)}</div>
                <div class="alt-reason">${alt.reason}</div>
            </button>
        `).join('');
        
        container.innerHTML = alternativeButtons;
        
        // Add click handlers for alternative buttons
        container.querySelectorAll('.alternative-btn').forEach(btn => {
            btn.onclick = async () => {
                const alternative = JSON.parse(btn.dataset.alternative);
                const summary = btn.dataset.summary;
                await scheduleAlternative(summary, alternative);
                removeConflictDialog();
            };
        });
    };

    // Display enhanced alternatives with options to move new or existing events
    const displayEnhancedAlternatives = (result, proposedEvent) => {
        const container = document.getElementById('alternatives-container');
        
        let html = '';
        
        // New event alternatives section
        if (result.new_event_alternatives && result.new_event_alternatives.length > 0) {
            html += `
                <div class="alternatives-section">
                    <h4>📅 Move Your New Event</h4>
                    <p class="section-description">Keep existing events in place, move "${proposedEvent.summary}" to:</p>
                    <div class="alternatives-group">
            `;
            
            result.new_event_alternatives.forEach(alt => {
                html += `
                    <button class="alternative-btn new-event-alt" data-alternative='${JSON.stringify(alt)}' data-summary='${proposedEvent.summary}'>
                        <div class="alt-option">${alt.option}</div>
                        <div class="alt-time">${formatDateTime(alt.start_time)} - ${formatDateTime(alt.end_time)}</div>
                        <div class="alt-reason">${alt.reason}</div>
                    </button>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        // Existing event alternatives section
        if (result.existing_event_alternatives && result.existing_event_alternatives.length > 0) {
            html += `
                <div class="alternatives-section">
                    <h4>🔄 Move Existing Event</h4>
                    <p class="section-description">Keep your requested time, move conflicting event to:</p>
                    <div class="alternatives-group">
            `;
            
            result.existing_event_alternatives.forEach(alt => {
                html += `
                    <button class="alternative-btn existing-event-alt" 
                            data-existing-event-id='${alt.existing_event_id}'
                            data-existing-title='${alt.existing_event_title}'
                            data-new-start='${alt.new_start_time}'
                            data-new-end='${alt.new_end_time}'
                            data-proposed-event='${JSON.stringify(proposedEvent)}'>
                        <div class="alt-option">${alt.option}</div>
                        <div class="alt-existing-title">Move: "${alt.existing_event_title}"</div>
                        <div class="alt-time">${formatDateTime(alt.new_start_time)} - ${formatDateTime(alt.new_end_time)}</div>
                        <div class="alt-reason">${alt.reason}</div>
                    </button>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = html;
        
        // Add click handlers for new event alternatives
        container.querySelectorAll('.new-event-alt').forEach(btn => {
            btn.onclick = async () => {
                const alternative = JSON.parse(btn.dataset.alternative);
                const summary = btn.dataset.summary;
                await scheduleAlternative(summary, alternative);
                removeConflictDialog();
            };
        });
        
        // Add click handlers for existing event alternatives
        container.querySelectorAll('.existing-event-alt').forEach(btn => {
            btn.onclick = async () => {
                const existingEventId = btn.dataset.existingEventId;
                const existingTitle = btn.dataset.existingTitle;
                const newStart = btn.dataset.newStart;
                const newEnd = btn.dataset.newEnd;
                const proposedEvent = JSON.parse(btn.dataset.proposedEvent);
                
                await moveExistingEvent(existingEventId, existingTitle, newStart, newEnd, proposedEvent);
                removeConflictDialog();
            };
        });
    };

    // Move existing event to new time and schedule new event at original time
    const moveExistingEvent = async (existingEventId, existingTitle, newStart, newEnd, proposedEvent) => {
        try {
            const response = await fetch('/move_existing_event', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    existing_event_id: existingEventId,
                    new_start_time: newStart,
                    new_end_time: newEnd,
                    proposed_event: proposedEvent
                }),
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showStatus(schedulerStatus, result.message, true);
                eventInput.value = '';
                fetchTasks();
                refreshCalendar();
            } else {
                showStatus(schedulerStatus, `Error: ${result.error}`, false);
            }
        } catch (error) {
            showStatus(schedulerStatus, `Network error: ${error.message}`, false);
        }
    };

    // Schedule at alternative time
    const scheduleAlternative = async (summary, alternative) => {
        try {
            const response = await fetch('/schedule_alternative', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    summary: summary,
                    start_time: alternative.start_time,
                    end_time: alternative.end_time
                }),
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showStatus(schedulerStatus, result.message, true);
                eventInput.value = '';
                fetchTasks();
                refreshCalendar();
            } else {
                showStatus(schedulerStatus, `Error: ${result.error}`, false);
            }
        } catch (error) {
            showStatus(schedulerStatus, `Network error: ${error.message}`, false);
        }
    };

    // Force schedule the original event
    const forceScheduleEvent = async (proposedEvent) => {
        try {
            const response = await fetch('/force_schedule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ event: proposedEvent }),
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showStatus(schedulerStatus, result.message, true);
                eventInput.value = '';
                fetchTasks();
                refreshCalendar();
            } else {
                showStatus(schedulerStatus, `Error: ${result.error}`, false);
            }
        } catch (error) {
            showStatus(schedulerStatus, `Network error: ${error.message}`, false);
        }
    };

    // Remove conflict dialog
    const removeConflictDialog = () => {
        const dialog = document.getElementById('conflict-dialog');
        if (dialog) {
            dialog.remove();
        }
    };

    // Format datetime for display
    const formatDateTime = (isoString) => {
        try {
            return new Date(isoString).toLocaleString('en-US', {
                weekday: 'short',
                month: 'short', 
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
        } catch {
            return isoString;
        }
    };

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
                refreshCalendar(); // Refresh the calendar
            } else if (response.status === 409) {
                // Conflict detected
                handleConflicts(result);
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
        // Show loading state
        tasksUl.innerHTML = `
            <li class="task-item loading-task">
                <div class="task-content">
                    <div class="loading-spinner"></div>
                    <span class="task-title">Loading tasks...</span>
                </div>
            </li>
        `;
        tasksStatus.style.display = 'none';
        if (emptyTasksDiv) emptyTasksDiv.style.display = 'none';

        try {
            const response = await fetch('/tasks');
            const tasks = await response.json();

            tasksUl.innerHTML = ''; // Clear the list

            if (tasks.length === 0) {
                if (emptyTasksDiv) {
                    emptyTasksDiv.style.display = 'flex';
                }
                updateEventCount(0);
            } else {
                if (emptyTasksDiv) {
                    emptyTasksDiv.style.display = 'none';
                }
                updateEventCount(tasks.length);

                tasks.forEach((task, index) => {
                    const li = document.createElement('li');
                    li.className = 'task-item';

                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.className = 'task-checkbox';
                    checkbox.id = `task-${index}`;

                    const taskContent = document.createElement('div');
                    taskContent.className = 'task-content';

                    const taskTitle = document.createElement('div');
                    taskTitle.className = 'task-title';
                    taskTitle.textContent = task.summary;

                    const taskTime = document.createElement('div');
                    taskTime.className = 'task-time';
                    taskTime.textContent = task.start_time;

                    taskContent.appendChild(taskTitle);
                    taskContent.appendChild(taskTime);

                    li.appendChild(checkbox);
                    li.appendChild(taskContent);

                    // Load completion state from localStorage
                    const taskKey = `${task.summary}-${task.start_time}`;
                    const isCompleted = localStorage.getItem(taskKey) === 'true';
                    if (isCompleted) {
                        li.classList.add('completed');
                        checkbox.checked = true;
                    }

                    // Add click listener to toggle completed state
                    li.addEventListener('click', (e) => {
                        // Don't toggle if clicking on a link or button inside the li
                        if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') return;

                        li.classList.toggle('completed');
                        // Also toggle the checkbox state
                        const cb = li.querySelector('input[type="checkbox"]');
                        if (cb) {
                            // If the click was not on the checkbox itself, sync its state
                            if (e.target !== cb) {
                                cb.checked = !cb.checked;
                            }
                            // Save state to localStorage
                            const completed = cb.checked;
                            localStorage.setItem(taskKey, completed.toString());
                        }
                    });

                    tasksUl.appendChild(li);
                });
            }
        } catch (error) {
            showStatus(tasksStatus, `Error fetching tasks: ${error.message}`, false);
            tasksUl.innerHTML = ''; // Clear loading message
            updateEventCount(0);
        }
    };
                        // Also toggle the checkbox state
                        const cb = li.querySelector('input[type="checkbox"]');
                        if (cb) {
                            // If the click was not on the checkbox itself, sync its state
                            if (e.target !== cb) {
                                cb.checked = !cb.checked;
                            }
                            // Save state to localStorage
                            const completed = cb.checked;
                            localStorage.setItem(taskKey, completed.toString());
                        }
                    });

                    tasksUl.appendChild(li);
                });
            }
        } catch (error) {
            showStatus(tasksStatus, `Error fetching tasks: ${error.message}`, false);
            tasksUl.innerHTML = ''; // Clear loading message
            updateEventCount(0);
        }
    };

    // --- Event Listeners ---
    refreshTasksButton.addEventListener('click', () => {
        fetchTasks();
        refreshCalendar();
    });

    // Initialize calendar and fetch tasks on initial page load
    initializeCalendar();
    fetchTasks();
});
