const path = require('path');

module.exports = {
  entry: './ui/src/index.js',
  output: {
    filename: 'main.js',
    path: path.resolve(__dirname, 'dist'),
  },
  watch: true,
  watchOptions: {
    poll: 1000 // Check for changes every second
  },
  module: {
    rules: [
      {
        use: {
          loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env']
            }
        }
      }
    ]
  }
};
