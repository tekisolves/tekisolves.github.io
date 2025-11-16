// config.js
// Unified configuration for navbar.js (ENV object)
// Auto-detects local file:// vs production and exposes global ENV

(function () {
    function ensureSlash(url) {
        if (!url) return url;
        return url.endsWith('/') ? url : url + '/';
    }

    const LOCAL_BASE = "file:///C:/www/tekisolves.github.io/";
    const PROD_BASE = "https://tekisolves.github.io/";

    const isLocal = window.location.protocol === "file:";
    const BASE = ensureSlash(isLocal ? LOCAL_BASE : PROD_BASE);

    const LINKS = {
        HOME: "",
        BLOG: "/blog/index.html",
        PRODUCTS: {
            ROADMAP: "resources/products/beginner-software-engineering-roadmap-guide-2025.html",
            REACT: "resources/products/30-react-interview-questions-guide.html"
        }
    };

    window.ENV = {
        BASE_URL: BASE,
        LINKS: LINKS
    };
})();
