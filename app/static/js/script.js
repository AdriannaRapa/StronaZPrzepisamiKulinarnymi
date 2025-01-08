console.log("Witaj na stronie głównej!");


document.querySelector("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  console.log("Dane logowania:", { email, password });

  const response = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const result = await response.json();
  console.log("Odpowiedź serwera:", result);

  if (response.ok) {
    alert(result.message);
    window.location.href = "/";
  } else {
    alert(result.error);
  }

  try {
    const response = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
    });
  
    const result = await response.json();
    console.log("Odpowiedź serwera:", result);
  
    if (response.ok) {
        alert(result.message);
        window.location.href = "/";
    } else {
        alert(result.error);
    }
  } catch (error) {
    console.error("Błąd podczas logowania:", error);
    alert("Wystąpił problem z połączeniem. Spróbuj ponownie później.");
  }
  
});
