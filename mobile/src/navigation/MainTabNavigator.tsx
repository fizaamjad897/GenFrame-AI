import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Text } from 'react-native';
import CreationEngineScreen from '../screens/CreationEngineScreen';
import TransformationEngineScreen from '../screens/TransformationEngineScreen';
import HistoryScreen from '../screens/HistoryScreen';
import ProfileScreen from '../screens/ProfileScreen';
import { MainTabParamList } from './types';

const Tab = createBottomTabNavigator<MainTabParamList>();

const ICONS: Record<keyof MainTabParamList, string> = {
  Creation: '✨',
  Transformation: '🔄',
  History: '🕘',
  Profile: '👤',
};

export default function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerTitleAlign: 'left',
        tabBarActiveTintColor: 'rgba(3, 105, 161, 1)',
        tabBarIcon: () => <Text style={{ fontSize: 18 }}>{ICONS[route.name]}</Text>,
      })}
    >
      <Tab.Screen name="Creation" component={CreationEngineScreen} options={{ title: 'Creation Engine' }} />
      <Tab.Screen
        name="Transformation"
        component={TransformationEngineScreen}
        options={{ title: 'Transformation Engine' }}
      />
      <Tab.Screen name="History" component={HistoryScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}
