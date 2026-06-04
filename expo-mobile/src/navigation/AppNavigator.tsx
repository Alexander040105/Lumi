import { StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '@/hooks/useAuth';
import { ThemeProvider } from '@/context/ThemeContext';
import { AuthProvider } from '@/context/AuthContext';
import LoginScreen from '@/screens/LoginScreen';
import ResetPasswordScreen from '@/screens/ResetPasswordScreen';
import MainTabs from './MainTabs';
import EcosimResultsScreen from '@/screens/EcosimResultsScreen';
import Toast from 'react-native-toast-message';

export type AuthStackParamList = {
  Login: undefined;
  ResetPassword: undefined;
};

export type AppStackParamList = {
  Main: undefined;
  EcosimResults: { result: any };
};

const AuthStack = createNativeStackNavigator<AuthStackParamList>();
const AppStack = createNativeStackNavigator<AppStackParamList>();

function AuthNavigator() {
  return (
    <AuthStack.Navigator screenOptions={{ headerShown: false }}>
      <AuthStack.Screen name="Login" component={LoginScreen} />
      <AuthStack.Screen name="ResetPassword" component={ResetPasswordScreen} />
    </AuthStack.Navigator>
  );
}

function AppNavigator() {
  return (
    <AppStack.Navigator screenOptions={{ headerShown: false }}>
      <AppStack.Screen name="Main" component={MainTabs} />
      <AppStack.Screen
        name="EcosimResults"
        component={EcosimResultsScreen}
        options={{ presentation: 'modal' }}
      />
    </AppStack.Navigator>
  );
}

function RootNavigator() {
  const { session, loading } = useAuth();

  if (loading) {
    return null;
  }

  return session ? <AppNavigator /> : <AuthNavigator />;
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
});

export default function AppNavigatorWrapper() {
  return (
    <SafeAreaView style={styles.safeArea} edges={['top', 'left', 'right', 'bottom']}>
      <AuthProvider>
        <ThemeProvider>
          <NavigationContainer>
            <RootNavigator />
            <Toast />
          </NavigationContainer>
        </ThemeProvider>
      </AuthProvider>
    </SafeAreaView>
  );
}
