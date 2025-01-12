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

function editUserName() {
  const newName = prompt("Podaj nowe imię i nazwisko:");
  if (newName) {
      fetch("/api/user/update_name", {
          method: "POST",
          headers: {
              "Content-Type": "application/json"
          },
          body: JSON.stringify({ name: newName })
      })
      .then(response => response.json())
      .then(data => {
          if (data.message) {
              document.getElementById("user-name").textContent = newName;
              alert("Imię i nazwisko zostały zaktualizowane.");
          } else {
              alert("Błąd: " + data.error);
          }
      })
      .catch(error => console.error("Błąd aktualizacji imienia i nazwiska:", error));
  }
}


function editUserEmail() {
  const newEmail = prompt("Podaj nowy adres e-mail:");
  if (newEmail) {
      fetch("/api/user/update_email", {
          method: "POST",
          headers: {
              "Content-Type": "application/json"
          },
          body: JSON.stringify({ email: newEmail })
      })
      .then(response => response.json())
      .then(data => {
          if (data.message) {
              document.getElementById("user-email").textContent = newEmail;
              alert("Adres e-mail został zaktualizowany.");
          } else {
              alert("Błąd: " + data.error);
          }
      })
      .catch(error => console.error("Błąd aktualizacji adresu e-mail:", error));
  }
}



function changeUserPassword() {
  const currentPassword = prompt("Podaj swoje obecne hasło:");
  const newPassword = prompt("Podaj nowe hasło (min. 8 znaków):");

  if (newPassword && newPassword.length >= 8) {
      fetch("/api/user/update_password", {
          method: "POST",
          headers: {
              "Content-Type": "application/json"
          },
          body: JSON.stringify({
              current_password: currentPassword,
              new_password: newPassword
          })
      })
      .then(response => response.json())
      .then(data => {
          if (data.message) {
              alert("Hasło zostało zmienione.");
          } else {
              alert("Błąd: " + data.error);
          }
      })
      .catch(error => console.error("Błąd zmiany hasła:", error));
  } else {
      alert("Hasło musi mieć co najmniej 8 znaków.");
  }
}



document.addEventListener("DOMContentLoaded", function () {
  fetch("/api/user")
      .then(response => response.json())
      .then(data => {
          document.getElementById("user-name").textContent = data.name || "Brak danych";
          document.getElementById("user-email").textContent = data.email || "Brak danych";
          document.getElementById("user-date").textContent = data.join_date || "Brak danych";
      })
      .catch(error => console.error("Błąd ładowania danych użytkownika:", error));
});


document.addEventListener("DOMContentLoaded", function () {
  // Sprawdzenie statusu zalogowania
  fetch("/is_logged_in")
      .then(response => response.json())
      .then(data => {
          if (data.logged_in) {
              // Pokaż sekcję ulubionych przepisów
              document.getElementById("favorites-section").style.display = "block";

              // Opcjonalnie: Załaduj ulubione przepisy
              loadFavoriteRecipes();
          }
      })
      .catch(error => console.error("Błąd sprawdzania statusu logowania:", error));
});

function loadFavoriteRecipes() {
  // Pobierz ulubione przepisy z backendu
  fetch("/account/data") // Zakładam, że endpoint zwraca ulubione przepisy
      .then(response => response.json())
      .then(data => {
          const favoritesContainer = document.getElementById("favorite-recipes");
          favoritesContainer.innerHTML = ""; // Wyczyść zawartość

          data.favorites.forEach(favorite => {
              const recipeDiv = document.createElement("div");
              recipeDiv.innerHTML = `
                  <div>
                      <h3>${favorite.name}</h3>
                      <p>Kategoria: ${favorite.category}</p>
                  </div>
              `;
              favoritesContainer.appendChild(recipeDiv);
          });
      })
      .catch(error => console.error("Błąd ładowania ulubionych przepisów:", error));
}


document.addEventListener("DOMContentLoaded", function () {
  // Sprawdź status logowania
  fetch("/is_logged_in")
      .then(response => response.json())
      .then(data => {
          const overlay = document.getElementById("favorites-overlay");

          if (data.logged_in) {
              // Ukryj nakładkę, jeśli użytkownik jest zalogowany
              overlay.classList.add("hidden");
          } else {
              // Pokaż nakładkę, jeśli użytkownik nie jest zalogowany
              overlay.classList.remove("hidden");
          }
      })
      .catch(error => console.error("Błąd sprawdzania statusu logowania:", error));
});


document.addEventListener("DOMContentLoaded", function () {
  // Pobierz ulubione przepisy
  fetch("/api/recipes/favorites")
      .then(response => response.json())
      .then(favoriteIds => {
          // Przejdź przez każde serduszko i oznacz ulubione
          document.querySelectorAll(".heart-icon").forEach(heart => {
              const recipeId = parseInt(heart.dataset.recipeId, 10);
              if (favoriteIds.includes(recipeId)) {
                  heart.classList.add("active"); // Oznacz jako ulubione
              } else {
                  heart.classList.remove("active"); // Domyślnie szare
              }
          });
      })
      .catch(error => console.error("Błąd podczas pobierania ulubionych przepisów:", error));
});


