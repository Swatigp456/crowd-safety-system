// static/js/admin_custom.js
// Admin panel custom JavaScript

(function($) {
    'use strict';
    
    // Add fade-in animation to all modules
    $(document).ready(function() {
        // Add animation classes
        $('.module').addClass('fade-in');
        $('#changelist').addClass('fade-in');
        
        // Add tooltips to buttons
        $('.button, input[type="submit"]').each(function() {
            if (!$(this).attr('title')) {
                $(this).attr('title', $(this).text());
            }
        });
        
        // Enhance filter sidebar
        $('#changelist-filter').addClass('modern-filter');
        
        // Add hover effects to table rows
        $('#result_list tbody tr').hover(
            function() {
                $(this).css('background', '#f8f9fa');
            },
            function() {
                $(this).css('background', '');
            }
        );
        
        // Add confirmation for delete actions
        $('.deletelink').click(function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
                return false;
            }
        });
        
        // Add search input styling
        $('#searchbar').addClass('modern-search').attr('placeholder', 'Search...');
        
        // Add count badge to filter links
        $('#changelist-filter a').each(function() {
            let text = $(this).text();
            if (text.match(/\d+/)) {
                $(this).addClass('filter-link-with-count');
            }
        });
        
        // Add date picker enhancements
        $('.vDateField, .vTimeField').addClass('modern-datepicker');
        
        // Show loading effect on form submit
        $('form').submit(function() {
            let submitBtn = $(this).find('input[type="submit"]');
            if (submitBtn.length) {
                submitBtn.prop('disabled', true).text('Processing...');
                setTimeout(function() {
                    submitBtn.prop('disabled', false).text(submitBtn.data('original-text') || 'Save');
                }, 5000);
            }
        });
        
        // Add dashboard stats cards
        if ($('body').hasClass('dashboard')) {
            addDashboardStats();
        }
    });
    
    // Add dashboard statistics cards
    function addDashboardStats() {
        let statsHtml = `
            <div class="dashboard-stats" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 15px;">
                    <i class="fas fa-users" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <h3 style="margin: 0; font-size: 2rem;">${$('#result_list tbody tr').length || '0'}</h3>
                    <p style="margin: 0;">Total Records</p>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 15px;">
                    <i class="fas fa-clock" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <h3 style="margin: 0; font-size: 2rem;">${new Date().toLocaleDateString()}</h3>
                    <p style="margin: 0;">Last Updated</p>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; border-radius: 15px;">
                    <i class="fas fa-chart-line" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <h3 style="margin: 0; font-size: 2rem;">Active</h3>
                    <p style="margin: 0;">System Status</p>
                </div>
            </div>
        `;
        
        $('#content-main').prepend(statsHtml);
    }
    
    // Add keyboard shortcuts
    $(document).keydown(function(e) {
        // Ctrl + S to save
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            $('form').submit();
        }
        // Ctrl + F to focus search
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            $('#searchbar').focus();
        }
    });
    
    // Add notification for successful actions
    function showNotification(message, type) {
        let notification = $(`
            <div class="admin-notification" style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${type === 'success' ? '#28a745' : '#dc3545'};
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                z-index: 9999;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                animation: slideIn 0.3s ease-out;
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
    
})(django.jQuery);