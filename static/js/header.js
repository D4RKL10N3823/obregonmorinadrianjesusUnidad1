const toggle = document.getElementById('categoryToggle');
const menu = document.getElementById('categoryMenu');

toggle.addEventListener('click', () => {
    menu.classList.toggle('hidden');
});

document.addEventListener('click', (e) => {
    if (!toggle.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.add('hidden');
    }
});

const profileMenuButton = document.getElementById('profileMenuButton');
const profileMenu = document.getElementById('profileMenu');

profileMenuButton.addEventListener('click', () => {
    profileMenu.classList.toggle('hidden');
});

document.addEventListener('click', (event) => {
    if (!profileMenuButton.contains(event.target) && !profileMenu.contains(event.target)) {
        profileMenu.classList.add('hidden');
    }
});