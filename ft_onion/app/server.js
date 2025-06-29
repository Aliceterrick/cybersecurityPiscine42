const express = require('express');
const bodyParser = require('body-parser');
const session = require('express-session');
const { Pool } = require('pg');
const bcrypt = require('bcrypt');
const path = require('path');
const WebSocket = require('ws');
const http = require('http');

const app = express();
const PORT = "3000";
const clients = new Map();

const pool = new Pool({
    user: process.env.DB_USER,
    host: 'postgres',
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: 5432,
    connectionTimeoutMillis: 5000,
    idleTimeoutMillis: 30000,
});

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({
    secret: process.env.SESSION_SECRET || 'your_secret_key',
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: false,
        httpOnly: true,
        maxAge: 24 * 60 * 60 * 1000
    }
}));
app.use(express.static(path.join(__dirname, 'app')))

async function initDB() {
    try {
        await pool.query(`
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                status VARCHAR(30) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `);
        await pool.query(`
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            `);
        await pool.query('UPDATE users SET status = $1', ["offline"])
        console.log('Database initialized');
    } catch (err) {
        console.error('Database initialization error:', err);
    }
}

app.post('/api/login', async (req, res) => {
    const { pseudo, password } = req.body;
    
    const result = await pool.query(
       'SELECT * FROM users WHERE username = $1', 
       [pseudo]
    );
 
    if (result.rows.length === 0) {
        return res.status(401).json({ success: false, message: 'Unknown username' });
    }
        
    const user = result.rows[0];
    const validPassword = await bcrypt.compare(password, user.password);
        
    if (!validPassword) {
       return res.status(401).json({ success: false, message: 'Invalid password' });
    }
    await pool.query(
        'UPDATE users SET status = $1 WHERE username = $2', ["online", pseudo]
    );
    req.session.user = { id: user.id, username: user.username };
    res.json({ success: true });
});

app.post('/api/signup', async (req, res) => {
    const { username, password } = req.body;
    
    try {
        const userExists = await pool.query(
            'SELECT * FROM users WHERE username = $1', 
            [username]
        );
        
        if (userExists.rows.length > 0) {
            return res.json({ success: false, message: 'Username already exists' });
        }
        
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        await pool.query(
            'INSERT INTO users (username, password, status) VALUES ($1, $2, $3)',
            [username, hashedPassword, "offline"]
        );
        
        res.json({ success: true });
    } catch (err) {
        console.error('Signup error:', err);
        res.status(500).json({ success: false, message: 'Server error' });
    }
});

app.post('/api/logout', async (req, res) => {
    
    if (!req.session.user) {
        return res.status(400).json({success: false, message: 'Not logged in'});
    }

    const username = req.session.user.username;
    
    await pool.query(
        'UPDATE users SET status = $1 WHERE username = $2',
        ["offline", username]
    );
    
        req.session.destroy(err => {
        if (err) {
            console.error('Session destroy error:', err);
            return res.status(500).json({success: false, message: 'Failed to destroy session'});
        }
        
        res.clearCookie('connect.sid');
        res.json({success: true});
    });
});

function broadcastEvent(event, data) {
    const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;

    clients.forEach((client, clientId) => {
        try {
            client.response.write(payload);
            client.lastPing = Date.now();
        } catch (error) {
            console.error(`Error sending event to client ${clientId}:`, error);
            clients.delete(clientId);
        }
    });
}

app.post('/api/messages', async (req, res) => {
    const { content } = req.body;
    if (!content || content.trim === '') {
        return res.status(400).json({ error: 'Message content required' });
    }

    try {
        const result = await pool.query(
            'INSERT INTO messages (user_id, content) VALUES ($1, $2) RETURNING *',
            [req.session.user.id, content.trim()]
        );
        const newMessage = result.rows[0];

        const userResult = await pool.query(
            'SELECT username FROM users WHERE id = $1',
            [req.session.user.id]
        );

        if (userResult.rows.length === 0) {
            return res.status(500).json({ error: 'User not found' });
        }
        const messageData = {
            ...newMessage,
            username: userResult.rows[0].username
        };

        broadcastEvent('newMessage', messageData);

        res.json({ success: true })
    } catch (err) {
        console.error('Message send error: ', err);
        res.status(500).json({ error: 'Failed to send message' });
    }
});


app.get('/api/get_online', async (req, res) => {
    const online = await pool.query(
        'SELECT * FROM users WHERE status = $1', ["online"]
    )
    res.json({online})
});

app.get('/api/auth/status', (req, res) => {
    if (req.session.user) {
        res.json({
            authenticated: true,
            user: req.session.user
        });
    } else {
        res.json({
            authenticated: false
        });
    }
});

app.get('/api/events', (req, res) => {
    if (!req.session.user) {
        return res.status(401).end();
    }

    res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-transform',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
        'Content-Encoding': 'none'
    });

    const userId = req.session.user.id;
    const clientId = Date.now();

    clients.set(clientId, {
        response: res,
        lastPing: Date.now()
    });

    res.write(': init\n\n');
    res.write(`event: connected\ndata: ${JSON.stringify({ clientId})}\n\n)`);
    const pingInterval = setInterval(() => {
        try {
            res.write(': ping\n\n');
            clients.get(clientId).lastPing = Date.now();
        } catch (e) {
            clearInterval(pingInterval);
        }
    }, 10000);

    req.on('close', () => {
        clearInterval(pingInterval);
        clients.delete(clientId);
    });
    
});


app.get('/api/messages', async (req, res) => {
    try {
        const result = await pool.query(`
            SELECT messages.*, users.username 
            FROM messages 
            JOIN users ON messages.user_id = users.id
            ORDER BY created_at DESC
            LIMIT 50
            `);
            res.json(result.rows.reverse());
        } catch (err) {
            console.error('Messages fetch error:', err);
            res.status(500).json({ error: 'Failed to load messages' });
        }
    });
    
initDB().then(() => {
    app.listen(PORT, '0.0.0.0', () => {
        console.log(`Server running on port ${PORT}`);
    });
});

setInterval(() => {
    const now = Date.now();
    clients.forEach((client, clientId) => {
        if (now - client.LastPing > 40000) {
            try {
                client.response.end();
            } catch (e) {}
        }
        clients.delete(clientId);
    });
}, 50000);