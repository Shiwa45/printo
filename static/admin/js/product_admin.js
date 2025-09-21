// Product Admin JavaScript for front/back design functionality

(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Handle design tool enabled/disabled state
        var $designToolEnabled = $('#id_design_tool_enabled');
        var $frontBackDesignEnabled = $('#id_front_back_design_enabled');
        
        function toggleFrontBackDesign() {
            if ($designToolEnabled.is(':checked')) {
                $frontBackDesignEnabled.prop('disabled', false);
                $frontBackDesignEnabled.closest('.form-row').removeClass('disabled');
            } else {
                $frontBackDesignEnabled.prop('disabled', true);
                $frontBackDesignEnabled.prop('checked', false);
                $frontBackDesignEnabled.closest('.form-row').addClass('disabled');
            }
        }
        
        // Initial state
        toggleFrontBackDesign();
        
        // Handle changes
        $designToolEnabled.change(function() {
            toggleFrontBackDesign();
            
            if (!$(this).is(':checked')) {
                // Show warning if disabling design tool with front/back enabled
                if ($frontBackDesignEnabled.is(':checked')) {
                    alert('Front/back design will be disabled when design tool is disabled.');
                }
            }
        });
        
        // Add visual styling for disabled state
        $('<style>')
            .prop('type', 'text/css')
            .html(`
                .form-row.disabled {
                    opacity: 0.5;
                }
                .form-row.disabled label {
                    color: #999;
                }
            `)
            .appendTo('head');
    });
    
})(django.jQuery);