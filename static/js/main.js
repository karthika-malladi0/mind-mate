// ==================== DARK MODE TOGGLE ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌙 Dark mode initializing...');
    
    // Initialize dark mode from localStorage
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        enableDarkMode();
    }

    // Add click listener to dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleDarkMode();
        });
    }
});

function toggleDarkMode() {
    const isDarkMode = document.body.classList.contains('dark-mode');
    if (isDarkMode) {
        disableDarkMode();
    } else {
        enableDarkMode();
    }
}

function enableDarkMode() {
    document.body.classList.add('dark-mode');
    localStorage.setItem('darkMode', 'true');
    updateDarkModeIcon(true);
    console.log('✅ Dark mode ENABLED');
}

function disableDarkMode() {
    document.body.classList.remove('dark-mode');
    localStorage.setItem('darkMode', 'false');
    updateDarkModeIcon(false);
    console.log('✅ Light mode ENABLED');
}

function updateDarkModeIcon(isDark) {
    const icon = document.getElementById('darkModeToggle');
    if (icon) {
        if (isDark) {
            icon.innerHTML = '<i class="fas fa-sun"></i>';
            icon.title = 'Switch to Light Mode';
        } else {
            icon.innerHTML = '<i class="fas fa-moon"></i>';
            icon.title = 'Switch to Dark Mode';
        }
    }
}

// ==================== NOTIFICATIONS ====================
function showNotification(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = `
        top: 100px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideInRight 0.3s ease-out;
    `;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// ==================== FORM VALIDATION ====================
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;

    form.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// ==================== CONFIRM DIALOG ====================
function showConfirmDialog(title, message, onConfirm) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'confirmModal_' + Date.now();
    modal.tabIndex = -1;
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    ${message}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-danger" id="confirmBtn">Confirm</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    const confirmModal = new bootstrap.Modal(modal);

    document.getElementById('confirmBtn').addEventListener('click', () => {
        onConfirm();
        confirmModal.hide();
        setTimeout(() => modal.remove(), 300);
    });

    confirmModal.show();
}

// ==================== LOADING STATE ====================
function setLoadingState(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Loading...`;
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || 'Submit';
    }
}

// ==================== SMOOTH SCROLL ====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#' && document.querySelector(href)) {
            e.preventDefault();
            document.querySelector(href).scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// ==================== ANIMATION ON SCROLL ====================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const fadeobserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
            fadeobserver.unobserve(entry.target);
        }
    });
}, observerOptions)

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.card, .stat-card, .btn').forEach(el => {
        fadeobserver.observe(el);
    });
});

// ==================== TOAST NOTIFICATION ====================
function showToast(message, icon = '✓') {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        z-index: 9999;
        animation: slideInRight 0.3s ease-out;
        display: flex;
        gap: 10px;
        align-items: center;
    `;
    toast.innerHTML = `
        <span>${icon}</span>
        <span>${message}</span>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInLeft 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==================== COPY TO CLIPBOARD ====================
function copyToClipboard(text, message = 'Copied!') {
    navigator.clipboard.writeText(text).then(() => {
        showToast(message, '📋');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// ==================== FORMAT NUMBERS ====================
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

// ==================== DEBOUNCE FUNCTION ====================
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== LOCAL STORAGE HELPERS ====================
const storage = {
    set: (key, value) => {
        localStorage.setItem(key, JSON.stringify(value));
    },
    get: (key) => {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    },
    remove: (key) => {
        localStorage.removeItem(key);
    },
    clear: () => {
        localStorage.clear();
    }
};

// ==================== API HELPER ====================
async function apiCall(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        const result = await response.json();

        if (!response.ok) {
            showNotification(result.error || 'An error occurred', 'danger');
            return null;
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        showNotification('Network error. Please try again.', 'danger');
        return null;
    }
}

// ==================== FORMAT DATE ====================
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// ==================== TIME AGO ====================
function timeAgo(dateString) {
    const date = new Date(dateString);
    const seconds = Math.floor((new Date() - date) / 1000);

    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + 'y ago';

    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + 'mo ago';

    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + 'd ago';

    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + 'h ago';

    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + 'm ago';

    return 'just now';
}

// ==================== MOOD EMOJI SELECTOR ====================
function getMoodEmoji(moodScore) {
    if (moodScore <= 2) return '😢';
    if (moodScore <= 4) return '😟';
    if (moodScore <= 6) return '😐';
    if (moodScore <= 8) return '😊';
    return '😄';
}

// ==================== RANDOM QUOTE ====================
function getRandomQuote() {
    const quotes = [
        "Your mental health is a priority, not a luxury.",
        "It's okay to not be okay.",
        "Progress, not perfection.",
        "You are stronger than you think.",
        "Take care of your mind. It's the only one you get.",
        "Small steps still move you forward.",
        "You deserve to be happy.",
        "Growth takes time and patience.",
        "Your feelings are valid.",
        "Every day is a fresh start."
    ];
    return quotes[Math.floor(Math.random() * quotes.length)];
}

// ==================== NAVBAR ACTIVE LINK ====================
document.addEventListener('DOMContentLoaded', function() {
    const currentLocation = location.pathname;
    const navLinks = document.querySelectorAll('.navbar-custom .nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (currentLocation === href) {
            link.classList.add('active');
        }
    });
});

// ==================== TABLE PAGINATION ====================
function paginateTable(tableId, rowsPerPage) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');
    const totalPages = Math.ceil(rows.length / rowsPerPage);

    rows.forEach(row => row.style.display = 'none');

    function showPage(pageNum) {
        const start = (pageNum - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        rows.forEach((row, index) => {
            if (index >= start && index < end) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    showPage(1);
}

// ==================== COUNTDOWN TIMER ====================
function startCountdown(targetDate, elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    function updateTimer() {
        const now = new Date().getTime();
        const distance = new Date(targetDate).getTime() - now;

        if (distance < 0) {
            element.textContent = 'Time is up!';
            return;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        element.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
    }

    updateTimer();
    setInterval(updateTimer, 1000);
}

// ==================== PREVENT DOUBLE SUBMIT ====================
document.addEventListener('submit', function(e) {
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    if (submitBtn) {
        submitBtn.dataset.originalText = submitBtn.innerHTML;
        submitBtn.addEventListener('click', function() {
            if (!form.classList.contains('submitted')) {
                form.classList.add('submitted');
                setLoadingState(submitBtn, true);

                setTimeout(() => {
                    form.classList.remove('submitted');
                    setLoadingState(submitBtn, false);
                }, 3000);
            }
        });
    }
});

// ==================== EXPORT HELPERS ====================
function exportToCSV(data, filename) {
    let csv = '';
    
    const headers = Object.keys(data[0]);
    csv += headers.join(',') + '\n';
    
    data.forEach(row => {
        csv += headers.map(header => `"${row[header]}"`).join(',') + '\n';
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
}

function exportToJSON(data, filename) {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
}

// ==================== PRINT PAGE ====================
function printPage() {
    window.print();
}

console.log('✅ Mind Mate App Loaded Successfully!');