const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const appDirectory = path.resolve(__dirname);



module.exports = {
  mode: 'development',
  devtool: 'eval-source-map',
  entry: path.resolve(appDirectory, 'index.web.js'),
  output: {
    filename: 'bundle.web.js',
    path: path.resolve(appDirectory, 'dist'),
    globalObject: 'this',
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        exclude: /node_modules\/(?!(@react-navigation|react-native|@react-native-async-storage)\/).*/,
        use: {
          loader: 'babel-loader',
          options: {
            cacheDirectory: true,
            presets: [
              ['@babel/preset-env', { targets: { browsers: 'last 2 versions' } }],
              ['@babel/preset-react', { runtime: 'automatic' }],
              '@babel/preset-typescript'
            ],
          },
        },
      },
      // React Native packages with fullySpecified disabled
      {
        test: /\.(js|jsx)$/,
        include: [
          /node_modules\/@react-navigation/,
          /node_modules\/@react-native-async-storage/
        ],
        resolve: {
          fullySpecified: false,
        },
        use: {
          loader: 'babel-loader',
          options: {
            cacheDirectory: true,
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
      },
      {
        test: /\.(png|jpe?g|gif)$/i,
        use: [
          {
            loader: 'url-loader',
            options: {
              limit: 8192,
            },
          },
        ],
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: path.resolve(appDirectory, 'index.html'),
    }),
  ],
  resolve: {
    extensions: ['.web.js', '.js', '.web.jsx', '.jsx', '.web.ts', '.ts', '.web.tsx', '.tsx', '.json'],
    alias: {
      'react-native': 'react-native-web',
      '@': path.resolve(appDirectory, 'src'),
    },
    fallback: {
      "crypto": false,
      "stream": false,
      "assert": false,
      "http": false,
      "https": false,
      "os": false,
      "url": false,
    },
    fullySpecified: false,
  },
  devServer: {
    static: {
      directory: path.join(appDirectory, 'dist'),
    },
    compress: true,
    port: 3000,
  },
}; 