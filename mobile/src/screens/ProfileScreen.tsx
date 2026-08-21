import React from 'react';
import { Alert, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { getRemainingCredits } from '../utils/credits';

export default function ProfileScreen() {
  const { user, logout } = useAuth();

  if (!user) return null;

  const confirmLogout = () => {
    Alert.alert('Sign out', 'Are you sure you want to sign out?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Sign out', style: 'destructive', onPress: logout },
    ]);
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.name}>{user.fullName || user.email}</Text>
        <Text style={styles.email}>{user.email}</Text>
        <Text style={styles.plan}>Plan: {user.plan || 'None'}</Text>
        {!user.is_postpaid && (
          <>
            <Text style={styles.row}>
              Creation credits: {getRemainingCredits(user, 'creation')}
            </Text>
            <Text style={styles.row}>
              Transformation credits: {getRemainingCredits(user, 'transformation')}
            </Text>
          </>
        )}
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={confirmLogout}>
        <Text style={styles.logoutText}>Sign out</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb', padding: 16 },
  card: {
    backgroundColor: '#fff',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    padding: 20,
  },
  name: { fontSize: 18, fontWeight: '700', color: '#111827' },
  email: { fontSize: 13, color: '#6b7280', marginTop: 2, marginBottom: 12 },
  plan: { fontSize: 14, color: '#111827', marginBottom: 6, fontWeight: '600' },
  row: { fontSize: 13, color: '#374151', marginTop: 4 },
  logoutButton: {
    marginTop: 24,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#dc2626',
  },
  logoutText: { color: '#dc2626', fontWeight: '600', fontSize: 15 },
});
