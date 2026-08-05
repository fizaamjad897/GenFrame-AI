import React, { useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import AspectRatioPicker from '../components/AspectRatioPicker';
import { useAuth } from '../context/AuthContext';
import { resizeImage } from '../api/engine';
import { extractErrorMessage } from '../api/client';
import { EngineType } from '../types/models';
import { getRemainingCredits, hasEngineActiveSubscription, isEngineAllocated } from '../utils/credits';
import { RootStackParamList } from '../navigation/types';

type Nav = NativeStackNavigationProp<RootStackParamList>;

export default function EngineScreen({ engineType }: { engineType: EngineType }) {
  const navigation = useNavigation<Nav>();
  const { user, refreshUser } = useAuth();
  const [aspectRatio, setAspectRatio] = useState('1:1');
  const [prompt, setPrompt] = useState('');
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const isCreation = engineType === 'creation';

  const pickImage = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission needed', 'Allow photo library access to pick an image.');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 0.9,
    });
    if (!result.canceled && result.assets[0]) {
      setImageUri(result.assets[0].uri);
    }
  };

  const canSubmit = isCreation
    ? Boolean(prompt.trim()) || Boolean(imageUri)
    : Boolean(imageUri);

  const onSubmit = async () => {
    if (!canSubmit || submitting) return;
    setSubmitting(true);
    try {
      const result = await resizeImage({ engineType, aspectRatio, prompt, imageUri });
      await refreshUser();
      setImageUri(null);
      setPrompt('');
      navigation.navigate('Result', { result });
    } catch (err) {
      Alert.alert('Generation failed', extractErrorMessage(err, 'Something went wrong.'));
    } finally {
      setSubmitting(false);
    }
  };

  if (!user) return null;

  if (!isEngineAllocated(user, engineType)) {
    return (
      <View style={styles.centered}>
        <Text style={styles.blockedTitle}>Engine not available</Text>
        <Text style={styles.blockedSubtitle}>
          This engine isn't enabled for your account yet.
        </Text>
      </View>
    );
  }

  const isPostpaid = Boolean(user.is_postpaid);
  const hasSubscription = hasEngineActiveSubscription(user, engineType);
  const remaining = getRemainingCredits(user, engineType);

  if (!isPostpaid && !hasSubscription) {
    return (
      <View style={styles.centered}>
        <Text style={styles.blockedTitle}>Subscription required</Text>
        <Text style={styles.blockedSubtitle}>
          Choose a plan to activate credits for the {isCreation ? 'Creation' : 'Transformation'}{' '}
          engine.
        </Text>
      </View>
    );
  }

  if (!isPostpaid && remaining <= 0) {
    return (
      <View style={styles.centered}>
        <Text style={styles.blockedTitle}>No credits available</Text>
        <Text style={styles.blockedSubtitle}>
          Your {isCreation ? 'Creation' : 'Transformation'} engine has 0 remaining credits.
        </Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
      <Text style={styles.heading}>{isCreation ? 'Creation Engine' : 'Transformation Engine'}</Text>
      {!isPostpaid && <Text style={styles.credits}>{remaining} credits remaining</Text>}

      <TouchableOpacity style={styles.uploadBox} onPress={pickImage}>
        {imageUri ? (
          <Image source={{ uri: imageUri }} style={styles.previewImage} resizeMode="cover" />
        ) : (
          <Text style={styles.uploadText}>
            {isCreation ? 'Add a reference image (optional)' : 'Tap to select an image'}
          </Text>
        )}
      </TouchableOpacity>
      {imageUri && (
        <TouchableOpacity onPress={() => setImageUri(null)}>
          <Text style={styles.removeLink}>Remove image</Text>
        </TouchableOpacity>
      )}

      {isCreation && (
        <>
          <Text style={styles.label}>Prompt</Text>
          <TextInput
            style={styles.promptInput}
            placeholder="Describe the image you want to create..."
            value={prompt}
            onChangeText={setPrompt}
            multiline
          />
        </>
      )}

      <Text style={styles.label}>Aspect ratio</Text>
      <AspectRatioPicker value={aspectRatio} onChange={setAspectRatio} />

      <TouchableOpacity
        style={[styles.submitButton, !canSubmit && styles.submitButtonDisabled]}
        onPress={onSubmit}
        disabled={!canSubmit || submitting}
      >
        {submitting ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.submitButtonText}>Generate</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f9fafb' },
  heading: { fontSize: 20, fontWeight: '700', color: '#111827', marginBottom: 4 },
  credits: { fontSize: 13, color: '#6b7280', marginBottom: 16 },
  uploadBox: {
    height: 200,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: 'rgba(3, 105, 161, 0.25)',
    borderStyle: 'dashed',
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
    overflow: 'hidden',
  },
  uploadText: { color: '#6b7280', fontSize: 14, paddingHorizontal: 20, textAlign: 'center' },
  previewImage: { width: '100%', height: '100%' },
  removeLink: { color: '#dc2626', fontSize: 13, marginTop: 8, textAlign: 'right' },
  label: { fontSize: 13, fontWeight: '600', color: '#111827', marginTop: 20, marginBottom: 8 },
  promptInput: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 10,
    padding: 12,
    fontSize: 14,
    minHeight: 90,
    textAlignVertical: 'top',
  },
  submitButton: {
    backgroundColor: 'rgba(3, 105, 161, 1)',
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 28,
  },
  submitButtonDisabled: { opacity: 0.4 },
  submitButtonText: { color: '#fff', fontWeight: '600', fontSize: 15 },
  centered: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32 },
  blockedTitle: { fontSize: 18, fontWeight: '700', color: '#111827', marginBottom: 8 },
  blockedSubtitle: { fontSize: 14, color: '#6b7280', textAlign: 'center', lineHeight: 20 },
});
