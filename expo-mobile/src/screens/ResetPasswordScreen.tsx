import { useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/hooks/useTheme';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Toast from 'react-native-toast-message';

export default function ResetPasswordScreen() {
  const { session, updatePassword } = useAuth();
  const { colors } = useTheme();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [busy, setBusy] = useState(false);

  const handleSubmit = async () => {
    if (password !== confirmPassword) {
      Toast.show({ type: 'error', text1: 'Passwords do not match' });
      return;
    }
    if (password.length < 6) {
      Toast.show({ type: 'error', text1: 'Password must be at least 6 characters' });
      return;
    }

    setBusy(true);
    try {
      const { error } = await updatePassword(password);
      if (error) throw error;
      Toast.show({
        type: 'success',
        text1: 'Password updated. You can sign in again.',
      });
    } catch (error: any) {
      Toast.show({
        type: 'error',
        text1: error?.message || 'Password update failed',
      });
    } finally {
      setBusy(false);
    }
  };

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: colors.background }]}
      contentContainerStyle={styles.content}
    >
      <Card>
        <Text style={[styles.title, { color: colors.foreground }]}>
          Reset your password
        </Text>
        <Text style={[styles.desc, { color: colors.mutedForeground }]}>
          Set a new password after confirming your email.
        </Text>

        {!session && (
          <Text style={[styles.hint, { color: colors.mutedForeground }]}>
            Open this page from the reset link in your email.
          </Text>
        )}

        <View style={styles.form}>
          <Input
            placeholder="New password"
            secureTextEntry
            value={password}
            onChangeText={setPassword}
            textContentType="newPassword"
          />
          <Input
            placeholder="Confirm new password"
            secureTextEntry
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            textContentType="newPassword"
          />
          <Button
            title="Update password"
            onPress={handleSubmit}
            disabled={busy || !session}
          />
        </View>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 4,
  },
  desc: {
    fontSize: 13,
    marginBottom: 16,
  },
  hint: {
    fontSize: 12,
    marginBottom: 12,
  },
  form: {
    gap: 10,
  },
});
