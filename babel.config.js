module.exports = function(api) {
  api.cache(true);

  const presets = [
    'module:@react-native/babel-preset'
  ];

  const plugins = [
    [
      'module-resolver',
      {
        root: ['./frontend'],
        extensions: ['.ios.js', '.android.js', '.js', '.ts', '.tsx', '.json'],
        alias: {
          "@components": "./frontend/components",
          "@screens": "./frontend/screens",
          "@services": "./frontend/services",
          "@hooks": "./frontend/hooks",
          "@config": "./frontend/config",
          "@assets": "./frontend/assets",
          "@navigation": "./frontend/navigation",
          "@utils": "./frontend/utils",
        }
      }
    ]
  ];

  return {
    presets,
    plugins,
  };
}; 