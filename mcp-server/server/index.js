const express = require('express');
const { spawn } = require('child_process');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 8080;

// MCP server instance
let mcpProcess = null;
const MCP_PORT = 8081;

// Start Python MCP server
function startMCPServer() {
  console.log(`Starting Python MCP server on port ${MCP_PORT}...`);
  
  // Try different Python commands
  const pythonCommands = ['python3', 'python', 'python3.11'];
  const pythonPath = process.env.PYTHON_PATH || pythonCommands.find(cmd => {
    try {
      const result = require('child_process').execSync(`which ${cmd}`, { encoding: 'utf8' });
      console.log(`Found Python at: ${result.trim()}`);
      return true;
    } catch (e) {
      return false;
    }
  }) || 'python';
  
  console.log(`Using Python command: ${pythonPath}`);
  
  const scriptPath = path.join(__dirname, 'start_mcp.py');
  console.log(`Script path: ${scriptPath}`);
  console.log(`Working directory: ${path.join(__dirname, '..')}`);
  
  // Check if script exists
  if (!fs.existsSync(scriptPath)) {
    console.error(`ERROR: Python script not found at ${scriptPath}`);
    return;
  }
  
  mcpProcess = spawn(pythonPath, [scriptPath], {
    env: {
      ...process.env,
      MCP_PORT: MCP_PORT.toString(),
      PYTHONPATH: path.join(__dirname, '..'),
    },
    cwd: path.join(__dirname, '..'),
  });

  mcpProcess.stdout.on('data', (data) => {
    console.log(`MCP: ${data}`);
  });

  mcpProcess.stderr.on('data', (data) => {
    console.error(`MCP Error: ${data}`);
  });

  mcpProcess.on('error', (error) => {
    console.error(`Failed to start MCP process: ${error.message}`);
  });

  mcpProcess.on('exit', (code) => {
    console.log(`MCP server exited with code ${code}`);
    // Restart after delay
    setTimeout(startMCPServer, 5000);
  });
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'kea-mcp-proxy' });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    name: 'Kea MCP Server',
    version: '1.0.0',
    endpoints: {
      sse: '/sse',
      messages: '/messages',
      health: '/health'
    }
  });
});

// Proxy MCP endpoints
const mcpProxy = createProxyMiddleware({
  target: `http://127.0.0.1:${MCP_PORT}`, // Use IPv4 instead of localhost
  changeOrigin: true,
  onError: (err, req, res) => {
    console.error('Proxy error:', err);
    res.status(502).json({ error: 'MCP server unavailable' });
  }
});

app.use('/sse', mcpProxy);
app.use('/messages', mcpProxy);

// Start servers
startMCPServer();

app.listen(PORT, () => {
  console.log(`Proxy server running on port ${PORT}`);
  console.log(`Health: http://localhost:${PORT}/health`);
  console.log(`SSE: http://localhost:${PORT}/sse`);
});