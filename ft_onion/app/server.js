const express = require('express');
const bodyParser = require('body-parser');
const session = require('express-session');
const { Pool } = require('pg');
const bcrypt = require('bcrypt');
const path = require('path');

const app = express();
const PORT = "3000";

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
    saveUninitialized: true,
    cookie: { secure: false }
}));

async function initDB() {
    try {
        await pool.query(`
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `);
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
        return res.json({ success: false, message: 'Invalid username' });
    }
        
    const user = result.rows[0];
    const validPassword = await bcrypt.compare(password, user.password);
        
    if (!validPassword) {
       return res.json({ success: false, message: 'Invalid password' });
    }
        
    req.session.user = { id: user.id, pseudo: user.username };
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
            'INSERT INTO users (username, password) VALUES ($1, $2)',
            [username, hashedPassword]
        );
        
        res.json({ success: true });
    } catch (err) {
        console.error('Signup error:', err);
        res.status(500).json({ success: false, message: 'Server error' });
    }
});

initDB().then(() => {
    app.listen(PORT, '0.0.0.0', () => {
        console.log(`Server running on port ${PORT}`);
    });
});