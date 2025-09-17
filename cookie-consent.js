// ===============================
// Cookie Consent Management
// ===============================

// Clear old consent key for a fresh start (comment out after first run if needed)
// localStorage.removeItem('cookieConsentTSolves1');

// Grab elements
const banner = document.getElementById('cookie-banner');
const acceptBtn = document.getElementById('accept-cookies');
const declineBtn = document.getElementById('decline-cookies');
const cookieToggle = document.getElementById('cookieToggle');
const cookieToggleLabel = document.getElementById('cookieToggleLabel');

// -------------------------------
// Get Consent and Expiry
// -------------------------------
function getConsent() {
    const consentData = JSON.parse(localStorage.getItem('cookieConsentTSolves1'));
    if (!consentData) return null;
    return (consentData.expiry > Date.now()) ? consentData.value : null;
}

// -------------------------------
// Set Consent (12 months expiry)
// -------------------------------
function setConsent(value) {
    const expiry = Date.now() + 365 * 24 * 60 * 60 * 1000; // 12 months
    localStorage.setItem('cookieConsentTSolves1', JSON.stringify({ value, expiry }));
    banner.style.display = 'none';
    if (value === 'accepted') initAnalytics();
}

// -------------------------------
// Analytics Init
// -------------------------------
function initAnalytics() {
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    gtag('js', new Date());
    gtag('config', 'G-8NWH600XP9');
}

// -------------------------------
// Update Toggle Label & State
// -------------------------------
function updateToggleLabel() {
    const consent = getConsent();
    if (consent === 'accepted') {
        cookieToggle.checked = true;
        cookieToggleLabel.textContent = "Disable Analytics Cookies";
    } else {
        cookieToggle.checked = false;
        cookieToggleLabel.textContent = "Enable Analytics Cookies";
    }
}

// -------------------------------
// Event Listeners
// -------------------------------
acceptBtn.addEventListener('click', () => {
    setConsent('accepted');
    updateToggleLabel();
});

declineBtn.addEventListener('click', () => {
    setConsent('declined');
    updateToggleLabel();
});

cookieToggle.addEventListener('change', () => {
    if (cookieToggle.checked) {
        setConsent('accepted');
        cookieToggleLabel.textContent = "Disable Analytics Cookies";
        alert("Cookies accepted and analytics enabled.");
    } else {
        setConsent('declined');
        cookieToggleLabel.textContent = "Enable Analytics Cookies";
        alert("Cookies declined.");
    }
});

// -------------------------------
// Show Banner / Init Analytics
// -------------------------------
(function init() {
    const consent = getConsent();
    if (!consent) {
        banner.style.display = 'block';
    } else if (consent === 'accepted') {
        initAnalytics();
    }
    updateToggleLabel();
})();
