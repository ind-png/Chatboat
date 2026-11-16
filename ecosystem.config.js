const path = require('path');

module.exports = {
  apps: [
    {
      name: 'chatboat-backend',
      cwd: path.join(__dirname, 'backend'),
      script: 'main.py',
      interpreter: path.join(__dirname, 'backend', '.venv', 'Scripts', 'python.exe'),
      env: {
        PYTHONPATH: path.join(__dirname, 'backend'),
      },
      autorestart: true,
      max_restarts: 10,
    },
    {
      name: 'chatboat-frontend',
      cwd: path.join(__dirname, 'frontend'),
      script: path.join(__dirname, 'frontend', 'node_modules', 'next', 'dist', 'bin', 'next'),
      args: 'dev -H 0.0.0.0',
      autorestart: true,
      max_restarts: 10,
    },
  ],
};

