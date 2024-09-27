// Function to load Google Analytics
function loadGoogleAnalytics() {
  console.log('GA script loading')
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  gtag('js', new Date());

  // Google Analytics ID (YOUR ID)
  gtag('config', 'UA-265858191-1'); // This is your Google Analytics ID
}

// Function to check user's cookie consent status
function checkCookieConsent() {
  const consent = localStorage.getItem('cookieConsent');

  if (consent === 'accepted') {
    loadGoogleAnalytics();  // Load Google Analytics if consent was previously accepted
  } else if (!consent) {
    document.getElementById('cookie-consent-banner').style.display = 'block'; // Show banner if no consent found
  }
}

// Wait for DOM to fully load
document.addEventListener('DOMContentLoaded', function () {
  // Accept cookies and load Google Analytics
  document.getElementById('accept-cookies').addEventListener('click', function () {
    localStorage.setItem('cookieConsent', 'accepted');
    loadGoogleAnalytics();  // Load Google Analytics on acceptance
    document.getElementById('cookie-consent-banner').style.display = 'none';  // Hide banner
  });

  // Decline cookies and hide the banner
  document.getElementById('decline-cookies').addEventListener('click', function () {
    localStorage.setItem('cookieConsent', 'declined');
    document.getElementById('cookie-consent-banner').style.display = 'none';  // Hide banner
  });

  // Check consent status when page loads
  checkCookieConsent();
});
