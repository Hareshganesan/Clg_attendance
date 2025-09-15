// app/static/js/main.js

// Function to initialize tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Function to initialize popovers
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Function to handle form validation styling
function initFormValidation() {
    // Example starter JavaScript for disabling form submissions if there are invalid fields
    'use strict';

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation');

    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        }, false);
    });
}

// Function to handle collapsible sidebar
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-collapsed');
        });
    }
}

// Initialize all components when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    initPopovers();
    initFormValidation();
    initSidebar();
    
    // Add animation class to cards
    const cards = document.querySelectorAll('.card-stats');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('shadow-lg');
        });
        card.addEventListener('mouseleave', function() {
            this.classList.remove('shadow-lg');
        });
    });
});

// Function to handle QR code scanning for attendance
function initQRScanner(elementId, callbackUrl) {
    if (!document.getElementById(elementId)) return;
    
    const html5QrCode = new Html5Qrcode(elementId);
    const config = { fps: 10, qrbox: { width: 250, height: 250 } };
    
    // Success callback
    const qrCodeSuccessCallback = (decodedText, decodedResult) => {
        // Stop scanning
        html5QrCode.stop();
        
        // Call the API to mark attendance
        fetch(callbackUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_code: decodedText
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', data.message);
                
                // Redirect to appropriate page after success
                if (data.redirect) {
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 2000);
                }
            } else {
                showAlert('danger', data.message);
                
                // Allow scanning again after error
                setTimeout(() => {
                    html5QrCode.start(
                        { facingMode: "environment" }, 
                        config,
                        qrCodeSuccessCallback,
                        qrCodeErrorCallback
                    );
                }, 3000);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'Error processing attendance. Please try again.');
            
            // Allow scanning again after error
            setTimeout(() => {
                html5QrCode.start(
                    { facingMode: "environment" }, 
                    config,
                    qrCodeSuccessCallback,
                    qrCodeErrorCallback
                );
            }, 3000);
        });
    };
    
    // Error callback
    const qrCodeErrorCallback = (errorMessage) => {
        // We don't need to do anything here
    };
    
    // Start scanning
    html5QrCode.start(
        { facingMode: "environment" }, 
        config,
        qrCodeSuccessCallback,
        qrCodeErrorCallback
    ).catch(err => {
        showAlert('danger', 'Unable to start camera. Please ensure you have given camera permissions.');
    });
}

// Function to show alerts
function showAlert(type, message) {
    const alertPlaceholder = document.getElementById('alert-placeholder');
    if (alertPlaceholder) {
        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        alertPlaceholder.appendChild(wrapper);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = wrapper.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    } else {
        alert(message);
    }
}
