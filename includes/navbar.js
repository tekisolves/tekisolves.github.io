// resources/include-navbar.js
function includeNavbar() {
    const navbarHTML = `
        <header>
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top" style="border-bottom:0.8px solid gold;">
                <div class="container">
                    <a class="navbar-brand" href="${ENV.BASE_URL + ENV.LINKS.HOME}">Teki Solves</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown"
                        aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse justify-content-end" id="navbarNavDropdown">
                        <ul class="navbar-nav">
                            <li class="nav-item">
                                <a class="nav-link" href="${ENV.BASE_URL + ENV.LINKS.BLOG}">Blog</a>
                            </li>
                            <li class="nav-item dropdown">
                                <a class="nav-link dropdown-toggle" href="#" id="productsDropdown" role="button"
                                    data-bs-toggle="dropdown" aria-expanded="false">
                                    Products
                                </a>
                                <ul class="dropdown-menu" aria-labelledby="productsDropdown">
                                    <li><a class="dropdown-item" href="${ENV.BASE_URL + ENV.LINKS.PRODUCTS.ROADMAP}">Beginner Software Engineering Guide 2025</a></li>
                                    <li><a class="dropdown-item" href="${ENV.BASE_URL + ENV.LINKS.PRODUCTS.REACT}">React Interview Prep</a></li>
                                </ul>
                            </li>
                            <!--<li class="nav-item">
                                <a class="nav-link" href="${ENV.BASE_URL + ENV.LINKS.ABOUT}">About</a>
                            </li>-->
                            <li class="nav-item dropdown">
                                <a class="nav-link" href="#">Analytics&nbsp;&nbsp;
                                    <input class="form-check-input" type="checkbox" id="cookieToggle">
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
        </header>
`;

    document.body.insertAdjacentHTML('afterbegin', navbarHTML);
}

// Call the function
includeNavbar();