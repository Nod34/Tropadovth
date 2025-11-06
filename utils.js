function isValidName(name) {
    const regex = /^[a-zA-ZÀ-ÿ\s'-]+$/;
    return regex.test(name) && name.length > 0 && name.length <= 50;
}

function calculateTickets(member, bonusRoles, tagEnabled, serverTag, tagQuantity) {
    const tickets = {
        base: 1,
        roles: {},
        tag: false
    };

    for (const [roleId, roleData] of Object.entries(bonusRoles)) {
        if (member.roles.cache.has(roleId)) {
            tickets.roles[roleData.name] = {
                quantity: roleData.quantity,
                abbreviation: roleData.abbreviation
            };
        }
    }

    if (tagEnabled && serverTag) {
        const displayName = member.displayName || member.user.username;
        const username = member.user.username;
        
        if (displayName.includes(serverTag) || username.includes(serverTag)) {
            tickets.tag = tagQuantity;
        }
    }

    return tickets;
}

function getTotalTickets(tickets) {
    let total = tickets.base || 1;
    
    const roleNames = Object.keys(tickets.roles || {});
    for (const roleName of roleNames) {
        total += tickets.roles[roleName].quantity;
    }
    
    if (tickets.tag) {
        total += tickets.tag;
    }
    
    return total;
}

function formatTicketsList(tickets) {
    const list = [];
    
    list.push('1 ficha base');
    
    for (const [roleName, roleData] of Object.entries(tickets.roles || {})) {
        list.push(`+${roleData.quantity} ficha(s) - ${roleName} (${roleData.abbreviation})`);
    }
    
    if (tickets.tag) {
        list.push(`+${tickets.tag} ficha(s) - TAG do servidor`);
    }
    
    return list;
}

function abbreviateName(firstName, lastName) {
    const firstInitial = lastName.charAt(0).toUpperCase();
    const secondInitial = lastName.charAt(1) ? lastName.charAt(1).toLowerCase() : '';
    return `${firstName} ${firstInitial}${secondInitial}.`;
}

module.exports = {
    isValidName,
    calculateTickets,
    getTotalTickets,
    formatTicketsList,
    abbreviateName
};
