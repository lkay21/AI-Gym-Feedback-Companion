const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Reduce file watcher load by excluding unnecessary directories
config.watchFolders = [];
config.resolver.sourceExts.push('cjs');

// Exclude node_modules and other large directories from watching
config.watcher = {
  additionalExts: ['cjs', 'mjs'],
  healthCheck: {
    enabled: true,
  },
};

// Reduce the number of files Metro watches
config.server = {
  ...config.server,
  enhanceMiddleware: (middleware) => {
    return middleware;
  },
};

module.exports = config;

