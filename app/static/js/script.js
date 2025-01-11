console.log("Plik script.js załadowany poprawnie!");

// Obsługa logowania
document.querySelector("#login-form")?.addEventListener("submit", async (event) => {
  event.preventDefault(); // Zatrzymuje domyślne przesyłanie formularza

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  console.log("Dane logowania:", { email, password }); // Debugowanie danych logowania

  try {
    // Wysyłanie żądania POST do backendu
    const response = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const result = await response.json();
    console.log("Odpowiedź serwera:", result); // Debugowanie odpowiedzi serwera

    if (response.ok) {
      alert(result.message); // Wyświetlenie komunikatu o sukcesie
      window.location.href = result.redirect_url; // Przekierowanie na stronę "Moje konto"
    } else {
      alert(result.message || "Nieprawidłowe dane logowania."); // Komunikat o błędzie
    }
  } catch (error) {
    console.error("Błąd podczas logowania:", error); // Wyświetlenie błędu w konsoli
    alert("Wystąpił problem z połączeniem. Spróbuj ponownie później.");
  }
});

// Pobieranie danych użytkownika i wyświetlanie na stronie "Moje konto"
async function loadAccountData() {
  try {
    const response = await fetch("/account", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      console.error("Nie udało się pobrać danych użytkownika.");
      return;
    }

    const data = await response.json();
    console.log("Dane użytkownika:", data);

    // Wyświetl dane użytkownika
    document.getElementById("user-name").textContent = data.name;
    document.getElementById("user-email").textContent = data.email;

    // Wyświetl przepisy użytkownika
    const recipesList = document.getElementById("recipes-list");
    data.recipes.forEach((recipe) => {
      const li = document.createElement("li");
      li.textContent = `${recipe.name} (${recipe.category})`;
      recipesList.appendChild(li);
    });

    // Wyświetl ulubione przepisy użytkownika
    const favoritesList = document.getElementById("favorites-list");
    data.favorites.forEach((favorite) => {
      const li = document.createElement("li");
      li.textContent = `${favorite.name} (${favorite.category})`;
      favoritesList.appendChild(li);
    });
  } catch (error) {
    console.error("Błąd podczas pobierania danych konta:", error);
  }
}

// Załaduj dane konta, jeśli jesteśmy na stronie "Moje konto"
if (window.location.pathname === "/account.html") {
  loadAccountData();
}

// Funkcja aktualizująca przyciski w nagłówku
async function updateNavButtons() {
  try {
    const response = await fetch("/is_logged_in", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    const data = await response.json();
    const userMenu = document.querySelector(".top-menu > div:last-child");
    const logoContainer = document.querySelector(".top-menu > div:first-child");

    // Zaktualizuj przyciski w menu użytkownika
    if (data.logged_in) {
      userMenu.innerHTML = `
        <a href="account.html" class="btn btn-outline-primary">Moje konto</a>
        <button class="btn btn-outline-danger" onclick="logout()">Wyloguj się</button>
      `;
    } else {
      userMenu.innerHTML = `
        <a href="login.html" class="btn btn-outline-success me-2">Logowanie</a>
        <a href="register.html" class="btn btn-outline-primary">Rejestracja</a>
      `;
    }

    // Dodaj logo, jeśli nie istnieje
    if (!logoContainer.querySelector("img")) {
      logoContainer.innerHTML = `
        <a href="index.html">
          <img src="static/images/logo.png" alt="Logo" class="logo">
        </a>
      `;
    }
  } catch (error) {
    console.error("Błąd podczas sprawdzania statusu logowania:", error);
  }
}

// Wywołaj funkcję po załadowaniu DOM
document.addEventListener("DOMContentLoaded", updateNavButtons);


// Funkcja wylogowania
async function logout() {
  try {
    const response = await fetch("/logout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    if (response.ok) {
      alert("Wylogowano pomyślnie.");
      window.location.href = "index.html"; // Przekierowanie na stronę główną po wylogowaniu
    } else {
      const errorData = await response.json();
      alert(errorData.message || "Wystąpił problem podczas wylogowywania.");
    }
  } catch (error) {
    console.error("Błąd podczas wylogowywania:", error);
    alert("Wystąpił problem z połączeniem. Spróbuj ponownie później.");
  }
}


// Podświetl aktywny przycisk w menu nawigacyjnym
function highlightActiveNav() {
  const navLinks = document.querySelectorAll(".main-nav a");
  const currentPath = window.location.pathname;

  navLinks.forEach((link) => {
    // Dopasuj dokładną ścieżkę lub obsłuż różne scenariusze w URL
    if (link.href.includes(currentPath)) {
      link.classList.add("active");
    } else {
      link.classList.remove("active"); // Usuń klasę "active" z innych linków
    }
  });
}

// Wywołaj funkcję podczas ładowania strony
document.addEventListener("DOMContentLoaded", highlightActiveNav);


// Wywołaj funkcję podczas ładowania strony
highlightActiveNav();
