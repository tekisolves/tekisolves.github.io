document.addEventListener('DOMContentLoaded', function () {
  const cookieBanner = document.getElementById('cookie-consent-banner');
  const acceptButton = document.getElementById('accept-cookies');
  const declineButton = document.getElementById('decline-cookies');

  localStorage.removeItem('cookieConsentTSolves');

  // Show the banner if consent hasn't been given yet
  if (!localStorage.getItem('cookieConsentTSolves1')) {
    cookieBanner.style.display = 'block';
  }

  // Accept cookies
  acceptButton.addEventListener('click', function () {
    location.reload();
    localStorage.setItem('cookieConsentTSolves1', 'accepted');
    cookieBanner.style.display = 'none';
    //loadGoogleAnalytics();
  });

  // Decline cookies
  declineButton.addEventListener('click', function () {
    localStorage.setItem('cookieConsentTSolves1', 'rejected');
    cookieBanner.style.display = 'none';
  });
});