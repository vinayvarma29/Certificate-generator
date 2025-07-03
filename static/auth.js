document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();  // Prevent form from submitting normally

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${username}&password=${password}`
        });

        if (response.ok) {
            // Redirect to certificate generation page on successful login
            window.location.href = '/certificate';
        } else {
            const data = await response.json();
            document.getElementById('errorMessage').textContent = data.message;
            document.getElementById('errorMessage').style.display = 'block';
        }
    } catch (error) {
        console.error("Error:", error);
        alert('An error occurred while logging in.');
    }
});
