let startDate = new Date();
// Ajusta para o domingo da semana atual
startDate.setDate(startDate.getDate() - startDate.getDay());

function render() {
    const container = document.getElementById('weekContainer');
    const display = document.getElementById('monthDisplay');
    
    if (!container || !display) return;

    container.innerHTML = '';
    
    const days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    const months = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    
    display.innerText = `${months[startDate.getMonth()]} ${startDate.getFullYear()}`;
    
    let current = new Date(startDate);

    for (let i = 0; i < 7; i++) {
        const year = current.getFullYear();
        const month = String(current.getMonth() + 1).padStart(2, '0');
        const day = String(current.getDate()).padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;

        const isToday = new Date().toDateString() === current.toDateString();
        const demandasDoDia = (typeof dbDemandas !== 'undefined' && dbDemandas[dateStr]) || [];
        
        const card = document.createElement('div');
        card.className = `day-card ${demandasDoDia.length > 0 ? 'has-course' : ''}`;
        
        let listHtml = '';
        demandasDoDia.forEach(texto => {
            let icon = '';
            let textoExibicao = '';

            if (texto.startsWith("DONE:")) {
                // Remove o prefixo e adiciona o check verde
                textoExibicao = texto.replace("DONE:", "");
                icon = '<i class="fas fa-check-circle" style="color: #27ae60; margin-right: 8px;"></i>';
            } else {
                // Remove o prefixo e adiciona o relógio laranja
                textoExibicao = texto.replace("WAIT:", "");
                icon = '<i class="fas fa-clock" style="color: #f39c12; margin-right: 8px;"></i>';
            }

            listHtml += `<div class="demand-item">${icon} <span>${textoExibicao}</span></div>`;
        });

        card.innerHTML = `
            ${isToday ? '<div class="today-tag">HOJE</div>' : ''}
            <div class="day-name">${days[i]}</div>
            <div class="day-number">${current.getDate()}</div>
            <div class="demand-list">${listHtml}</div>
        `;
        
        container.appendChild(card);
        current.setDate(current.getDate() + 1);
    }
}

function changeWeek(offset) {
    startDate.setDate(startDate.getDate() + offset);
    render();
}

document.addEventListener('DOMContentLoaded', render);