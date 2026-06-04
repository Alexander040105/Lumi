import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Text } from 'react-native';
import { useTheme } from '@/hooks/useTheme';
import HomeScreen from '@/screens/HomeScreen';
import DashboardScreen from '@/screens/DashboardScreen';
import EcosimInputScreen from '@/screens/EcosimInputScreen';
import AdvancedEcosimScreen from '@/screens/AdvancedEcosimScreen';

export type MainTabsParamList = {
  Home: undefined;
  Dashboard: undefined;
  Ecosim: undefined;
  Advanced: undefined;
};

const Tabs = createBottomTabNavigator<MainTabsParamList>();

export default function MainTabs() {
  const { colors } = useTheme();
  return (
    <Tabs.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: colors.card,
          borderTopColor: colors.border,
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.mutedForeground,
      }}
    >
      <Tabs.Screen
        name="Home"
        component={HomeScreen}
        options={{
          tabBarIcon: () => <Text>🏠</Text>,
          tabBarLabel: 'Home',
        }}
      />
      <Tabs.Screen
        name="Ecosim"
        component={EcosimInputScreen}
        options={{
          tabBarIcon: () => <Text>⚡</Text>,
          tabBarLabel: 'Ecosim',
        }}
      />
      <Tabs.Screen
        name="Advanced"
        component={AdvancedEcosimScreen}
        options={{
          tabBarIcon: () => <Text>🧠</Text>,
          tabBarLabel: 'Advanced',
        }}
      />
      <Tabs.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          tabBarIcon: () => <Text>📊</Text>,
          tabBarLabel: 'Dashboard',
        }}
      />
    </Tabs.Navigator>
  );
}
