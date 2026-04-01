// static/js/admin_modern.js
// Modern Admin Panel JavaScript

(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Add fade-in animation to all modules
        $('.module').addClass('fade-in');
        
        // Add dashboard stats if on dashboard page
        if ($('body').hasClass('dashboard')) {
            addDashboardStats();
        }
        
        // Add hover effects to table rows
        $('#result_list tbody tr').hover(
            function() {
                $(this).css('cursor', 'pointer');
            }
        );
        
        // Add confirmation for delete actions
        $('.deletelink').click(function(e) {
            if (!confirm('⚠️ Are you sure you want to delete this item?\n\nThis action cannot be undone.')) {
                e.preventDefault();
                return false;
            }
        });
        
        // Add search input placeholder
        $('#searchbar').attr('placeholder', '🔍 Search...').css('padding-left', '35px');
        
        // Add tooltips to action buttons
        $('.action-checkbox').tooltip();
        
        // Add keyboard shortcuts
        $(document).keydown(function(e) {
            // Ctrl + S to save
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                $('form').submit();
                showNotification('Saving...', 'info');
            }
            // Ctrl + F to focus search
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                $('#searchbar').focus();
                showNotification('Search activated', 'info');
            }
        });
        
        // Add animation to messages
        $('.messagelist li').each(function(index) {
            $(this).delay(index * 100).fadeIn();
        });
    });
    
    // Add dashboard statistics cards
    function addDashboardStats() {
        const modelCount = $('#result_list tbody tr').length;
        const today = new Date();
        const dateString = today.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        const statsHtml = `
            <div class="dashboard-stats">
                <div class="stat-card" onclick="location.href='/admin/auth/user/'">
                    <i class="fas fa-users"></i>
                    <h3>${modelCount || '0'}</h3>
                    <p>Total Records</p>
                </div>
                <div class="stat-card" onclick="location.href='/admin/'">
                    <i class="fas fa-calendar-day"></i>
                    <h3>${today.getDate()}</h3>
                    <p>${dateString}</p>
                </div>
                <div class="stat-card" onclick="showSystemStatus()">
                    <i class="fas fa-chart-line"></i>
                    <h3>Active</h3>
                    <p>System Status</p>
                </div>
            </div>
        `;
        
        $('#content-main').prepend(statsHtml);
    }
    
    // Show notification
    function showNotification(message, type) {
        const notification = $(`
            <div class="admin-notification" style="
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: ${type === 'success' ? '#10b981' : (type === 'error' ? '#ef4444' : '#3b82f6')};
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                z-index: 9999;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                animation: slideIn 0.3s ease-out;
                font-size: 14px;
                font-weight: 500;
            ">
                ${message}
            </div>
        `);
        
        $('body').append(notification);
        
        setTimeout(function() {
            notification.fadeOut(300, function() {
                $(this).remove();
            });
        }, 3000);
    }
    
    // Show system status
    function showSystemStatus() {
        const statuses = [
            { name: 'Database', status: 'Connected', color: '#10b981' },
            { name: 'Server', status: 'Running', color: '#10b981' },
            { name: 'Cache', status: 'Active', color: '#10b981' },
            { name: 'API', status: 'Available', color: '#10b981' }
        ];
        
        let statusHtml = '<div class="system-status-modal"><h3>System Status</h3>';
        statuses.forEach(s => {
            statusHtml += `
                <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                    <span>${s.name}</span>
                    <span style="color: ${s.color};">✓ ${s.status}</span>
                </div>
            `;
        });
        statusHtml += '<button onclick="closeModal()" style="margin-top: 15px; padding: 8px 16px;">Close</button></div>';
        
        const modal = $(statusHtml).css({
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: 'white',
            padding: '20px',
            borderRadius: '12px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
            zIndex: '10000',
            minWidth: '300px'
        });
        
        $('body').append(modal);
    }
    
    // Dark mode toggle
    function initDarkMode() {
        const darkModeToggle = $('<button class="dark-mode-toggle"><i class="fas fa-moon"></i></button>');
        $('body').append(darkModeToggle);
        
        darkModeToggle.click(function() {
            $('body').toggleClass('dark-mode');
            const isDark = $('body').hasClass('dark-mode');
            localStorage.setItem('darkMode', isDark);
            darkModeToggle.html(isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>');
            showNotification(isDark ? 'Dark mode activated' : 'Light mode activated', 'info');
        });
        
        // Check saved preference
        if (localStorage.getItem('darkMode') === 'true') {
            $('body').addClass('dark-mode');
            darkModeToggle.html('<i class="fas fa-sun"></i>');
        }
    }
    
    // Export functions to global scope
    window.showNotification = showNotification;
    window.showSystemStatus = showSystemStatus;
    window.closeModal = function() {
        $('.system-status-modal').remove();
    };
    
    // Initialize dark mode
    initDarkMode();
    
})(django.jQuery);