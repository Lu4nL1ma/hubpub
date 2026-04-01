// agd.js

let startDate = new Date();
// Ajusta para o domingo da semana atual
startDate.setDate(startDate.getDate() - startDate.getDay());

function render() {
    const container = document.getElementById('weekContainer');
    const display = document.getElementById('monthDisplay');
    
    // Verifica se os elementos existem no DOM
    if (!container || !display) return;

    container.innerHTML = '';
    
    const days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    const months = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    
    // Atualiza o topo da agenda com Mês e Ano
    display.innerText = `${months[startDate.getMonth()]} ${startDate.getFullYear()}`;
    
    let current = new Date(startDate);

    for (let i = 0; i < 7; i++) {
        // --- CORREÇÃO DE FUSO HORÁRIO ---
        // Criamos a string YYYY-MM-DD baseada na data LOCAL
        const year = current.getFullYear();
        const month = String(current.getMonth() + 1).padStart(2, '0'); // Meses no JS começam em 0
        const day = String(current.getDate()).padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;
        // --------------------------------

        const isToday = new Date().toDateString() === current.toDateString();
        
        // Busca no objeto dbDemandas (injetado pelo Django no HTML)
        // Opcional: Garante que dbDemandas existe para não quebrar o script
        const demandasDoDia = (typeof dbDemandas !== 'undefined' && dbDemandas[dateStr]) || [];
        
        const card = document.createElement('div');
        card.className = `day-card ${demandasDoDia.length > 0 ? 'has-course' : ''}`;
        
        let listHtml = '';
        demandasDoDia.forEach(texto => {
            listHtml += `<div class="demand-item">${texto}</div>`;
        });

        card.innerHTML = `
            ${isToday ? '<div class="today-tag">HOJE</div>' : ''}
            <div class="day-name">${days[i]}</div>
            <div class="day-number">${current.getDate()}</div>
            <div class="demand-list">${listHtml}</div>
        `;
        
        container.appendChild(card);
        
        // Incrementa o dia para a próxima iteração do loop
        current.setDate(current.getDate() + 1);
    }
}

/**
 * Altera a semana visualizada
 * @param {number} offset - Quantidade de dias (ex: 7 para próxima semana, -7 para anterior)
 */
function changeWeek(offset) {
    startDate.setDate(startDate.getDate() + offset);
    render();
}

// Inicializa a renderização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', render);