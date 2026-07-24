const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

// Configuration
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://127.0.0.1:8000/api/v1/whatsapp/process';

// Initialize the WhatsApp Client
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        executablePath: '/usr/bin/google-chrome-stable',
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
    }
});

// Display QR Code
client.on('qr', (qr) => {
    console.log('Veuillez scanner ce QR code avec votre application WhatsApp :');
    qrcode.generate(qr, { small: true });
});

// On Ready
client.on('ready', () => {
    console.log('✅ Le Bot WhatsApp est prêt et connecté !');
});

// Message received
client.on('message', async msg => {
    // Ne répondre qu'aux messages texte standards (pas de statuts, etc.)
    if (msg.type !== 'chat') return;
    
    console.log(`📩 Message reçu de ${msg.from} : ${msg.body}`);

    try {
        // Envoi au backend Python FastAPI
        const response = await axios.post(FASTAPI_URL, {
            session_id: msg.from, // Le numéro sert d'identifiant de session
            message: msg.body
        });

        // Récupérer la réponse de l'Agent IA
        const answer = response.data.answer;
        
        // Renvoyer la réponse sur WhatsApp
        await msg.reply(answer);
        console.log(`📤 Réponse envoyée à ${msg.from}`);

    } catch (error) {
        console.error("❌ Erreur lors de la communication avec l'API FastAPI :", error.message);
        await msg.reply("Désolé, je rencontre des difficultés techniques avec le serveur d'IA en ce moment.");
    }
});

// Start the client
client.initialize();
