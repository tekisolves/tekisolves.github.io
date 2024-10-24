document.addEventListener('DOMContentLoaded', function () {
  const cookieBanner = document.getElementById('cookie-consent-banner');
  const acceptButton = document.getElementById('accept-cookies');
  const declineButton = document.getElementById('decline-cookies');

  localStorage.removeItem('cookieConsent');

  // Show the banner if consent hasn't been given yet
  if (!localStorage.getItem('cookieConsentTS')) {
    cookieBanner.style.display = 'block';
  }

  // Accept cookies
  acceptButton.addEventListener('click', function () {
    localStorage.setItem('cookieConsentTS', 'accepted');
    cookieBanner.style.display = 'none';
    loadGoogleAnalytics();
  });

  // Decline cookies
  declineButton.addEventListener('click', function () {
    localStorage.setItem('cookieConsentTS', 'rejected');
    cookieBanner.style.display = 'none';
  });
});
