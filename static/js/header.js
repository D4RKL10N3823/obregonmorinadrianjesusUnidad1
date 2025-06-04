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

const toggleBtn = document.getElementById('toggleSearch');
const searchContainer = document.getElementById('searchContainer');
const searchInput = document.getElementById('searchInput');
const clearBtn = document.getElementById('clearSearch');

toggleBtn.addEventListener('click', () => {
    searchContainer.classList.remove('hidden');
    searchContainer.classList.add('flex');
    toggleBtn.classList.add('hidden');
    setTimeout(() => searchInput.focus(), 100);
});

clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    searchContainer.classList.remove('flex');
    searchContainer.classList.add('hidden');
    toggleBtn.classList.remove('hidden');
});