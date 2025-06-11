document.addEventListener('DOMContentLoaded', () => {
    // Al momento de escribir muestra una X para borrar el contenido del input
    const searchInput = document.getElementById('searchInput');
    const clearBtn = document.getElementById('clearSearch');

    searchInput.focus();

    searchInput.addEventListener('input', () => {
        if (searchInput.value.trim() !== '') {
            clearBtn.classList.remove('hidden');
        } else {
            clearBtn.classList.add('hidden');
        }
    });

    clearBtn.addEventListener('click', () => {
        searchInput.value = '';
        clearBtn.classList.add('hidden');
    });
});
