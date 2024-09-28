// Function to load Google Analytics
function loadGoogleAnalytics() {
  console.log("Attempting to load Google Analytics...");
  
  // Create script element to load Google Analytics
  var scriptTag = document.createElement('script');
  scriptTag.src = 'https://www.googletagmanager.com/gtag/js?id=UA-265858191-1'; // Your Google Analytics ID
  scriptTag.async = true;
  document.head.appendChild(scriptTag);
  
  // Log when the script successfully loads
  scriptTag.onload = function() {
    console.log("Google Analytics script loaded successfully.");
    
    // Initialize Google Analytics
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'UA-265858191-1'); // Your Google Analytics ID
  };
  
  // Log if the script fails to load
  scriptTag.onerror = function() {
    console.error("Failed to load Google Analytics script.");
  };
}

// Function to check user's cookie consent status
function checkCookieConsent() {
  const consent = localStorage.getItem('cookieConsent');
  console.log("Cookie consent status:", consent);  // Log consent status
  
  if (consent === 'accepted') {
    console.log("Consent accepted. Loading Google Analytics...");
    loadGoogleAnalytics();  // Load Google Analytics if consent was previously accepted
  } else if (!consent) {
    console.log("No consent found. Displaying consent banner...");
    document.getElementById('cookie-consent-banner').style.display = 'block'; // Show banner if no consent found
  }
}

// Wait for DOM to fully load
document.addEventListener('DOMContentLoaded', function () {
  console.log("DOM loaded. Setting up event listeners.");
  
  // Accept cookies and load Google Analytics
  document.getElementById('accept-cookies').addEventListener('click', function() {
    console.log("Cookies accepted by user.");
    localStorage.setItem('cookieConsent', 'accepted');
    loadGoogleAnalytics();  // Load Google Analytics on acceptance
    document.getElementById('cookie-consent-banner').style.display = 'none';  // Hide banner
  });

  // Decline cookies and hide the banner
  document.getElementById('decline-cookies').addEventListener('click', function() {
    console.log("Cookies declined by user.");
    localStorage.setItem('cookieConsent', 'declined');
    document.getElementById('cookie-consent-banner').style.display = 'none';  // Hide banner
  });

  // Check consent status when page loads
  checkCookieConsent();
});