function toggleFavorite(heartIcon) {
  const recipeId = heartIcon.dataset.recipeId;
  const isActive = heartIcon.classList.contains("active");

  if (!recipeId) {
      alert("Wystąpił błąd. Nie znaleziono ID przepisu.");
      return;
  }

  if (isActive) {
      // Usuń z ulubionych
      fetch(`/api/recipes/${recipeId}/favorite`, { method: "DELETE" })
          .then(response => response.json())
          .then(data => {
              if (data.message) {
                  heartIcon.classList.remove("active");
              }
          })
          .catch(error => console.error("Błąd podczas usuwania z ulubionych:", error));
  } else {
      // Dodaj do ulubionych
      fetch(`/api/recipes/${recipeId}/favorite`, { method: "POST" })
          .then(response => {
              if (response.status === 401) {
                  alert("Zaloguj się, aby dodać przepis do ulubionych.");
                  return;
              }
              return response.json();
          })
          .then(data => {
              if (data.message) {
                  heartIcon.classList.add("active");
              }
          })
          .catch(error => console.error("Błąd podczas dodawania do ulubionych:", error));
  }
}


document.addEventListener("DOMContentLoaded", function () {
  // Pobranie ulubionych przepisów
  fetch("/api/user/favorites")
      .then(response => response.json())
      .then(favorites => {
          const container = document.getElementById("favorites-container");

          if (favorites.length === 0) {
              container.innerHTML = "<p>Brak ulubionych przepisów.</p>";
              return;
          }

          // Generowanie kart ulubionych przepisów
          favorites.forEach(recipe => {
              const recipeCard = document.createElement("div");
              recipeCard.classList.add("col-md-3");

              recipeCard.innerHTML = `
                  <div class="recipe-card">
                      <img src="${recipe.image_url}" alt="${recipe.name}">
                      <h5>${recipe.name}</h5>
                      <p>${recipe.description}</p>
                      <button class="remove-favorite" onclick="removeFavorite(${recipe.id})">Usuń z ulubionych</button>
                  </div>
              `;

              container.appendChild(recipeCard);
          });
      })
      .catch(error => console.error("Błąd podczas ładowania ulubionych przepisów:", error));
});

// Funkcja do usuwania ulubionego przepisu
function removeFavorite(recipeId) {
  fetch(`/api/recipes/${recipeId}/favorite`, { method: "DELETE" })
      .then(response => response.json())
      .then(data => {
          if (data.message) {
              alert(data.message);
              location.reload(); // Odśwież stronę, aby zaktualizować ulubione
          }
      })
      .catch(error => console.error("Błąd podczas usuwania z ulubionych:", error));
}


function toggleFavorite(heartIcon) {
  const recipeId = heartIcon.dataset.recipeId;
  const isActive = heartIcon.classList.contains("active");

  if (!recipeId) {
      alert("Wystąpił błąd. Nie znaleziono ID przepisu.");
      return;
  }

  if (isActive) {
      // Usuń z ulubionych
      fetch(`/api/recipes/${recipeId}/favorite`, { method: "DELETE" })
          .then(response => response.json())
          .then(data => {
              if (data.message) {
                  heartIcon.classList.remove("active");
              }
          })
          .catch(error => console.error("Błąd podczas usuwania z ulubionych:", error));
  } else {
      // Dodaj do ulubionych
      fetch(`/api/recipes/${recipeId}/favorite`, { method: "POST" })
          .then(response => {
              if (response.status === 401) {
                  alert("Zaloguj się, aby dodać przepis do ulubionych.");
                  return;
              }
              return response.json();
          })
          .then(data => {
              if (data.message) {
                  heartIcon.classList.add("active");
              }
          })
          .catch(error => console.error("Błąd podczas dodawania do ulubionych:", error));
  }
}


document.querySelector('.search-bar input').addEventListener('keypress', function(event) {
  if (event.key === 'Enter') {
      event.preventDefault(); // Zapobiega domyślnemu przesłaniu formularza
      const query = this.value.trim();
      if (query) {
          window.location.href = `/search?query=${encodeURIComponent(query)}`;
      } else {
          alert('Wpisz coś w wyszukiwarce!');
      }
  }
});


// Dodaj obsługę przycisku "Usuń konto"
document.getElementById('delete-account').addEventListener('click', function () {
  if (confirm('Czy na pewno chcesz usunąć swoje konto? Tej operacji nie można cofnąć.')) {
    fetch('/delete-account', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => {
      if (response.ok) {
        alert('Twoje konto zostało usunięte.');
        window.location.href = '/index.html'; // Przekierowanie na stronę logowania
      } else {
        alert('Wystąpił problem podczas usuwania konta. Spróbuj ponownie później.');
      }
    })
    .catch(error => {
      console.error('Błąd:', error);
      alert('Wystąpił błąd podczas połączenia z serwerem.');
    });
  }
});

document.addEventListener("DOMContentLoaded", function () {
  fetch("/is_logged_in") // Endpoint sprawdzający, czy użytkownik jest zalogowany
    .then(response => response.json())
    .then(data => {
      const overlay = document.getElementById("overlay-add-recipe");

      if (!data.logged_in) {
        // Jeśli użytkownik nie jest zalogowany, pokaż nakładkę
        overlay.classList.remove("hidden");
      } else {
        // Jeśli użytkownik jest zalogowany, ukryj nakładkę
        overlay.classList.add("hidden");
      }
    })
    .catch(error => console.error("Błąd sprawdzania statusu logowania:", error));
});

