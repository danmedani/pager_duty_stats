const path = require('path');

module.exports = {
  entry: {
      index: './ui/src/pages/index.js',
      stats: './ui/src/pages/stats.js'
  },
  output: {
    filename: '[name].bundle.js',
    path: path.resolve(__dirname, '../static'),
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
