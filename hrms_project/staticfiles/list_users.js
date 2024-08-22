async function listUsers() {
    try {
        const response = await fetch('/accounts/api/proxy-supabase/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        if (!response.ok) {
            throw new Error('Failed to fetch users');
        }
        const data = await response.json();
        const userListContainer = document.getElementById('user-list');
        userListContainer.innerHTML = ''; // Clear existing content
        
        // Create table
        const table = document.createElement('table');
        table.className = 'user-table';
        
        // Add table header
        const header = table.createTHead();
        const headerRow = header.insertRow(0);
        const headers = ['Email', 'Admin', 'Name', 'Created', 'Last Sign In', 'Email Confirmed'];
        headers.forEach(text => {
            const th = document.createElement('th');
            th.textContent = text;
            headerRow.appendChild(th);
        });
        
        // Add table body
        const tbody = table.createTBody();
        data.users.forEach(user => {
            const row = tbody.insertRow();
            row.insertCell(0).textContent = user.email;
            row.insertCell(1).textContent = user.is_admin ? 'Yes' : 'No';
            row.insertCell(2).textContent = `${user.first_name} ${user.last_name}`.trim() || 'N/A';
            row.insertCell(3).textContent = new Date(user.created_at).toLocaleDateString();
            row.insertCell(4).textContent = user.last_sign_in_at ? new Date(user.last_sign_in_at).toLocaleDateString() : 'Never';
            row.insertCell(5).textContent = user.email_confirmed ? 'Yes' : 'No';
        });
        
        userListContainer.appendChild(table);
    } catch (error) {
        console.error('Error fetching users:', error);
        const userListContainer = document.getElementById('user-list');
        userListContainer.innerHTML = `<p>Error loading users: ${error.message}</p>`;
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', listUsers);