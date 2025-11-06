const fs = require('fs');
const path = require('path');

const DB_FILE = path.join(__dirname, 'database.json');

let db = {
    participants: [],
    blacklist: [],
    config: {
        hashtag: null,
        hashtagLocked: false,
        bonusRoles: {},
        tagEnabled: false,
        serverTag: null,
        tagQuantity: 1
    }
};

function loadDatabase() {
    try {
        if (fs.existsSync(DB_FILE)) {
            const data = fs.readFileSync(DB_FILE, 'utf8');
            db = JSON.parse(data);
        }
    } catch (error) {
        console.error('Erro ao carregar database:', error);
    }
}

function saveDatabase() {
    try {
        fs.writeFileSync(DB_FILE, JSON.stringify(db, null, 2), 'utf8');
    } catch (error) {
        console.error('Erro ao salvar database:', error);
    }
}

loadDatabase();

module.exports = {
    get participants() { return db.participants; },
    get blacklist() { return db.blacklist; },
    get config() { return db.config; },

    addParticipant(userId, firstName, lastName, hashtag, messageId) {
        const fullName = `${firstName} ${lastName}`;
        db.participants.push({
            userId,
            firstName,
            lastName,
            fullName,
            hashtag,
            messageId,
            registeredAt: Date.now(),
            tickets: {
                base: 1,
                roles: {},
                tag: false
            }
        });
        saveDatabase();
    },

    removeParticipant(userId) {
        db.participants = db.participants.filter(p => p.userId !== userId);
        saveDatabase();
    },

    getParticipant(userId) {
        return db.participants.find(p => p.userId === userId);
    },

    isRegistered(userId) {
        return db.participants.some(p => p.userId === userId);
    },

    isNameTaken(firstName, lastName) {
        const fullName = `${firstName} ${lastName}`;
        return db.participants.some(p => p.fullName === fullName);
    },

    getAllParticipants() {
        return db.participants;
    },

    updateTickets(userId, tickets) {
        const participant = db.participants.find(p => p.userId === userId);
        if (participant) {
            participant.tickets = tickets;
            saveDatabase();
        }
    },

    addToBlacklist(userId, username, reason) {
        db.blacklist.push({
            userId,
            username,
            reason,
            addedAt: Date.now()
        });
        saveDatabase();
    },

    removeFromBlacklist(userId) {
        db.blacklist = db.blacklist.filter(u => u.userId !== userId);
        saveDatabase();
    },

    isBlacklisted(userId) {
        return db.blacklist.some(u => u.userId === userId);
    },

    setHashtag(hashtag) {
        db.config.hashtag = hashtag;
        saveDatabase();
    },

    lockHashtag() {
        db.config.hashtagLocked = true;
        saveDatabase();
    },

    addBonusRole(roleId, roleName, quantity, abbreviation) {
        db.config.bonusRoles[roleId] = {
            name: roleName,
            quantity: quantity,
            abbreviation: abbreviation
        };
        saveDatabase();
    },

    removeBonusRole(roleId) {
        delete db.config.bonusRoles[roleId];
        saveDatabase();
    },

    setTagEnabled(enabled, tag, quantity) {
        db.config.tagEnabled = enabled;
        db.config.serverTag = tag;
        if (quantity !== undefined) {
            db.config.tagQuantity = quantity;
        }
        saveDatabase();
    },

    clearParticipants() {
        db.participants = [];
        db.config.hashtagLocked = false;
        saveDatabase();
    },

    clearAll() {
        db.participants = [];
        db.config = {
            hashtag: null,
            hashtagLocked: false,
            bonusRoles: {},
            tagEnabled: false,
            serverTag: null,
            tagQuantity: 1
        };
        saveDatabase();
    },

    getStatistics() {
        let totalTickets = 0;
        let ticketsByRole = {};
        let ticketsByTag = 0;

        for (const p of db.participants) {
            const roleNames = Object.keys(p.tickets.roles || {});
            totalTickets += 1 + roleNames.length + (p.tickets.tag ? 1 : 0);

            roleNames.forEach(roleName => {
                ticketsByRole[roleName] = (ticketsByRole[roleName] || 0) + 1;
            });

            if (p.tickets.tag) {
                ticketsByTag++;
            }
        }

        return {
            totalParticipants: db.participants.length,
            totalTickets,
            ticketsByRole,
            ticketsByTag
        };
    }
};
