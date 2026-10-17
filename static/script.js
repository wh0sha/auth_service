document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirm = document.getElementById('confirm_password').value;
            const captcha = document.getElementById('captcha').value;
            
            if (!/^[a-zA-Z0-9]{3,20}$/.test(username)) {
                e.preventDefault();
                alert('Имя пользователя: только латиница и цифры, от 3 до 20 символов');
                return false;
            }
            
            if (email.indexOf('@') === -1 || !email.split('@')[1].includes('.')) {
                e.preventDefault();
                alert('Введите корректный email');
                return false;
            }
            
            if (password.length < 6 || !/[a-zA-Z]/.test(password) || !/\d/.test(password)) {
                e.preventDefault();
                alert('Пароль: минимум 6 символов, должны быть буквы и цифры');
                return false;
            }
            
            if (password !== confirm) {
                e.preventDefault();
                alert('Пароли не совпадают');
                return false;
            }
            
            if (!captcha) {
                e.preventDefault();
                alert('Решите капчу');
                return false;
            }
            
            if (!/^\d+$/.test(captcha)) {
                e.preventDefault();
                alert('Капча должна быть числом');
                return false;
            }
        });
    }
    
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const login = document.getElementById('login').value;
            const password = document.getElementById('password').value;
            const captcha = document.getElementById('captcha').value;
            
            if (!login) {
                e.preventDefault();
                alert('Введите логин или email');
                return false;
            }
            
            if (!password) {
                e.preventDefault();
                alert('Введите пароль');
                return false;
            }
            
            if (!captcha) {
                e.preventDefault();
                alert('Решите капчу');
                return false;
            }
            
            if (!/^\d+$/.test(captcha)) {
                e.preventDefault();
                alert('Капча должна быть числом');
                return false;
            }
        });
    }
});