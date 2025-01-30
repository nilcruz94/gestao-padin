document.addEventListener("DOMContentLoaded", function() {
    const nome = document.getElementById('nome');
    const email = document.getElementById('email');
    const senha = document.getElementById('senha');
    const confirmarSenha = document.getElementById('confirmar_senha');
    const emailError = document.getElementById('email-error');
    const senhaError = document.getElementById('senha-error');
    const confirmarSenhaError = document.getElementById('confirmar-senha-error');

    // Função para validação de e-mail
    function validateEmail(email) {
        const regex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!regex.test(email)) {
            throw new Error('E-mail inválido!');
        }
    }

    // Adiciona o evento de "input" para validar em tempo real
    document.getElementById('register-form').addEventListener('input', function(e) {

        // Verificação do campo de nome
        if (nome.value.trim() === '') {
            document.getElementById('nome-error').textContent = 'Nome é obrigatório!';
            document.getElementById('nome-error').style.display = 'block';
        } else {
            document.getElementById('nome-error').style.display = 'none';
        }

        // Verificação do campo de email
        if (email.value.trim() !== '') {
            try {
                validateEmail(email.value);
                emailError.style.display = 'none';
            } catch (e) {
                emailError.textContent = e.message;
                emailError.style.display = 'block';
            }
        } else {
            emailError.style.display = 'none';
        }

        // Verificação da senha
        if (senha.value.trim().length < 6) {
            senhaError.textContent = 'A senha deve ter no mínimo 6 caracteres.';
            senhaError.style.display = 'block';
        } else {
            senhaError.style.display = 'none';
        }

        // Verificação de confirmação da senha
        if (confirmarSenha.value !== senha.value) {
            confirmarSenhaError.textContent = 'As senhas não coincidem.';
            confirmarSenhaError.style.display = 'block';
        } else {
            confirmarSenhaError.style.display = 'none';
        }
    });
});
