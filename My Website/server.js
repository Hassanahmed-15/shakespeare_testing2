const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = 8000;

const MIME_TYPES = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.wav': 'audio/wav',
    '.mp4': 'video/mp4',
    '.woff': 'application/font-woff',
    '.ttf': 'application/font-ttf',
    '.eot': 'application/vnd.ms-fontobject',
    '.otf': 'application/font-otf',
    '.wasm': 'application/wasm'
};

const server = http.createServer((req, res) => {
    console.log(`${req.method} ${req.url}`);

    // Handle Netlify function endpoint
    const parsedUrl = url.parse(req.url);
    const pathname = parsedUrl.pathname;

    if (pathname === '/.netlify/functions/shakespeare' && req.method === 'POST') {
        let body = '';
        
        req.on('data', chunk => {
            body += chunk.toString();
        });
        
        req.on('end', () => {
            try {
                const { text, level, model } = JSON.parse(body);
                
                // Mock response for local testing
                const mockAnalysis = `This is a mock analysis for local testing. The actual text submitted was:
                
"${text.substring(0, 100)}${text.length > 100 ? '...' : ''}"

Analysis Level: ${level}
Model: ${model}

⚠️ NOTE: This is a mock response. To use real AI analysis, you need to:
1. Install Netlify CLI: npm install -g netlify-cli
2. Set OPENAI_API_KEY in environment
3. Run: netlify dev

Or deploy to Netlify and set the environment variable there.`;

                res.writeHead(200, {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                });
                
                res.end(JSON.stringify({
                    choices: [{
                        message: {
                            content: mockAnalysis
                        }
                    }],
                    usage: {
                        prompt_tokens: 50,
                        completion_tokens: 100,
                        total_tokens: 150
                    }
                }));
            } catch (error) {
                res.writeHead(400, {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                });
                res.end(JSON.stringify({ error: 'Invalid JSON' }));
            }
        });
        
        return;
    }

    // Handle OPTIONS (CORS preflight)
    if (req.method === 'OPTIONS') {
        res.writeHead(200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        });
        res.end();
        return;
    }

    // Parse URL
    const parsedUrl = url.parse(req.url);
    let pathname = parsedUrl.pathname;

    // Default to index.html
    if (pathname === '/') {
        pathname = '/index.html';
    }

    // Security: prevent directory traversal
    const safePath = path.normalize(pathname).replace(/^(\.\.[\/\\])+/, '');
    const filePath = path.join(__dirname, safePath);

    // Check if file exists
    fs.access(filePath, fs.constants.F_OK, (err) => {
        if (err) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('404 Not Found');
            return;
        }

        // Read and serve file
        fs.readFile(filePath, (err, data) => {
            if (err) {
                res.writeHead(500, { 'Content-Type': 'text/plain' });
                res.end('500 Internal Server Error');
                return;
            }

            const ext = path.parse(filePath).ext;
            const contentType = MIME_TYPES[ext] || 'application/octet-stream';

            res.writeHead(200, { 'Content-Type': contentType });
            res.end(data);
        });
    });
});

server.listen(PORT, () => {
    console.log(`🚀 Server running at http://localhost:${PORT}/`);
    console.log(`📝 Open http://localhost:${PORT}/ in your browser`);
    console.log(`⚠️  Note: Using mock API responses. For real AI, use Netlify CLI.`);
});

