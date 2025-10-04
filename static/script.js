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
                showEventDetails(info.event);
            },
            eventDidMount: function(info) {
                info.el.title = `${info.event.title}\n${info.event.start.toLocaleString()}`;
            },
            timeZone: 'local',
            locale: 'en',
            firstDay: 0,
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
                    <div class="event-details-actions">
                        <button class="delete-event-btn" data-event-id="${event.id}">
                            <i data-lucide="trash-2"></i>
                            Delete Event
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Handle delete button click
        const deleteBtn = modal.querySelector('.delete-event-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                showDeleteConfirmation(event, modal);
            });
        }
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    };

    // Function to show delete confirmation dialog
    const showDeleteConfirmation = (event, parentModal) => {
        const confirmModal = document.createElement('div');
        confirmModal.className = 'confirmation-modal';
        confirmModal.innerHTML = `
            <div class="confirmation-content">
                <div class="confirmation-header">
                    <div class="warning-icon">
                        <i data-lucide="alert-triangle"></i>
                    </div>
                    <h3>Delete Event?</h3>
                </div>
                <div class="confirmation-body">
                    <p>Are you sure you want to delete:</p>
                    <p class="event-title-confirm"><strong>"${event.title}"</strong></p>
                    <p class="warning-text">This action cannot be undone.</p>
                </div>
                <div class="confirmation-actions">
                    <button class="cancel-btn">
                        <i data-lucide="x"></i>
                        Cancel
                    </button>
                    <button class="confirm-delete-btn">
                        <i data-lucide="trash-2"></i>
                        Delete
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(confirmModal);
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        const cancelBtn = confirmModal.querySelector('.cancel-btn');
        const confirmBtn = confirmModal.querySelector('.confirm-delete-btn');

        cancelBtn.addEventListener('click', () => {
            confirmModal.remove();
        });

        confirmBtn.addEventListener('click', async () => {
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<i data-lucide="loader"></i> Deleting...';
            
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }

            try {
                const response = await fetch(`/delete_event/${event.id}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    // Show success message
                    showToast('Event deleted successfully', 'success');
                    // Close both modals
                    confirmModal.remove();
                    parentModal.remove();
                    // Refresh calendar
                    refreshCalendar();
                } else {
                    const data = await response.json();
                    showToast(data.error || 'Failed to delete event', 'error');
                    confirmBtn.disabled = false;
                    confirmBtn.innerHTML = '<i data-lucide="trash-2"></i> Delete';
                    if (typeof lucide !== 'undefined') {
                        lucide.createIcons();
                    }
                }
            } catch (error) {
                console.error('Error deleting event:', error);
                showToast('Error deleting event', 'error');
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = '<i data-lucide="trash-2"></i> Delete';
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }
        });

        confirmModal.addEventListener('click', (e) => {
            if (e.target === confirmModal) {
                confirmModal.remove();
            }
        });
    };

    // Function to show toast notifications
    const showToast = (message, type = 'info') => {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i data-lucide="${type === 'success' ? 'check-circle' : type === 'error' ? 'x-circle' : 'info'}"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(toast);
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Animate in
        setTimeout(() => toast.classList.add('toast-show'), 10);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('toast-show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
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
        
        for (const conflict of conflicts) {
            await showConflictResolutionDialog(conflict);
        }
    };

    // Show enhanced conflict resolution dialog with AI suggestions
    const showConflictResolutionDialog = async (conflict) => {
        const proposed = conflict.proposed_event;
        
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
                        <button id="split-task-btn" class="split-btn">✂️ Split into Smaller Blocks</button>
                        <button id="force-original" class="force-btn">Force Original Time</button>
                        <button id="cancel-event" class="cancel-btn">Cancel</button>
                    </div>
                </div>
            </div>
        `;
        
        const existingDialog = document.getElementById('conflict-dialog');
        if (existingDialog) {
            existingDialog.remove();
        }
        
        document.body.insertAdjacentHTML('beforeend', dialogHtml);
        
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
        
        document.getElementById('split-task-btn').onclick = async () => {
            await handleTaskSplitting(proposed);
        };
        
        document.getElementById('force-original').onclick = () => {
            forceScheduleEvent(proposed);
            removeConflictDialog();
        };
        
        document.getElementById('cancel-event').onclick = () => {
            showStatus(schedulerStatus, 'Event cancelled due to conflicts.', false);
            removeConflictDialog();
        };
    };

    // Display alternative time options
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
            
            html += '</div></div>';
        }
        
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
            
            html += '</div></div>';
        }
        
        container.innerHTML = html;
        
        container.querySelectorAll('.new-event-alt').forEach(btn => {
            btn.onclick = async () => {
                const alternative = JSON.parse(btn.dataset.alternative);
                const summary = btn.dataset.summary;
                await scheduleAlternative(summary, alternative);
                removeConflictDialog();
            };
        });
        
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

    // Handle task splitting
    const handleTaskSplitting = async (proposedEvent) => {
        const dialog = document.getElementById('conflict-dialog');
        if (dialog) {
            // Update dialog to show loading state
            dialog.innerHTML = `
                <h3>✂️ Analyzing Task Splitting Options</h3>
                <div class="loading-alternatives">
                    <p>🤖 AI is finding the best way to split your task...</p>
                </div>
            `;
        }
        
        try {
            const response = await fetch('/suggest_split', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ proposed_event: proposedEvent }),
            });
            
            const result = await response.json();
            
            if (response.ok) {
                displaySplitSuggestion(result, proposedEvent);
            } else {
                showStatus(schedulerStatus, `Error: ${result.error}`, false);
                removeConflictDialog();
            }
        } catch (error) {
            showStatus(schedulerStatus, `Network error: ${error.message}`, false);
            removeConflictDialog();
        }
    };

    // Display split task suggestion
    const displaySplitSuggestion = (splitSuggestion, originalEvent) => {
        const dialog = document.getElementById('conflict-dialog');
        if (!dialog) return;
        
        const suggestedEvents = splitSuggestion.suggested_events || [];
        const recommendation = splitSuggestion.recommendation || 'split_task';
        const reason = splitSuggestion.reason || 'AI analyzed your calendar for optimal scheduling';
        
        let eventsHtml = '';
        if (suggestedEvents.length > 0) {
            eventsHtml = suggestedEvents.map((event, index) => `
                <div class="split-event-item">
                    <div class="split-number">${index + 1}</div>
                    <div class="split-details">
                        <div class="split-title">${event.summary}</div>
                        <div class="split-time">${formatDateTime(event.start_time)} - ${formatDateTime(event.end_time)}</div>
                        <div class="split-duration">${event.duration_hours || calculateDuration(event.start_time, event.end_time)} hours</div>
                    </div>
                </div>
            `).join('');
        }
        
        const dialogHtml = `
            <h3>✂️ Task Splitting ${recommendation === 'single_block' ? '(Single Block Recommended)' : 'Suggestion'}</h3>
            <div class="split-suggestion-container">
                <div class="split-reason">
                    <strong>💡 Recommendation:</strong> ${reason}
                </div>
                
                <div class="split-comparison">
                    <div class="original-event">
                        <h4>Original Request:</h4>
                        <p><strong>${originalEvent.summary}</strong></p>
                        <p>${formatDateTime(originalEvent.start_time)} - ${formatDateTime(originalEvent.end_time)}</p>
                    </div>
                    
                    <div class="suggested-split">
                        <h4>Suggested Schedule:</h4>
                        <div class="split-events-list">
                            ${eventsHtml}
                        </div>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button id="accept-split" class="primary-btn">✓ Schedule Split Tasks</button>
                    <button id="cancel-split" class="cancel-btn">Cancel</button>
                </div>
            </div>
        `;
        
        dialog.innerHTML = dialogHtml;
        
        document.getElementById('accept-split').onclick = async () => {
            await scheduleSplitTasks(suggestedEvents);
        };
        
        document.getElementById('cancel-split').onclick = () => {
            showStatus(schedulerStatus, 'Task splitting cancelled.', false);
            removeConflictDialog();
        };
    };

    // Schedule split tasks
    const scheduleSplitTasks = async (splitEvents) => {
        const dialog = document.getElementById('conflict-dialog');
        if (dialog) {
            dialog.innerHTML = `
                <h3>⏳ Scheduling Split Tasks...</h3>
                <div class="loading-alternatives">
                    <p>Creating ${splitEvents.length} events...</p>
                </div>
            `;
        }
        
        try {
            const response = await fetch('/schedule_split', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ events: splitEvents }),
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showStatus(schedulerStatus, result.message, true);
                eventInput.value = '';
                fetchTasks();
                refreshCalendar();
                removeConflictDialog();
            } else {
                // Handle partial success (207 status)
                if (response.status === 207) {
                    const message = `${result.message}. Some events may have conflicts.`;
                    showStatus(schedulerStatus, message, result.created_count > 0);
                    if (result.created_count > 0) {
                        fetchTasks();
                        refreshCalendar();
                    }
                    removeConflictDialog();
                } else {
                    showStatus(schedulerStatus, `Error: ${result.error}`, false);
                    removeConflictDialog();
                }
            }
        } catch (error) {
            showStatus(schedulerStatus, `Network error: ${error.message}`, false);
            removeConflictDialog();
        }
    };

    // Calculate duration between two times in hours
    const calculateDuration = (startTime, endTime) => {
        const start = new Date(startTime);
        const end = new Date(endTime);
        const durationMs = end - start;
        const durationHours = durationMs / (1000 * 60 * 60);
        return durationHours.toFixed(1);
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
        element.className = 'status-message';
        if (isSuccess) {
            element.classList.add('success');
        } else {
            element.classList.add('error');
        }
    };

    // --- Fetch and display tasks ---
    const fetchTasks = async () => {
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

            tasksUl.innerHTML = '';

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

                    const taskKey = `${task.summary}-${task.start_time}`;
                    const isCompleted = localStorage.getItem(taskKey) === 'true';
                    if (isCompleted) {
                        li.classList.add('completed');
                        checkbox.checked = true;
                    }

                    li.addEventListener('click', (e) => {
                        if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') return;

                        li.classList.toggle('completed');
                        const cb = li.querySelector('input[type="checkbox"]');
                        if (cb) {
                            if (e.target !== cb) {
                                cb.checked = !cb.checked;
                            }
                            const completed = cb.checked;
                            localStorage.setItem(taskKey, completed.toString());
                        }
                    });

                    tasksUl.appendChild(li);
                });
            }
        } catch (error) {
            showStatus(tasksStatus, `Error fetching tasks: ${error.message}`, false);
            tasksUl.innerHTML = '';
            updateEventCount(0);
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
        scheduleButton.innerHTML = '<i data-lucide="loader-2" class="animate-spin"></i> Scheduling...';
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
                eventInput.value = '';
                fetchTasks();
                refreshCalendar();
            } else if (response.status === 409) {
                handleConflicts(result);
            } else {
                showStatus(schedulerStatus, `Error: ${result.error}`, false);
            }
        } catch (error) {
            showStatus(schedulerStatus, `Network error: ${error.message}`, false);
        } finally {
            scheduleButton.disabled = false;
            scheduleButton.innerHTML = '<span class="btn-text">Schedule</span><i data-lucide="sparkles" class="btn-icon"></i>';
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    });

    // --- Event Listeners ---
    refreshTasksButton.addEventListener('click', () => {
        fetchTasks();
        refreshCalendar();
    });

    // Enter key support for input
    eventInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            scheduleButton.click();
        }
    });

    // --- Feedback System ---
    console.log('🔍 Initializing Feedback System...');
    const teachFeedbackBtn = document.getElementById('teach-feedback-btn');
    const feedbackSection = document.getElementById('feedback-section');
    const closeFeedbackBtn = document.getElementById('close-feedback-btn');
    const submitFeedbackBtn = document.getElementById('submit-feedback-btn');
    const viewFeedbackBtn = document.getElementById('view-feedback-btn');
    const feedbackInput = document.getElementById('feedback-input');
    const feedbackStatus = document.getElementById('feedback-status');

    console.log('📋 Feedback elements:', {
        teachBtn: !!teachFeedbackBtn,
        section: !!feedbackSection,
        closeBtn: !!closeFeedbackBtn,
        submitBtn: !!submitFeedbackBtn,
        viewBtn: !!viewFeedbackBtn,
        input: !!feedbackInput,
        status: !!feedbackStatus
    });

    if (teachFeedbackBtn) {
        console.log('✅ Teach button found, adding click listener');
        teachFeedbackBtn.addEventListener('click', () => {
            console.log('🖱️ Teach button clicked!');
            const isVisible = feedbackSection.style.display !== 'none';
            console.log('Current visibility:', isVisible ? 'visible' : 'hidden');
            feedbackSection.style.display = isVisible ? 'none' : 'block';
            console.log('New state:', feedbackSection.style.display);
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        });
    } else {
        console.error('❌ Teach feedback button not found!');
    }

    if (closeFeedbackBtn) {
        closeFeedbackBtn.addEventListener('click', () => {
            feedbackSection.style.display = 'none';
            feedbackInput.value = '';
            feedbackStatus.style.display = 'none';
        });
    }

    if (submitFeedbackBtn) {
        submitFeedbackBtn.addEventListener('click', async () => {
            const feedbackText = feedbackInput.value.trim();
            if (!feedbackText) {
                showStatus(feedbackStatus, 'Please enter your feedback', false);
                return;
            }

            // Visual feedback - change section appearance
            feedbackSection.classList.add('feedback-processing');
            submitFeedbackBtn.disabled = true;
            submitFeedbackBtn.innerHTML = '<i data-lucide="loader-2" class="animate-spin"></i> <span>AI is learning...</span>';
            feedbackStatus.innerHTML = '<div class="feedback-processing-msg">🧠 Processing your feedback...</div>';
            feedbackStatus.style.display = 'block';

            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }

            try {
                const response = await fetch('/feedback/smart', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ feedback_text: feedbackText }),
                });

                const result = await response.json();

                if (response.ok) {
                    // Success animation
                    feedbackSection.classList.remove('feedback-processing');
                    feedbackSection.classList.add('feedback-success');
                    
                    // Show success message with animation
                    let statusHtml = `<div class="feedback-success-msg">
                        <div class="success-icon">✓</div>
                        <div class="success-text">${result.message}</div>
                    </div>`;
                    
                    // Show what was extracted if available
                    if (result.extracted) {
                        const extracted = result.extracted;
                        statusHtml += '<div class="extracted-info animate-in">';
                        statusHtml += '<div class="extracted-header">📋 What I learned:</div>';
                        if (extracted.class_name) {
                            statusHtml += `<div class="extracted-item"><span class="label">📚 Class:</span> <span class="value">${extracted.class_name}</span></div>`;
                        }
                        if (extracted.assignment_type) {
                            statusHtml += `<div class="extracted-item"><span class="label">📝 Type:</span> <span class="value">${extracted.assignment_type}</span></div>`;
                        }
                        if (extracted.duration_hours) {
                            statusHtml += `<div class="extracted-item"><span class="label">⏱️ Duration:</span> <span class="value">${extracted.duration_hours} hours</span></div>`;
                        }
                        statusHtml += '</div>';
                    } else if (result.note) {
                        statusHtml += `<div class="extracted-info animate-in">
                            <div class="info-note">💡 ${result.note}</div>
                        </div>`;
                    }
                    
                    feedbackStatus.innerHTML = statusHtml;
                    feedbackInput.value = '';
                    
                    // Remove success class after animation
                    setTimeout(() => {
                        feedbackSection.classList.remove('feedback-success');
                    }, 2000);
                } else {
                    feedbackSection.classList.remove('feedback-processing');
                    feedbackSection.classList.add('feedback-error');
                    feedbackStatus.innerHTML = `<div class="feedback-error-msg">
                        <div class="error-icon">✗</div>
                        <div class="error-text">Error: ${result.error}</div>
                    </div>`;
                    
                    setTimeout(() => {
                        feedbackSection.classList.remove('feedback-error');
                    }, 3000);
                }
            } catch (error) {
                feedbackSection.classList.remove('feedback-processing');
                feedbackSection.classList.add('feedback-error');
                feedbackStatus.innerHTML = `<div class="feedback-error-msg">
                    <div class="error-icon">✗</div>
                    <div class="error-text">Network error: ${error.message}</div>
                </div>`;
                
                setTimeout(() => {
                    feedbackSection.classList.remove('feedback-error');
                }, 3000);
            } finally {
                submitFeedbackBtn.disabled = false;
                submitFeedbackBtn.innerHTML = '<span>✓ Teach AI</span>';
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }
        });
    }

    if (viewFeedbackBtn) {
        viewFeedbackBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/feedback/view');
                const result = await response.json();

                if (response.ok) {
                    showFeedbackModal(result.summary, result.raw_data);
                } else {
                    showStatus(feedbackStatus, 'Error loading feedback', false);
                }
            } catch (error) {
                showStatus(feedbackStatus, `Network error: ${error.message}`, false);
            }
        });
    }

    // Show feedback modal
    const showFeedbackModal = (summary, rawData) => {
        const modal = document.createElement('div');
        modal.className = 'feedback-modal';
        
        const classPatterns = rawData.class_patterns || {};
        const typePatterns = rawData.assignment_type_patterns || {};
        const generalFeedback = rawData.general_feedback || [];
        
        let contentHtml = '<h3>📚 Learned Duration Patterns</h3>';
        
        if (Object.keys(classPatterns).length > 0) {
            contentHtml += '<div class="feedback-section-content"><h4>Class-Specific Patterns:</h4><ul>';
            for (const [className, assignments] of Object.entries(classPatterns)) {
                for (const [assignmentType, data] of Object.entries(assignments)) {
                    contentHtml += `<li><strong>${className} ${assignmentType}:</strong> ${data.typical_duration_hours} hours`;
                    if (data.notes) {
                        contentHtml += ` <em>(${data.notes})</em>`;
                    }
                    contentHtml += `</li>`;
                }
            }
            contentHtml += '</ul></div>';
        }
        
        if (Object.keys(typePatterns).length > 0) {
            contentHtml += '<div class="feedback-section-content"><h4>General Assignment Patterns:</h4><ul>';
            for (const [type, data] of Object.entries(typePatterns)) {
                contentHtml += `<li><strong>${type}:</strong> ${data.typical_duration_hours} hours`;
                if (data.notes) {
                    contentHtml += ` <em>(${data.notes})</em>`;
                }
                contentHtml += `</li>`;
            }
            contentHtml += '</ul></div>';
        }
        
        if (generalFeedback.length > 0) {
            contentHtml += '<div class="feedback-section-content"><h4>General Preferences:</h4><ul>';
            generalFeedback.slice(-10).forEach(item => {
                contentHtml += `<li>${item.text}</li>`;
            });
            contentHtml += '</ul></div>';
        }
        
        if (Object.keys(classPatterns).length === 0 && Object.keys(typePatterns).length === 0 && generalFeedback.length === 0) {
            contentHtml += '<p>No patterns learned yet. Start teaching the AI about your assignments!</p>';
        }
        
        modal.innerHTML = `
            <div class="feedback-modal-content">
                ${contentHtml}
                <button class="close-modal-btn primary-btn">Close</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        modal.querySelector('.close-modal-btn').onclick = () => modal.remove();
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    };

    // Initialize calendar and fetch tasks on initial page load
    initializeCalendar();
    fetchTasks();
});
