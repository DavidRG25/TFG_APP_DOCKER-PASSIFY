document.addEventListener("DOMContentLoaded", function() {
    // 1. Añadir el botón de LIMPIAR si hay filtros activos (Mantenemos el botón BUSCAR visible por estabilidad)
    var searchBtns = document.querySelectorAll("input[type='submit'].btn-primary, button[type='submit'].btn-primary");
    
    searchBtns.forEach(function(btn) {
        // En Jazzmin el buscador suele estar bajo #changelist-search o un div con form
        if (btn.closest('#changelist-search') || btn.closest('.changelist-form') || btn.closest('.filter-list')) {
            // El botón BUSCAR se queda normal. Ya no lo ocultamos para evitar cuelgues del DOM de Jazzmin.

            // Si hay parámetros en la URL (un filtro aplicado), ponemos el botón LIMPIAR
            if (window.location.search && window.location.search !== '?' && !btn.parentNode.querySelector('.btn-clear-filters')) {
                var clearBtn = document.createElement("a");
                clearBtn.href = window.location.pathname; // Elimina todo lo del ? hacia adelante
                clearBtn.className = "btn btn-secondary btn-clear-filters ml-2";
                clearBtn.style.marginRight = "15px";
                clearBtn.innerHTML = '<i class="fas fa-times"></i> Limpiar';
                
                // Lo ponemos después del botón BUSCAR
                btn.parentNode.insertBefore(clearBtn, btn.nextSibling);
            }
        }
    });
});
