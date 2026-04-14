let startDate = new Date();
startDate.setDate(startDate.getDate() - startDate.getDay());

function render() {
    const container = document.getElementById('weekContainer');
    const display = document.getElementById('monthDisplay');
    
    if (!container || !display) return;
    container.innerHTML = '';
    
    const days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    const months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    
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
        demandasDoDia.forEach(textoCompleto => {
            const partes = textoCompleto.split('|');
            const idBanco = partes[0];
            const textoOriginal = partes[1];

            let icon = '';
            let textoExibicao = '';
            let statusClass = '';

            if (textoOriginal.startsWith("DONE:")) {
                textoExibicao = textoOriginal.replace("DONE:", "");
                icon = '<i class="fas fa-check-circle" style="color: var(--success); margin-right: 8px;"></i>';
                statusClass = 'status-done';
            } else {
                textoExibicao = textoOriginal.replace("WAIT:", "");
                icon = '<i class="fas fa-clock" style="color: var(--warning); margin-right: 8px;"></i>';
                statusClass = 'status-wait';
            }

            listHtml += `
                <div class="demand-item ${statusClass}">
                    ${icon} <span>${textoExibicao}</span>
                    <button class="btn-del-item" onclick="confirmarExclusao(${idBanco})" title="Excluir">
                        <i class="fas fa-times"></i>
                    </button>
                </div>`;
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

// ESTA É A FUNÇÃO QUE RESOLVE O 404
function confirmarExclusao(id) {
    if(confirm("Deseja realmente excluir este agendamento?")) {
        // Redireciona para o caminho EXATO que aparece no seu erro do Django
        window.location.href = `/staff/agenda/deletar/${id}/`;
    }
}

function changeWeek(offset) {
    startDate.setDate(startDate.getDate() + offset);
    render();
}

document.addEventListener('DOMContentLoaded', render);