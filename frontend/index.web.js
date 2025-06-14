import { AppRegistry } from 'react-native-web';
import App from './src/App';
import appConfig from './app.json';

const appName = appConfig.name;

AppRegistry.registerComponent(appName, () => App);
AppRegistry.runApplication(appName, {
  rootTag: document.getElementById('root'),
}); 