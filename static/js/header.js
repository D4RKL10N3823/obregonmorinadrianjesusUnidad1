document.addEventListener('DOMContentLoaded', () => {
    // Muestra y oculta el menu del perfil al darle click (perfil y cerrar sesión)
    const profileMenuButton = document.getElementById('profileMenuButton');
    const profileMenu = document.getElementById('profileMenu');

    if (profileMenuButton && profileMenu) {
        profileMenuButton.addEventListener('click', () => {
            profileMenu.classList.toggle('hidden');
        });

        document.addEventListener('click', (event) => {
            if (!profileMenuButton.contains(event.target) && !profileMenu.contains(event.target)) {
                profileMenu.classList.add('hidden');
            }
        });
    }
});
