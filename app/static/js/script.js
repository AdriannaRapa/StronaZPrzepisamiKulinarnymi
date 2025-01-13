console.log("Plik script.js załadowany poprawnie!");

// Obsługa logowania - CHECK
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




// Wyświetlanie danych użytkownika na stronie "Moje konto" - CHECK
document.addEventListener("DOMContentLoaded", function () {
  fetch("/api/user")
    .then(response => response.json())
    .then(data => {
      const userName = document.getElementById("user-name");
      const userEmail = document.getElementById("user-email");
      const userDate = document.getElementById("user-date");

      if (userName) userName.textContent = data.name || "Brak danych";
      if (userEmail) userEmail.textContent = data.email || "Brak danych";
      if (userDate) userDate.textContent = data.join_date || "Brak danych";
    })
    .catch(error => console.error("Błąd ładowania danych użytkownika:", error));
});




// Funkcja aktualizująca przyciski w nagłówku - CHECK
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


// Funkcja wylogowania - CHECK
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


// Podświetl aktywny przycisk w menu nawigacyjnym - CHECK -> NIBY NIE POTRZEBNY ALE LEPIEJ DZIAŁA PODŚWIETLANIE
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

//zmiana nazwy - CHECK
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

//zmaina emaila - CHECK
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


//zmiana hasła - CHECK
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




// Nakładka na sekcje ulubione przepisy i dodaj przepis dla użytkownika niezalogowanego - CHECK
document.addEventListener("DOMContentLoaded", function () {
  // Sprawdź status logowania
  fetch("/is_logged_in")
    .then((response) => response.json())
    .then((data) => {
      const favoritesOverlay = document.getElementById("favorites-overlay");
      const addRecipeOverlay = document.getElementById("overlay-add-recipe");

      if (data.logged_in) {
        // Ukryj nakładkę, jeśli użytkownik jest zalogowany
        if (favoritesOverlay) {
          favoritesOverlay.classList.add("hidden");
        }
        if (addRecipeOverlay) {
          addRecipeOverlay.classList.add("hidden");
        }
      } else {
        // Pokaż nakładkę, jeśli użytkownik nie jest zalogowany
        if (favoritesOverlay) {
          favoritesOverlay.classList.remove("hidden");
        }
        if (addRecipeOverlay) {
          addRecipeOverlay.classList.remove("hidden");
        }
      }
    })
    .catch((error) =>
      console.error("Błąd sprawdzania statusu logowania:", error)
    );
});



// Obsługa przycisku wyszukiwania  - CHECK
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

//Usuwanie konta
document.addEventListener("DOMContentLoaded", function () {
  const deleteAccountButton = document.getElementById('delete-account');

  // Sprawdź, czy element istnieje
  if (deleteAccountButton) {
    deleteAccountButton.addEventListener('click', function () {
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
            window.location.href = '/index.html'; // Przekierowanie na stronę główną
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
  } else {
    console.log("Przycisk 'Usuń konto' nie istnieje na tej stronie."); // Informacja o braku elementu
  }
});





document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("recipes-container");

  try {
    const response = await fetch("/api/recipes");
    if (!response.ok) throw new Error("Nie udało się pobrać przepisów.");

    const recipes = await response.json();

    // Tworzenie kart dla każdego przepisu
    recipes.forEach(recipe => {
      const card = document.createElement("div");
      card.classList.add("col-md-6", "mb-4");
      card.innerHTML = `
        <div class="recipe-card">
          <span class="heart-icon" onclick="toggleFavorite(this)" data-recipe-id="${recipe.id}">&hearts;</span>
          <img src="${recipe.image_url}" alt="${recipe.name}" class="recipe-image">
          <h3>${recipe.name}</h3>
          <button class="btn btn-primary w-100 mt-2" onclick="showRecipeDetails(${recipe.id})">Przeglądaj</button>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (error) {
    console.error("Błąd podczas ładowania przepisów:", error);
    container.innerHTML = "<p class='text-danger'>Nie udało się załadować przepisów. Spróbuj ponownie później.</p>";
  }
});

function toggleFavorite(element) {
  alert("Dodano do ulubionych!");
}

function showRecipeDetails(recipeId) {
  alert("Wyświetl szczegóły przepisu ID: " + recipeId);
}


function toggleFavorite(element, recipeId) {
  fetch('/is_logged_in')
    .then(response => response.json())
    .then(data => {
      if (data.logged_in) {
        // Dodaj do ulubionych
        fetch(`/favorite/${recipeId}`, { method: 'POST' })
          .then(res => res.json())
          .then(result => alert(result.message))
          .catch(err => alert("Błąd podczas dodawania do ulubionych."));
      } else {
        alert("Musisz być zalogowany, aby dodać przepis do ulubionych.");
      }
    })
    .catch(err => console.error("Błąd podczas sprawdzania statusu logowania:", err));
}


function loadRecipes(category = null) {
  const container = document.getElementById("recipes-container");
  container.innerHTML = ""; // Wyczyść kontener

  const url = category ? `/api/recipes?category=${category}` : "/api/recipes";

  fetch(url)
    .then(response => response.json())
    .then(recipes => {
      recipes.forEach(recipe => {
        const card = document.createElement("div");
        card.classList.add("col-md-6", "mb-4");
        card.innerHTML = `
          <div class="recipe-card">
            <span class="heart-icon" onclick="toggleFavorite(this, ${recipe.id})">&hearts;</span>
            <img src="${recipe.image_url}" alt="${recipe.name}" class="recipe-image">
            <h3>${recipe.name}</h3>
            <button class="btn btn-primary w-100 mt-2" onclick="showRecipeDetails(${recipe.id})">Przeglądaj</button>
          </div>
        `;
        container.appendChild(card);
      });
    })
    .catch(err => console.error("Błąd podczas ładowania przepisów:", err));
}


function showRecipeDetails(recipeId) {
  window.location.href = `/recipe/${recipeId}`;
}





document.getElementById("contact-form").addEventListener("submit", async (event) => {
  event.preventDefault(); // Zablokuj domyślną akcję formularza

  const formData = new FormData(event.target);
  const messageBox = document.getElementById("message-box");

  try {
    const response = await fetch("/contact", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error("Nie udało się wysłać wiadomości.");
    }

    const result = await response.json();
    // Wyświetl komunikat o sukcesie
    messageBox.style.display = "block";
    messageBox.className = "alert alert-success"; // Klasa Bootstrap dla sukcesu
    messageBox.textContent = "Wiadomość została wysłana pomyślnie!";
    event.target.reset(); // Wyczyść formularz
  } catch (error) {
    console.error("Błąd podczas wysyłania wiadomości:", error);
    // Wyświetl komunikat o błędzie
    messageBox.style.display = "block";
    messageBox.className = "alert alert-danger"; // Klasa Bootstrap dla błędu
    messageBox.textContent = "Wystąpił błąd podczas wysyłania wiadomości. Spróbuj ponownie później.";
  }
});
