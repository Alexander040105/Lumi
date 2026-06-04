const { getDefaultConfig } = require('expo/metro-config');

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname);

// Fix React Native 0.81 debugger-frontend ENOENT watch error
config.resolver.blockList = [
  /node_modules\/.*\/\.debugger-frontend-.*/,
  /node_modules\/.*\/\.hermes-.*/,
];

module.exports = config;
